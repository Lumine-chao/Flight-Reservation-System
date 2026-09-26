# 航班预订系统（Flight Reservation System）

一套面向终端旅客的在线机票预订平台：旅客自助完成注册登录、航班查询、下单预订与订单管理；管理员通过独立后台维护基础数据并处置异常订单。

本实现依据《航班预订系统项目说明文档（PRD）》与《航班预订系统技术架构文档》开发，后端使用 **Python FastAPI** 替代文档默认的 Java Spring Boot，功能与校验规则完全对齐需求文档。

---

## 技术栈

| 端 | 技术 |
| --- | --- |
| 后端 | Python 3.11+ · FastAPI · SQLAlchemy · Pydantic v2 · PyMySQL |
| 认证 | JWT（客户/管理员双密钥）· BCrypt 密码加密 · Redis 令牌黑名单（本地可降级为内存缓存） |
| 前端 | Vue 3 · Vite · Element Plus · Pinia · Vue Router · Axios |
| 数据库 | MySQL 8.0（utf8mb4） |
| 缓存 | Redis 7（可选，未安装时自动使用内存缓存，功能一致） |
| 部署 | Docker Compose（MySQL + Redis + 后端 + Nginx 前端） |

## 功能清单

### 账号模块
- 注册：用户名（4～8 位字母数字、非纯数字、非数字开头）、密码（8～20 位含字母与数字、不与用户名相同、非连续重复字符）、确认密码、安全问题与答案（答案加密存储）
- 登录：连续失败 4 次锁定 15 分钟（Redis 计数），展示剩余尝试次数；支持 Token 注销（黑名单）
- 忘记密码：回答安全问题验证身份后重置，连续答错 3 次锁定

### 订单模块
- 航班查询：按出发地、目的地、航班日期检索在售航班
- 新建订单：校验航线、航班、日期（须晚于今天）、票数（1～9）、舱位、乘机人、余票，服务端计价
- 我的订单：状态筛选（已出票/已完成/已取消）、按订单号/乘机人/航班日期检索、查看详情（含状态流转时间线）
- 更新订单：仅「已出票」且航班日期未到的订单可改，乐观锁（version）防并发覆盖，改舱位/票数后服务端重算价格
- 取消订单：非物理删除，状态流转留痕可追溯
- 自动完成：定时任务将航班日期已过且仍为「已出票」的订单置为「已完成」（系统留痕）

### 管理后台（独立入口 `/admin/login`）
- 基础数据：城市新增/启停（含所属省份）、航班新增/编辑/启停（三舱价格、余票、起降时间）；城市按省份分组展示
- 订单管理：按订单号/乘机人/航班日期/状态检索全部订单、查看详情、异常订单处置（取消 + 备注留痕）

## 快速开始

### 方式一：Docker Compose 一键启动（推荐）

```bash
docker compose up -d --build
```

启动后访问：

- 客户前台：http://localhost:5173
- 管理后台：http://localhost:5173/admin/login
- API 文档：http://localhost:8080/docs

默认账号：

| 角色 | 账号 | 密码 |
| --- | --- | --- |
| 管理员 | admin | Admin123456 |
| 演示客户 | demo01 | Demo123456 |

> 首次启动会自动建表并初始化 225 个城市（覆盖 34 个省级行政区，含省份归属；仅收录具有民用运输机场的城市）、630 条航班、管理员与演示账号；城市选择器为「先选省份、再选城市」的级联选择，支持输入过滤；每个有机场城市均保证至少可查到往返本省/区域枢纽的航班，不会出现选了城市却查无航班的空结果。后续启动为幂等增量——升级种子数据后，缺失的城市/航班会自动补入，不会重复插入。城市种子依据中国民用航空局颁布的民用运输机场所在地清单生成，未收录无民航机场的地级市。

### 方式二：本地开发（本机 MySQL）

1. 准备 MySQL，创建数据库与账号：

```sql
CREATE DATABASE flight_reservation DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'flight'@'%' IDENTIFIED BY 'flight123456';
GRANT ALL PRIVILEGES ON flight_reservation.* TO 'flight'@'%';
FLUSH PRIVILEGES;
```

2. 启动后端（首次会自动建表 + 初始化数据）：

