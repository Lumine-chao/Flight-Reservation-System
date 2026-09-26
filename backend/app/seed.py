"""启动时自举：建表（幂等）+ 基础数据初始化（城市、航班、管理员、演示账号）。"""
import hashlib
import logging

from sqlalchemy import text

from sql.cities_data import PROVINCE_CITIES
from sql.flights_fill import FILL_FLIGHTS
from sql.pricing import haversine_km, price_business, price_economy, price_first

from .database import SessionLocal, engine
from .models import AdminUser, City, Flight, User
from .security import hash_password

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS `user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(16) NOT NULL,
  `password_hash` VARCHAR(100) NOT NULL,
  `security_question` VARCHAR(64) NOT NULL,
  `security_answer_hash` VARCHAR(100) NOT NULL,
  `status` TINYINT NOT NULL DEFAULT 1,
  `locked_until` DATETIME NULL,
  `fail_count` INT NOT NULL DEFAULT 0,
  `token_version` INT NOT NULL DEFAULT 0,
  `last_login_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `city` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `city_code` VARCHAR(64) NOT NULL,
  `city_name` VARCHAR(64) NOT NULL,
  `province` VARCHAR(64) NOT NULL DEFAULT '',
  `status` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_city_code` (`city_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `flight` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `flight_no` VARCHAR(32) NOT NULL,
  `from_city_id` BIGINT NOT NULL,
  `to_city_id` BIGINT NOT NULL,
  `depart_time` VARCHAR(8) NOT NULL,
  `arrive_time` VARCHAR(8) NOT NULL,
  `airline` VARCHAR(64) NOT NULL,
  `price_economy` DECIMAL(10,2) NOT NULL,
  `price_business` DECIMAL(10,2) NOT NULL,
  `price_first` DECIMAL(10,2) NOT NULL,
  `seat_remain` INT NOT NULL DEFAULT 100,
  `status` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_flight_no` (`flight_no`),
  KEY `idx_route` (`from_city_id`, `to_city_id`),
  CONSTRAINT `fk_flight_from` FOREIGN KEY (`from_city_id`) REFERENCES `city` (`id`),
  CONSTRAINT `fk_flight_to` FOREIGN KEY (`to_city_id`) REFERENCES `city` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `orders` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `order_no` VARCHAR(32) NOT NULL,
  `user_id` BIGINT NOT NULL,
  `flight_id` BIGINT NOT NULL,
  `flight_date` DATE NOT NULL,
  `passenger_name` VARCHAR(64) NOT NULL,
  `from_city_id` BIGINT NOT NULL,
  `to_city_id` BIGINT NOT NULL,
  `ticket_count` INT NOT NULL DEFAULT 1,
  `seat_class` VARCHAR(16) NOT NULL DEFAULT 'ECONOMY',
  `unit_price` DECIMAL(10,2) NOT NULL,
  `total_price` DECIMAL(10,2) NOT NULL,
  `status` VARCHAR(16) NOT NULL DEFAULT 'TICKETED',
  `version` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_status` (`user_id`, `status`, `created_at`),
  KEY `idx_passenger_name` (`passenger_name`),
  KEY `idx_flight_date` (`flight_date`),
  KEY `idx_status_date` (`status`, `flight_date`),
  CONSTRAINT `fk_order_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_order_flight` FOREIGN KEY (`flight_id`) REFERENCES `flight` (`id`),
  CONSTRAINT `fk_order_from` FOREIGN KEY (`from_city_id`) REFERENCES `city` (`id`),
  CONSTRAINT `fk_order_to` FOREIGN KEY (`to_city_id`) REFERENCES `city` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `order_status_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `order_id` BIGINT NOT NULL,
  `from_status` VARCHAR(16) NULL,
  `to_status` VARCHAR(16) NOT NULL,
  `action` VARCHAR(32) NOT NULL,
  `operator_type` VARCHAR(16) NOT NULL,
  `operator_id` BIGINT NULL,
  `operate_time` DATETIME NOT NULL,
  `remark` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  KEY `idx_order` (`order_id`),
  CONSTRAINT `fk_log_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `admin_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(32) NOT NULL,
  `password_hash` VARCHAR(100) NOT NULL,
  `role` VARCHAR(16) NOT NULL DEFAULT 'ADMIN',
  `status` TINYINT NOT NULL DEFAULT 1,
  `last_login_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `app_meta` (
  `k` VARCHAR(32) NOT NULL,
  `v` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

# 城市种子：由 sql/cities_data.py 提供（225 城、34 省级行政区）
SEED_CITIES = sorted(
    ((code, meta[1], meta[0]) for code, meta in PROVINCE_CITIES.items()),
    key=lambda x: (x[2], x[0]),
)

# 航班种子（省份 -> 航线列表）。航线：省份/直辖市 + 主要城市，覆盖全部 34 个省级行政区。
# (出发代码, 到达代码, 起飞, 到达, 航司, 余票)；三舱价格播种时按距离计算（见 sql/pricing.py）
SEED_FLIGHTS_BY_PROVINCE = {
    "北京": [
        ("beijing", "shanghai", "08:00", "10:15", "中国国际航空", 120),
        ("beijing", "guangzhou", "09:20", "12:40", "中国国际航空", 110),
        ("beijing", "shenzhen", "12:30", "15:50", "中国国际航空", 100),
        ("beijing", "chengdu", "07:40", "10:50", "中国国际航空", 110),
        ("beijing", "chongqing", "09:00", "11:55", "中国国际航空", 120),
        ("beijing", "xian", "10:10", "12:25", "中国国际航空", 130),
        ("beijing", "kunming", "08:30", "12:05", "中国东方航空", 100),
        ("beijing", "haerbin", "11:20", "13:25", "中国国际航空", 115),
        ("beijing", "urumqi", "12:10", "16:05", "海南航空", 110),
        ("beijing", "lasa", "07:50", "11:20", "中国国际航空", 80),
        ("beijing", "hangzhou", "10:10", "12:20", "中国国际航空", 120),
        ("beijing", "nanjing", "13:10", "15:20", "中国国际航空", 105),
        ("beijing", "wuhan", "14:00", "16:10", "中国东方航空", 110),
        ("beijing", "changsha", "15:30", "18:00", "中国南方航空", 100),
        ("beijing", "zhengzhou", "16:40", "18:20", "中国南方航空", 120),
        ("beijing", "jinan", "17:30", "19:00", "中国东方航空", 115),
        ("beijing", "huhehaote", "09:50", "11:30", "中国国际航空", 110),
        ("beijing", "shijiazhuang", "12:40", "13:30", "中国南方航空", 130),
        ("beijing", "taiyuan", "14:20", "15:40", "中国东方航空", 120),
        ("beijing", "shenyang", "11:00", "12:40", "中国南方航空", 115),
        ("beijing", "dalian", "17:20", "19:05", "中国国际航空", 100),
        ("beijing", "changchun", "13:50", "15:50", "中国南方航空", 110),
        ("beijing", "xining", "10:30", "13:20", "中国东方航空", 100),
        ("beijing", "yinchuan", "15:00", "17:20", "中国国际航空", 105),
        ("beijing", "guiyang", "08:10", "11:35", "中国南方航空", 100),
        ("beijing", "nanning", "13:00", "16:25", "中国南方航空", 95),
        ("beijing", "haikou", "09:30", "13:20", "海南航空", 110),
        ("beijing", "fuzhou", "11:50", "14:40", "厦门航空", 100),
        ("beijing", "nanchang", "14:30", "16:50", "中国东方航空", 105),
    ],
    "上海": [
        ("shanghai", "beijing", "09:30", "11:45", "中国东方航空", 100),
        ("shanghai", "guangzhou", "10:20", "12:55", "中国东方航空", 120),
        ("shanghai", "shenzhen", "13:10", "15:50", "中国南方航空", 115),
        ("shanghai", "chengdu", "08:50", "11:40", "中国东方航空", 105),
        ("shanghai", "chongqing", "12:20", "15:10", "中国东方航空", 110),
        ("shanghai", "xian", "14:40", "17:10", "中国东方航空", 120),
        ("shanghai", "kunming", "09:10", "12:45", "中国东方航空", 100),
        ("shanghai", "hangzhou", "11:00", "12:10", "中国东方航空", 130),
        ("shanghai", "nanjing", "15:20", "16:40", "中国东方航空", 125),
        ("shanghai", "wuhan", "07:20", "09:05", "中国东方航空", 140),
        ("shanghai", "hefei", "13:40", "15:00", "中国东方航空", 130),
        ("shanghai", "qingdao", "16:40", "18:15", "中国东方航空", 125),
        ("shanghai", "xiamen", "17:30", "19:15", "海南航空", 120),
        ("shanghai", "tianjin", "14:50", "17:00", "中国东方航空", 105),
        ("shanghai", "dalian", "10:40", "12:30", "中国东方航空", 115),
        ("shanghai", "sanya", "08:20", "11:40", "中国东方航空", 110),
        ("shanghai", "changsha", "16:10", "18:15", "中国南方航空", 120),
        ("shanghai", "zhengzhou", "12:50", "14:40", "中国南方航空", 125),
        ("shanghai", "guilin", "10:10", "12:40", "中国南方航空", 110),
    ],
    "广东": [
        ("guangzhou", "shenzhen", "10:00", "11:05", "中国南方航空", 150),
        ("shenzhen", "guangzhou", "13:20", "14:25", "深圳航空", 90),
        ("guangzhou", "beijing", "11:30", "14:50", "中国南方航空", 110),
        ("shenzhen", "beijing", "17:10", "20:30", "中国南方航空", 96),
        ("guangzhou", "shanghai", "15:00", "17:25", "中国南方航空", 120),
        ("shenzhen", "shanghai", "09:00", "11:20", "深圳航空", 115),
        ("guangzhou", "chengdu", "13:40", "16:25", "中国南方航空", 110),
        ("shenzhen", "chengdu", "16:30", "19:15", "深圳航空", 105),
        ("guangzhou", "kunming", "09:10", "11:40", "中国南方航空", 120),
        ("shenzhen", "xian", "14:10", "16:50", "中国东方航空", 100),
        ("guangzhou", "changsha", "15:30", "16:55", "中国南方航空", 130),
        ("shenzhen", "changsha", "19:30", "20:55", "深圳航空", 120),
        ("guangzhou", "wuhan", "11:50", "13:40", "中国南方航空", 135),
        ("guangzhou", "nanning", "17:20", "18:40", "中国南方航空", 130),
        ("guangzhou", "haikou", "09:50", "11:10", "海南航空", 130),
        ("shenzhen", "haikou", "14:30", "15:50", "深圳航空", 125),
        ("shenzhen", "sanya", "16:10", "17:45", "海南航空", 110),
        ("guangzhou", "xiamen", "12:20", "13:40", "厦门航空", 125),
        ("shenzhen", "fuzhou", "15:00", "16:20", "深圳航空", 120),
        ("guangzhou", "nanchang", "10:40", "12:15", "中国南方航空", 130),
        ("guangzhou", "guilin", "13:00", "14:10", "中国南方航空", 140),
        ("guangzhou", "guiyang", "16:40", "18:20", "中国南方航空", 120),
        ("guangzhou", "changchun", "08:10", "12:20", "中国南方航空", 95),
        ("shenzhen", "haerbin", "12:30", "16:45", "深圳航空", 90),
        ("shenzhen", "lanzhou", "11:40", "15:10", "深圳航空", 100),
        ("guangzhou", "yinchuan", "14:50", "18:20", "中国南方航空", 95),
        ("shenzhen", "xining", "10:20", "14:00", "深圳航空", 90),
        ("guangzhou", "taiyuan", "13:20", "16:10", "中国南方航空", 100),
        ("shenzhen", "shijiazhuang", "15:40", "18:30", "深圳航空", 105),
        ("guangzhou", "huhehaote", "17:50", "21:10", "中国南方航空", 95),
    ],
    "四川": [
        ("chengdu", "beijing", "16:30", "19:40", "四川航空", 95),
        ("chengdu", "shanghai", "15:20", "18:05", "四川航空", 88),
        ("chengdu", "chongqing", "08:40", "09:40", "四川航空", 140),
        ("chengdu", "xian", "12:10", "13:40", "四川航空", 130),
        ("chengdu", "kunming", "07:30", "09:05", "四川航空", 140),
        ("chengdu", "guiyang", "14:20", "15:40", "四川航空", 135),
        ("chengdu", "xiamen", "13:30", "16:35", "四川航空", 105),
        ("chengdu", "wuhan", "10:50", "12:50", "四川航空", 120),
        ("chengdu", "changsha", "16:00", "17:50", "四川航空", 115),
        ("chengdu", "lanzhou", "11:20", "13:00", "四川航空", 120),
        ("chengdu", "nanning", "15:10", "17:30", "四川航空", 110),
        ("chengdu", "haikou", "09:40", "12:30", "四川航空", 110),
    ],
    "重庆": [
        ("chongqing", "beijing", "14:30", "17:25", "四川航空", 95),
        ("chongqing", "shanghai", "09:20", "11:40", "中国东方航空", 105),
        ("chongqing", "guangzhou", "13:10", "15:20", "中国南方航空", 115),
        ("chongqing", "shenzhen", "17:00", "19:10", "深圳航空", 110),
        ("chongqing", "xian", "08:10", "09:30", "中国东方航空", 130),
        ("chongqing", "kunming", "11:50", "13:20", "中国东方航空", 125),
        ("chongqing", "wuhan", "15:40", "17:10", "中国南方航空", 135),
    ],
    "陕西": [
        ("xian", "beijing", "11:00", "13:15", "中国东方航空", 120),
        ("xian", "shanghai", "08:30", "10:55", "中国东方航空", 130),
        ("xian", "guangzhou", "13:50", "16:30", "中国南方航空", 120),
        ("xian", "shenzhen", "16:20", "18:50", "深圳航空", 115),
        ("xian", "chengdu", "10:20", "12:00", "四川航空", 130),
        ("xian", "chongqing", "14:40", "16:05", "中国东方航空", 125),
        ("xian", "hangzhou", "17:30", "19:50", "中国东方航空", 120),
        ("xian", "wuhan", "18:30", "20:10", "中国国际航空", 115),
        ("xian", "yinchuan", "12:40", "14:05", "中国东方航空", 130),
        ("xian", "lanzhou", "15:20", "16:45", "中国东方航空", 135),
        ("xian", "urumqi", "09:00", "12:30", "中国东方航空", 110),
    ],
    "湖北": [
        ("wuhan", "beijing", "10:30", "12:40", "中国东方航空", 110),
        ("wuhan", "shanghai", "12:40", "14:25", "中国南方航空", 110),
        ("wuhan", "guangzhou", "08:50", "10:40", "中国南方航空", 135),
        ("wuhan", "shenzhen", "14:30", "16:20", "深圳航空", 125),
        ("wuhan", "chengdu", "11:20", "13:20", "四川航空", 120),
        ("wuhan", "chongqing", "16:50", "18:20", "中国南方航空", 130),
        ("wuhan", "xian", "15:00", "16:40", "中国南方航空", 135),
        ("wuhan", "changsha", "17:30", "18:40", "中国南方航空", 140),
        ("wuhan", "nanchang", "13:10", "14:30", "中国东方航空", 135),
    ],
    "湖南": [
        ("changsha", "beijing", "09:00", "11:30", "中国南方航空", 100),
        ("changsha", "shanghai", "13:30", "15:35", "中国东方航空", 120),
        ("changsha", "guangzhou", "10:40", "12:05", "中国南方航空", 130),
        ("changsha", "shenzhen", "15:20", "16:45", "深圳航空", 120),
        ("changsha", "chengdu", "12:50", "14:50", "四川航空", 115),
        ("changsha", "kunming", "17:40", "19:40", "中国东方航空", 120),
        ("changsha", "xian", "14:10", "15:50", "中国东方航空", 125),
    ],
    "浙江": [
        ("hangzhou", "beijing", "08:10", "10:20", "中国国际航空", 120),
        ("hangzhou", "shanghai", "11:00", "12:10", "中国东方航空", 130),
        ("hangzhou", "guangzhou", "13:40", "16:00", "中国南方航空", 125),
        ("hangzhou", "shenzhen", "16:20", "18:40", "深圳航空", 120),
        ("hangzhou", "chengdu", "10:30", "13:30", "四川航空", 115),
        ("hangzhou", "xian", "14:50", "17:10", "中国东方航空", 125),
        ("hangzhou", "xiamen", "17:10", "18:50", "厦门航空", 125),
    ],
    "江苏": [
        ("nanjing", "beijing", "08:30", "10:40", "中国东方航空", 115),
        ("nanjing", "shanghai", "12:30", "13:50", "中国东方航空", 130),
        ("nanjing", "guangzhou", "14:10", "16:30", "中国南方航空", 125),
        ("nanjing", "shenzhen", "17:00", "19:20", "深圳航空", 120),
        ("nanjing", "chengdu", "13:50", "16:35", "中国东方航空", 105),
        ("nanjing", "xian", "15:30", "17:30", "中国东方航空", 125),
        ("nanjing", "qingdao", "18:20", "19:40", "中国东方航空", 130),
    ],
    "山东": [
        ("jinan", "beijing", "09:40", "11:10", "中国东方航空", 115),
        ("jinan", "shanghai", "13:20", "15:00", "中国东方航空", 125),
        ("qingdao", "beijing", "10:20", "11:55", "山东航空", 135),
        ("qingdao", "shanghai", "16:40", "18:15", "中国东方航空", 125),
        ("jinan", "guangzhou", "14:00", "16:40", "中国南方航空", 110),
        ("qingdao", "chengdu", "12:30", "15:30", "四川航空", 110),
        ("jinan", "xian", "17:20", "19:10", "中国东方航空", 120),
        ("qingdao", "shenzhen", "09:10", "12:10", "深圳航空", 105),
    ],
    "河南": [
        ("zhengzhou", "beijing", "08:20", "10:00", "中国南方航空", 120),
        ("zhengzhou", "shanghai", "12:50", "14:40", "中国南方航空", 125),
        ("zhengzhou", "guangzhou", "14:30", "16:40", "中国南方航空", 120),
        ("zhengzhou", "shenzhen", "11:30", "14:05", "中国南方航空", 115),
        ("zhengzhou", "chengdu", "16:40", "18:50", "四川航空", 120),
        ("zhengzhou", "xian", "18:10", "19:20", "中国东方航空", 130),
        ("zhengzhou", "kunming", "09:50", "12:30", "中国东方航空", 110),
    ],
    "福建": [
        ("fuzhou", "beijing", "11:50", "14:40", "厦门航空", 100),
        ("fuzhou", "shanghai", "14:10", "15:50", "厦门航空", 125),
        ("xiamen", "beijing", "09:00", "12:10", "厦门航空", 105),
        ("xiamen", "shanghai", "11:10", "12:55", "厦门航空", 130),
        ("xiamen", "chengdu", "08:10", "11:15", "厦门航空", 120),
        ("xiamen", "guangzhou", "12:20", "13:40", "厦门航空", 125),
        ("fuzhou", "shenzhen", "16:30", "17:55", "深圳航空", 120),
        ("xiamen", "kunming", "13:50", "16:50", "厦门航空", 110),
    ],
    "天津": [
        ("tianjin", "shanghai", "09:40", "11:50", "天津航空", 120),
        ("tianjin", "guangzhou", "13:10", "16:00", "天津航空", 110),
        ("tianjin", "chengdu", "16:20", "19:20", "天津航空", 105),
        ("tianjin", "xian", "11:30", "13:30", "天津航空", 125),
    ],
    "河北": [
        ("shijiazhuang", "beijing", "12:40", "13:30", "中国南方航空", 130),
        ("shijiazhuang", "guangzhou", "15:40", "18:30", "中国南方航空", 105),
        ("shijiazhuang", "shanghai", "09:50", "11:50", "中国东方航空", 125),
        ("shijiazhuang", "chengdu", "17:10", "19:50", "四川航空", 115),
        ("tangshan", "shanghai", "10:30", "12:30", "中国东方航空", 120),
        ("qinhuangdao", "beijing", "08:50", "10:00", "中国国际航空", 125),
    ],
    "山西": [
        ("taiyuan", "beijing", "14:20", "15:40", "中国东方航空", 120),
        ("taiyuan", "shanghai", "10:10", "12:20", "中国东方航空", 120),
        ("taiyuan", "guangzhou", "13:20", "16:10", "中国南方航空", 100),
        ("taiyuan", "chengdu", "16:40", "18:50", "四川航空", 115),
        ("taiyuan", "xian", "11:50", "13:20", "中国东方航空", 130),
        ("datong", "shanghai", "15:00", "17:10", "中国东方航空", 115),
    ],
    "内蒙古": [
        ("huhehaote", "beijing", "09:50", "11:30", "中国国际航空", 110),
        ("huhehaote", "shanghai", "13:20", "15:50", "中国东方航空", 110),
        ("huhehaote", "guangzhou", "17:50", "21:10", "中国南方航空", 95),
        ("baotou", "beijing", "11:00", "12:30", "中国国际航空", 115),
        ("baotou", "shanghai", "14:40", "17:10", "中国东方航空", 105),
        ("eerduosi", "beijing", "16:20", "17:50", "中国国际航空", 110),
        ("chifeng", "beijing", "09:10", "10:30", "中国国际航空", 115),
    ],
    "辽宁": [
        ("shenyang", "beijing", "11:00", "12:40", "中国南方航空", 115),
        ("shenyang", "shanghai", "14:30", "16:50", "中国东方航空", 115),
        ("shenyang", "guangzhou", "09:20", "13:10", "中国南方航空", 100),
        ("shenyang", "chengdu", "17:10", "20:40", "四川航空", 105),
        ("shenyang", "xian", "12:40", "15:20", "中国东方航空", 115),
        ("dalian", "beijing", "17:20", "19:05", "中国国际航空", 100),
        ("dalian", "shanghai", "10:40", "12:30", "中国东方航空", 115),
        ("dalian", "guangzhou", "13:50", "17:40", "中国南方航空", 100),
        ("dalian", "chengdu", "08:30", "12:00", "四川航空", 105),
    ],
    "吉林": [
        ("changchun", "beijing", "13:50", "15:50", "中国南方航空", 110),
        ("changchun", "shanghai", "10:00", "12:40", "中国东方航空", 110),
        ("changchun", "guangzhou", "08:10", "12:20", "中国南方航空", 95),
        ("changchun", "chengdu", "15:40", "19:30", "四川航空", 100),
    ],
    "黑龙江": [
        ("haerbin", "beijing", "11:20", "13:25", "中国国际航空", 115),
        ("haerbin", "shanghai", "09:40", "12:30", "中国东方航空", 110),
        ("haerbin", "guangzhou", "13:10", "17:30", "中国南方航空", 95),
        ("haerbin", "shenzhen", "12:30", "16:45", "深圳航空", 90),
        ("haerbin", "chengdu", "15:50", "19:50", "四川航空", 100),
        ("haerbin", "xian", "10:50", "14:00", "中国东方航空", 110),
        ("qiqihaer", "beijing", "09:20", "11:30", "中国国际航空", 110),
        ("daqing", "beijing", "14:00", "16:10", "中国南方航空", 110),
        ("mudanjiang", "shanghai", "11:30", "14:20", "中国东方航空", 105),
        ("jiamusi", "beijing", "13:40", "16:00", "中国国际航空", 105),
    ],
    "安徽": [
        ("hefei", "shanghai", "13:40", "15:00", "中国东方航空", 130),
        ("hefei", "beijing", "09:10", "11:10", "中国东方航空", 120),
        ("hefei", "guangzhou", "15:20", "17:30", "中国南方航空", 115),
        ("hefei", "shenzhen", "10:30", "12:50", "深圳航空", 115),
        ("hefei", "chengdu", "17:40", "20:00", "四川航空", 110),
        ("hefei", "xian", "12:20", "14:10", "中国东方航空", 125),
        ("huangshan", "shanghai", "09:50", "11:20", "中国东方航空", 130),
        ("huangshan", "guangzhou", "14:10", "15:50", "中国南方航空", 120),
    ],
    "江西": [
        ("nanchang", "beijing", "14:30", "16:50", "中国东方航空", 105),
        ("nanchang", "shanghai", "10:10", "11:50", "中国东方航空", 130),
        ("nanchang", "guangzhou", "10:40", "12:15", "中国南方航空", 130),
        ("nanchang", "shenzhen", "15:20", "16:55", "深圳航空", 125),
        ("nanchang", "chengdu", "17:10", "19:20", "四川航空", 115),
        ("nanchang", "xian", "12:50", "14:40", "中国东方航空", 120),
        ("jingdezhen", "beijing", "09:30", "11:40", "中国国际航空", 115),
        ("ganzhou", "shanghai", "13:20", "15:10", "中国东方航空", 120),
    ],
    "广西": [
        ("nanning", "beijing", "13:00", "16:25", "中国南方航空", 95),
        ("nanning", "shanghai", "09:10", "11:50", "中国东方航空", 110),
        ("nanning", "guangzhou", "17:20", "18:40", "中国南方航空", 130),
        ("nanning", "chengdu", "11:20", "13:30", "四川航空", 115),
        ("guilin", "beijing", "10:30", "13:20", "中国南方航空", 110),
        ("guilin", "shanghai", "10:10", "12:40", "中国南方航空", 110),
        ("guilin", "guangzhou", "13:00", "14:10", "中国南方航空", 140),
        ("guilin", "shenzhen", "16:00", "17:10", "深圳航空", 135),
        ("liuzhou", "shanghai", "14:40", "17:10", "中国东方航空", 115),
    ],
    "贵州": [
        ("guiyang", "beijing", "08:10", "11:35", "中国南方航空", 100),
        ("guiyang", "shanghai", "12:50", "15:20", "中国东方航空", 110),
        ("guiyang", "guangzhou", "16:40", "18:20", "中国南方航空", 120),
        ("guiyang", "shenzhen", "10:20", "12:00", "深圳航空", 115),
        ("guiyang", "chengdu", "14:20", "15:40", "四川航空", 135),
        ("guiyang", "xian", "17:50", "19:50", "中国东方航空", 115),
        ("zunyi", "shanghai", "09:40", "12:10", "中国东方航空", 110),
        ("zunyi", "beijing", "13:20", "16:20", "中国南方航空", 105),
    ],
    "云南": [
        ("kunming", "beijing", "08:30", "12:05", "中国东方航空", 100),
        ("kunming", "shanghai", "10:20", "13:20", "中国东方航空", 105),
        ("kunming", "guangzhou", "13:10", "15:10", "中国南方航空", 120),
        ("kunming", "shenzhen", "16:20", "18:20", "深圳航空", 115),
        ("kunming", "chengdu", "07:30", "09:05", "四川航空", 140),
        ("kunming", "xian", "14:00", "16:10", "中国东方航空", 120),
        ("kunming", "changsha", "10:50", "13:15", "中国东方航空", 120),
        ("kunming", "guilin", "17:30", "19:20", "中国东方航空", 125),
        ("lijiang", "shanghai", "11:10", "14:20", "中国东方航空", 110),
        ("lijiang", "guangzhou", "15:00", "17:40", "中国南方航空", 110),
        ("xishuangbanna", "beijing", "13:40", "17:30", "中国东方航空", 90),
        ("xishuangbanna", "shanghai", "09:00", "12:10", "中国东方航空", 95),
        ("dali", "chengdu", "10:40", "12:40", "四川航空", 120),
        ("dali", "shanghai", "14:30", "17:30", "中国东方航空", 105),
    ],
    "海南": [
        ("haikou", "beijing", "09:30", "13:20", "海南航空", 110),
        ("haikou", "shanghai", "13:40", "16:20", "中国东方航空", 115),
        ("haikou", "guangzhou", "09:50", "11:10", "海南航空", 130),
        ("haikou", "shenzhen", "14:30", "15:50", "深圳航空", 125),
        ("sanya", "beijing", "11:00", "15:00", "海南航空", 105),
        ("sanya", "shanghai", "08:20", "11:40", "中国东方航空", 110),
        ("sanya", "guangzhou", "15:40", "17:00", "海南航空", 120),
        ("sanya", "chengdu", "12:30", "15:10", "四川航空", 115),
    ],
    "甘肃": [
        ("lanzhou", "beijing", "10:00", "12:30", "中国东方航空", 110),
        ("lanzhou", "shanghai", "14:10", "16:50", "中国东方航空", 105),
        ("lanzhou", "guangzhou", "13:00", "16:00", "中国南方航空", 100),
        ("lanzhou", "shenzhen", "11:40", "15:10", "深圳航空", 100),
        ("lanzhou", "chengdu", "11:20", "13:00", "四川航空", 120),
        ("lanzhou", "xian", "15:30", "17:00", "中国东方航空", 130),
        ("lanzhou", "urumqi", "09:20", "12:00", "中国东方航空", 110),
        ("jiayuguan", "beijing", "12:30", "15:30", "中国东方航空", 100),
        ("dunhuang", "xian", "10:10", "11:50", "中国东方航空", 115),
    ],
    "青海": [
        ("xining", "beijing", "10:30", "13:20", "中国东方航空", 100),
        ("xining", "shanghai", "14:00", "16:50", "中国东方航空", 100),
        ("xining", "guangzhou", "12:10", "15:00", "中国南方航空", 95),
        ("xining", "chengdu", "16:20", "17:50", "四川航空", 115),
        ("xining", "shenzhen", "10:20", "14:00", "深圳航空", 90),
        ("xining", "xian", "13:30", "15:10", "中国东方航空", 120),
    ],
    "宁夏": [
        ("yinchuan", "beijing", "15:00", "17:20", "中国国际航空", 105),
        ("yinchuan", "shanghai", "09:30", "12:20", "中国东方航空", 105),
        ("yinchuan", "guangzhou", "14:50", "18:20", "中国南方航空", 95),
        ("yinchuan", "chengdu", "11:40", "13:50", "四川航空", 115),
        ("yinchuan", "xian", "12:40", "14:05", "中国东方航空", 130),
        ("yinchuan", "urumqi", "17:10", "19:50", "中国东方航空", 105),
    ],
    "新疆": [
        ("urumqi", "beijing", "12:10", "16:05", "海南航空", 110),
        ("urumqi", "shanghai", "09:00", "13:10", "中国东方航空", 105),
        ("urumqi", "guangzhou", "08:30", "13:20", "中国南方航空", 100),
        ("urumqi", "chengdu", "14:20", "17:50", "四川航空", 105),
        ("urumqi", "xian", "09:00", "12:30", "中国东方航空", 110),
        ("urumqi", "kunming", "11:30", "15:50", "中国东方航空", 95),
        ("kashi", "urumqi", "10:20", "12:40", "中国南方航空", 110),
        ("kashi", "beijing", "13:00", "17:50", "中国南方航空", 90),
        ("akesu", "urumqi", "15:10", "16:40", "中国南方航空", 120),
        ("hami", "beijing", "09:50", "12:40", "中国东方航空", 100),
        ("tulufan", "urumqi", "09:10", "10:00", "中国南方航空", 140),
        ("yili", "beijing", "11:20", "15:30", "中国东方航空", 95),
    ],
    "西藏": [
        ("lasa", "beijing", "07:50", "11:20", "中国国际航空", 80),
        ("lasa", "chengdu", "12:30", "14:30", "中国国际航空", 95),
        ("lasa", "chongqing", "15:20", "17:50", "四川航空", 90),
        ("lasa", "xian", "09:30", "12:10", "中国东方航空", 90),
        ("rikaze", "chengdu", "13:40", "15:50", "中国国际航空", 90),
        ("linzhi", "chengdu", "10:50", "12:40", "中国国际航空", 95),
    ],
    "台湾": [
        ("taibei", "shanghai", "10:10", "12:00", "中华航空", 110),
        ("taibei", "beijing", "13:30", "16:40", "中华航空", 100),
        ("taibei", "guangzhou", "16:20", "18:20", "中华航空", 110),
        ("taibei", "xiamen", "09:00", "10:40", "厦门航空", 115),
        ("gaoxiong", "shanghai", "11:00", "13:10", "中华航空", 105),
        ("gaoxiong", "xiamen", "14:20", "15:40", "厦门航空", 115),
    ],
    "香港": [
        ("xianggang", "beijing", "09:00", "12:10", "国泰航空", 110),
        ("xianggang", "shanghai", "13:20", "15:40", "国泰航空", 115),
        ("xianggang", "chengdu", "16:00", "18:30", "国泰航空", 110),
        ("xianggang", "hangzhou", "10:40", "13:00", "国泰航空", 105),
        ("xianggang", "sanya", "14:50", "16:40", "国泰航空", 110),
    ],
    "澳门": [
        ("aomen", "beijing", "10:30", "13:50", "澳门航空", 105),
        ("aomen", "shanghai", "14:30", "16:50", "澳门航空", 110),
        ("aomen", "chengdu", "09:20", "11:50", "澳门航空", 110),
        ("aomen", "xian", "17:10", "19:50", "澳门航空", 105),
    ],
}

# 合并自动补齐航线（无航线有机场城市 -> 本省枢纽往返），保证每个有机场城市都能查到航班
for _prov, _routes in FILL_FLIGHTS.items():
    if _prov in SEED_FLIGHTS_BY_PROVINCE:
        SEED_FLIGHTS_BY_PROVINCE[_prov].extend(_routes)
    else:
        SEED_FLIGHTS_BY_PROVINCE[_prov] = _routes


def seed_fingerprint() -> str:
    """种子内容指纹：城市/航班任一字段（含票价）变化都会触发重建。"""
    h = hashlib.sha256()
    for code, name, province in SEED_CITIES:
        h.update(f"{code}|{name}|{province}\n".encode("utf-8"))
    for province in sorted(SEED_FLIGHTS_BY_PROVINCE):
        for f in SEED_FLIGHTS_BY_PROVINCE[province]:
            h.update(f"{province}|{'|'.join(map(str, f))}\n".encode("utf-8"))
    return h.hexdigest()


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123456"
DEMO_USERNAME = "demo01"
DEMO_PASSWORD = "Demo123456"


def init_schema():
    with engine.begin() as conn:
        for statement in [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]:
            conn.execute(text(statement))


def seed_if_empty():
    """基础数据初始化：城市/航班与种子不一致（编码体系变更、票价调整）时重建。

    首次启动或种子升级（如本次票价改为按真实距离计价）会清空旧业务数据后按种子
    重建；已与种子一致时跳过，避免覆盖管理员在后台的调整。用户账号不重置。
    """
    with SessionLocal() as db:
        db_codes = {c.city_code for c in db.query(City.city_code).all()}
        seed_codes = {c[0] for c in SEED_CITIES}
        db_flight_count = db.query(Flight).count()
        seed_flight_count = sum(len(r) for r in SEED_FLIGHTS_BY_PROVINCE.values())
        fingerprint = seed_fingerprint()
        stored_fingerprint = db.execute(
            text("SELECT v FROM app_meta WHERE k = 'seed_fingerprint'")
        ).scalar()
        need_rebuild = (
            db_codes != seed_codes
            or db_flight_count != seed_flight_count
            or stored_fingerprint != fingerprint
        )

        if need_rebuild:
            db.execute(text("DELETE FROM order_status_log"))
            db.execute(text("DELETE FROM orders"))
            db.execute(text("DELETE FROM flight"))
            db.execute(text("DELETE FROM city"))

            # 城市：code -> (省份, 名称)，带省份字段
            city_ids = {}
            for code, name, province in SEED_CITIES:
                city = City(city_code=code, city_name=name, province=province)
                db.add(city)
                db.flush()
                city_ids[code] = city.id

            # 航班：按省份分组的航线展开为航班（航班号 = FR + 序号）
            flight_seq = 200
            for _province, routes in SEED_FLIGHTS_BY_PROVINCE.items():
                for f in routes:
                    from_id = city_ids.get(f[0])
                    to_id = city_ids.get(f[1])
                    if from_id is None or to_id is None:
                        raise SystemExit(f"航班种子引用了未收录的城市代码: {f[0]} / {f[1]}")
                    economy = price_economy(haversine_km(f[0], f[1]))
                    db.add(Flight(
                        flight_no=f"FR{flight_seq}",
                        from_city_id=from_id,
                        to_city_id=to_id,
                        depart_time=f[2],
                        arrive_time=f[3],
                        airline=f[4],
                        price_economy=economy,
                        price_business=price_business(economy),
                        price_first=price_first(economy),
                        seat_remain=f[5],
                    ))
                    flight_seq += 1
            db.execute(
                text("INSERT INTO app_meta (k, v) VALUES ('seed_fingerprint', :v) "
                     "ON DUPLICATE KEY UPDATE v = :v"),
                {"v": fingerprint},
            )
            logger.info("基础数据重建完成：城市 %d 个、航班 %d 条", len(city_ids), seed_flight_count)
        else:
            logger.info("基础数据与种子一致，跳过重建（城市 %d 个、航班 %d 条）", len(db_codes), db_flight_count)

        if db.query(AdminUser).count() == 0:
            db.add(AdminUser(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD), role="SUPER"))
            logger.info("已初始化管理员账号 %s", ADMIN_USERNAME)

        if db.query(User).filter(User.username == DEMO_USERNAME).count() == 0:
            db.add(User(
                username=DEMO_USERNAME,
                password_hash=hash_password(DEMO_PASSWORD),
                security_question="您最喜欢的城市是？",
                security_answer_hash=hash_password("HANGZHOU"),
            ))
            logger.info("已初始化演示账号 %s", DEMO_USERNAME)
        db.commit()
