-- 航班预订系统建表脚本（与 app/seed.py 中 SCHEMA_SQL 保持一致）
-- MySQL 8.0 / utf8mb4

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
  `city_code` VARCHAR(16) NOT NULL,
  `city_name` VARCHAR(64) NOT NULL,
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