```bash
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

> 配置项在 `backend/config.py` 中均有默认值，**不创建 `.env` 也能直接启动**；需要覆盖时把 `backend/.env.example` 复制为 `.env` 再改。本机未装 Redis 时保持 `REDIS_URL` 为空即可，登录锁定/令牌黑名单/订单号自增自动降级为进程内内存实现，功能一致。

3. 启动前端：

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173（Vite 已代理 `/api` 到 8080）。

## 目录结构

```
flight-reservation/
├── README.md
├── docker-compose.yml          # MySQL + Redis + 后端 + 前端 一键编排
├── .gitignore                  # 排除 .venv / node_modules / dist / .env
├── docs/                       # 架构文档与项目说明
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example            # 配置模板（可选，复制为 .env 后覆盖默认值）
│   ├── app/
│   │   ├── main.py             # 应用入口（含定时任务启动）
│   │   ├── config.py           # 环境配置（pydantic-settings，字段均有默认值）
│   │   ├── models.py           # SQLAlchemy 模型
│   │   ├── schemas.py          # Pydantic 入参模型
│   │   ├── validators.py       # 用户名/密码/日期/航线校验
│   │   ├── security.py         # BCrypt + JWT
│   │   ├── redis_client.py     # Redis 封装（可降级内存）
│   │   ├── dependencies.py     # 鉴权依赖
│   │   ├── exceptions.py       # 业务异常
│   │   ├── constants.py        # 错误码 / 状态机 / 提示语
│   │   ├── scheduler.py        # 订单自动完成定时任务
│   │   ├── seed.py             # 建表 + 初始化数据（三舱票价按距离计算）
│   │   ├── services/           # 业务服务层
│   │   └── routers/            # 路由层
│   └── sql/
│       ├── schema.sql          # 建表 DDL
│       ├── pricing.py          # 统一计价：距离 → 三舱价格
│       ├── coords.py           # 城市经纬度（计价用）
│       ├── cities_data.py      # 225 城省份归属（生成）
│       ├── flights_fill.py     # 支线航线（生成）
│       ├── generate_cities.py  # 城市数据生成脚本
│       ├── _gen_fill.py        # 支线航线生成脚本
│       ├── migrate.py          # 迁移脚本
│       ├── check_coords.py     # 经纬度校验
│       └── check_flights.py    # 航线覆盖校验
└── frontend/
    ├── Dockerfile
    ├── nginx.conf              # 静态托管 + /api 反代
    ├── vite.config.js          # dev 代理
    └── src/
        ├── views/              # 8 个页面（含管理端 3 个）
        ├── components/         # 导航、状态标签、航班/乘机人表单
        ├── api/                # axios 封装（客户/管理员双实例）
        ├── stores/             # Pinia（token / user / admin）
        └── utils/              # 常量、校验、日期工具
```

## 接口一览

所有接口统一返回 `{ code, message, data }`，`code = 0` 表示成功。

| 模块 | 方法与路径 | 说明 |
| --- | --- | --- |
| 注册 | POST /api/users/register | 注册并自动登录 |
| 当前用户 | GET /api/users/me | 查询当前登录用户 |
| 登录 | POST /api/auth/login | 失败计数、锁定 |
| 安全问题 | GET /api/auth/security-question?username= | 查询注册安全问题 |
| 重置密码 | POST /api/auth/reset-password | 安全答案验证 + 重置 |
| 刷新令牌 | POST /api/auth/refresh | 续期客户令牌 |
| 登出 | POST /api/auth/logout | 令牌加入黑名单 |
| 城市列表 | GET /api/base/cities | 在售城市 |
| 航班查询 | GET /api/flights?fromCity=&toCity= | 按航线检索在售航班 |
| 航班详情 | GET /api/flights/{flight_no} | 航班详情（含余票） |
| 创建订单 | POST /api/orders | 创建订单（服务端计价） |
| 订单列表 | GET /api/orders?status= | 我的订单（按状态筛选） |
| 订单检索 | GET /api/orders/search?orderNo=&passengerName=&flightDate= | 我的订单检索 |
| 订单详情 | GET /api/orders/{order_no} | 订单详情 + 状态流转时间线 |
| 更新订单 | PUT /api/orders/{order_no} | 改日期/航班/舱位/票数（乐观锁） |
| 取消订单 | POST /api/orders/{order_no}/cancel | 取消订单（留痕） |
| 管理员登录 | POST /api/admin/login | 管理员登录（独立密钥） |
| 城市管理 | GET/POST /api/admin/cities | 城市列表 / 新增 |
| 城市启停 | PUT /api/admin/cities/{city_id}/status | 城市启停 |
| 航班管理 | GET/POST /api/admin/flights | 航班列表 / 新增编辑 |
| 订单检索 | GET /api/admin/orders | 全部订单检索（按订单号/乘机人/日期/状态） |
| 订单处置 | POST /api/admin/orders/{order_no}/handle | 异常订单处置（取消 + 备注） |

> 客户接口均需请求头 `Authorization: Bearer <token>`；管理端接口使用管理员令牌，两套令牌密钥隔离。

## 设计要点

- **错误码驱动提示语**：全部业务异常统一走 `constants.py` 中的错误码，前端拿到中文提示直接展示，杜绝系统级报错。
- **订单状态机**：`TICKETED → DONE / CANCELLED`，状态流转一律写 `order_status_log` 留痕（操作人：客户/系统/管理员）。
- **订单号唯一**：`FR + 日期 + Redis 自增序号`，跨天自动重置。
- **数据安全**：密码与安全答案 BCrypt 加密存储；客户仅能访问本人订单（接口层强制 user_id 过滤）；乐观锁版本号防并发覆盖。
- **权限隔离**：客户 JWT 与管理员 JWT 使用不同密钥与登录态，管理端接口独立鉴权。
