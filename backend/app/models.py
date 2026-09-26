from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def now() -> datetime:
    return datetime.now()


class User(Base):
    """客户表 user。"""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    security_question: Mapped[str] = mapped_column(String(64), nullable=False)
    security_answer_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now, onupdate=now)


class City(Base):
    """城市表 city。"""
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    city_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    city_name: Mapped[str] = mapped_column(String(64), nullable=False)
    province: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)


class Flight(Base):
    """航班表 flight。"""
    __tablename__ = "flight"
    __table_args__ = (Index("idx_route", "from_city_id", "to_city_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    flight_no: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    from_city_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("city.id"), nullable=False)
    to_city_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("city.id"), nullable=False)
    depart_time: Mapped[str] = mapped_column(String(8), nullable=False)
    arrive_time: Mapped[str] = mapped_column(String(8), nullable=False)
    airline: Mapped[str] = mapped_column(String(64), nullable=False)
    price_economy: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_business: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_first: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    seat_remain: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)


class Order(Base):
    """订单表 orders。"""
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_user_status", "user_id", "status", "created_at"),
        Index("idx_passenger_name", "passenger_name"),
        Index("idx_flight_date", "flight_date"),
        Index("idx_status_date", "status", "flight_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    flight_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("flight.id"), nullable=False)
    flight_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    passenger_name: Mapped[str] = mapped_column(String(64), nullable=False)
    from_city_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("city.id"), nullable=False)
    to_city_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("city.id"), nullable=False)
    ticket_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    seat_class: Mapped[str] = mapped_column(String(16), nullable=False, default="ECONOMY")
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="TICKETED")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now, onupdate=now)


class OrderStatusLog(Base):
    """订单状态流转留痕表 order_status_log。"""
    __tablename__ = "order_status_log"
    __table_args__ = (Index("idx_order", "order_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("orders.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    operator_type: Mapped[str] = mapped_column(String(16), nullable=False)
    operator_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    operate_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AdminUser(Base):
    """管理员表 admin_user。"""
    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="ADMIN")
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=now, onupdate=now)
