-- SQLite 3 建表 DDL（由 SQLAlchemy 模型生成，应用启动时自动执行，此文件供查阅）

CREATE TABLE admin_user (
	id INTEGER NOT NULL, 
	username VARCHAR(32) NOT NULL, 
	password_hash VARCHAR(100) NOT NULL, 
	role VARCHAR(16) NOT NULL, 
	status SMALLINT NOT NULL, 
	last_login_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);

CREATE TABLE app_meta (
	k VARCHAR(32) NOT NULL, 
	v VARCHAR(128) NOT NULL, 
	PRIMARY KEY (k)
);

CREATE TABLE city (
	id INTEGER NOT NULL, 
	city_code VARCHAR(64) NOT NULL, 
	city_name VARCHAR(64) NOT NULL, 
	province VARCHAR(64) NOT NULL, 
	status SMALLINT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (city_code)
);

CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(16) NOT NULL, 
	password_hash VARCHAR(100) NOT NULL, 
	security_question VARCHAR(64) NOT NULL, 
	security_answer_hash VARCHAR(100) NOT NULL, 
	status SMALLINT NOT NULL, 
	locked_until DATETIME, 
	fail_count INTEGER NOT NULL, 
	token_version INTEGER NOT NULL, 
	last_login_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);

CREATE TABLE flight (
	id INTEGER NOT NULL, 
	flight_no VARCHAR(32) NOT NULL, 
	from_city_id INTEGER NOT NULL, 
	to_city_id INTEGER NOT NULL, 
	depart_time VARCHAR(8) NOT NULL, 
	arrive_time VARCHAR(8) NOT NULL, 
	airline VARCHAR(64) NOT NULL, 
	price_economy NUMERIC(10, 2) NOT NULL, 
	price_business NUMERIC(10, 2) NOT NULL, 
	price_first NUMERIC(10, 2) NOT NULL, 
	seat_remain INTEGER NOT NULL, 
	status SMALLINT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (flight_no), 
	FOREIGN KEY(from_city_id) REFERENCES city (id), 
	FOREIGN KEY(to_city_id) REFERENCES city (id)
);
CREATE INDEX idx_route ON flight (from_city_id, to_city_id);

CREATE TABLE orders (
	id INTEGER NOT NULL, 
	order_no VARCHAR(32) NOT NULL, 
	user_id INTEGER NOT NULL, 
	flight_id INTEGER NOT NULL, 
	flight_date DATE NOT NULL, 
	passenger_name VARCHAR(64) NOT NULL, 
	from_city_id INTEGER NOT NULL, 
	to_city_id INTEGER NOT NULL, 
	ticket_count INTEGER NOT NULL, 
	seat_class VARCHAR(16) NOT NULL, 
	unit_price NUMERIC(10, 2) NOT NULL, 
	total_price NUMERIC(10, 2) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	version INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (order_no), 
	FOREIGN KEY(user_id) REFERENCES user (id), 
	FOREIGN KEY(flight_id) REFERENCES flight (id), 
	FOREIGN KEY(from_city_id) REFERENCES city (id), 
	FOREIGN KEY(to_city_id) REFERENCES city (id)
);
CREATE INDEX idx_flight_date ON orders (flight_date);
CREATE INDEX idx_passenger_name ON orders (passenger_name);
CREATE INDEX idx_status_date ON orders (status, flight_date);
CREATE INDEX idx_user_status ON orders (user_id, status, created_at);

CREATE TABLE order_status_log (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	from_status VARCHAR(16), 
	to_status VARCHAR(16) NOT NULL, 
	action VARCHAR(32) NOT NULL, 
	operator_type VARCHAR(16) NOT NULL, 
	operator_id INTEGER, 
	operate_time DATETIME NOT NULL, 
	remark VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id)
);
CREATE INDEX idx_order ON order_status_log (order_id);
