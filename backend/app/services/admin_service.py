from datetime import datetime

from sqlalchemy.orm import Session

from .. import constants, validators
from ..exceptions import BizException
from ..models import AdminUser, City, Flight, Order, User
from ..security import check_password, create_admin_token
from .order_service import _write_status_log, to_order_out


def admin_login(db: Session, username: str, password: str) -> dict:
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not check_password(password, admin.password_hash):
        raise BizException(5001)
    if admin.status != 1:
        raise BizException(5002)
    admin.last_login_at = datetime.now()
    db.commit()
    token, expires_at = create_admin_token(admin.id, admin.username, admin.role)
    return {"token": token, "expiresAt": expires_at, "username": admin.username, "role": admin.role}


# ============ 城市基础数据维护 ============
def create_city(db: Session, city_code: str, city_name: str, province: str = "") -> dict:
    city_code = city_code.strip().upper()
    city_name = city_name.strip()
    province = province.strip()
    if not city_code or not city_name:
        raise BizException(5004)
    exists = db.query(City).filter(City.city_code == city_code).first()
    if exists:
        raise BizException(5004)
    city = City(city_code=city_code, city_name=city_name, province=province)
    db.add(city)
    db.commit()
    return {"id": city.id, "cityCode": city.city_code, "cityName": city.city_name,
            "province": city.province, "status": city.status}


def update_city_status(db: Session, city_id: int, status: int) -> dict:
    city = db.get(City, city_id)
    if not city:
        raise BizException(3010)
    city.status = 1 if status == 1 else 0
    db.commit()
    return {"id": city.id, "cityCode": city.city_code, "cityName": city.city_name,
            "province": city.province, "status": city.status}


def list_all_cities(db: Session) -> list[dict]:
    cities = db.query(City).order_by(City.id.asc()).all()
    return [
        {"id": c.id, "cityCode": c.city_code, "cityName": c.city_name,
         "province": c.province, "status": c.status}
        for c in cities
    ]


# ============ 航班与舱位价格维护 ============
def _city_required(db: Session, code: str) -> City:
    city = db.query(City).filter(City.city_code == code).first()
    if not city:
        raise BizException(3010)
    return city


def upsert_flight(db: Session, payload) -> dict:
    from_city = _city_required(db, payload.fromCity)
    to_city = _city_required(db, payload.toCity)
    if payload.fromCity == payload.toCity:
        raise BizException(3009)
    if not payload.flightNo.strip():
        raise BizException(5005)

    flight = db.get(Flight, payload.id) if payload.id else None
    if flight:
        exists = db.query(Flight).filter(Flight.flight_no == payload.flightNo, Flight.id != flight.id).first()
        if exists:
            raise BizException(5005)
        flight.flight_no = payload.flightNo.strip().upper()
        flight.from_city_id = from_city.id
        flight.to_city_id = to_city.id
        flight.depart_time = payload.departTime
        flight.arrive_time = payload.arriveTime
        flight.airline = payload.airline
        flight.price_economy = payload.priceEconomy
        flight.price_business = payload.priceBusiness
        flight.price_first = payload.priceFirst
        flight.seat_remain = payload.seatRemain
        flight.status = payload.status
    else:
        exists = db.query(Flight).filter(Flight.flight_no == payload.flightNo).first()
        if exists:
            raise BizException(5005)
        flight = Flight(
            flight_no=payload.flightNo.strip().upper(),
            from_city_id=from_city.id,
            to_city_id=to_city.id,
            depart_time=payload.departTime,
            arrive_time=payload.arriveTime,
            airline=payload.airline,
            price_economy=payload.priceEconomy,
            price_business=payload.priceBusiness,
            price_first=payload.priceFirst,
            seat_remain=payload.seatRemain,
            status=payload.status,
        )
        db.add(flight)
    db.commit()
    return {"id": flight.id, "flightNo": flight.flight_no, "status": flight.status,
            "fromCityName": from_city.city_name, "toCityName": to_city.city_name}


def list_all_flights(db: Session) -> list[dict]:
    flights = db.query(Flight).order_by(Flight.flight_no.asc()).all()
    cities = {c.id: c for c in db.query(City).all()}
    result = []
    for f in flights:
        fc = cities.get(f.from_city_id)
        tc = cities.get(f.to_city_id)
        item = _flight_out(f, fc, tc)
        result.append(item)
    return result


def _flight_out(flight: Flight, from_city: City | None, to_city: City | None) -> dict:
    return {
        "id": flight.id,
        "flightNo": flight.flight_no,
        "fromCity": from_city.city_code if from_city else "",
        "fromCityName": from_city.city_name if from_city else "",
        "toCity": to_city.city_code if to_city else "",
        "toCityName": to_city.city_name if to_city else "",
        "departTime": flight.depart_time,
        "arriveTime": flight.arrive_time,
        "airline": flight.airline,
        "priceEconomy": float(flight.price_economy),
        "priceBusiness": float(flight.price_business),
        "priceFirst": float(flight.price_first),
        "seatRemain": flight.seat_remain,
        "status": flight.status,
    }


# ============ 订单查询与异常订单处置 ============
def admin_search_orders(db: Session, order_no: str | None = None, passenger_name: str | None = None,
                        flight_date: str | None = None, status: str | None = None) -> list[dict]:
    q = db.query(Order)
    if order_no:
        q = q.filter(Order.order_no == order_no)
    if passenger_name:
        q = q.filter(Order.passenger_name == passenger_name)
    if flight_date:
        d = validators.parse_flight_date(flight_date)
        if d is None:
            raise BizException(3008)
        q = q.filter(Order.flight_date == d)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.created_at.desc()).limit(200).all()
    if not orders:
        if order_no:
            raise BizException(3004)
        raise BizException(3003)
    return [_order_out_admin(db, o) for o in orders]


def _order_out_admin(db: Session, order: Order) -> dict:
    from .order_service import _city_of, _flight_of

    flight = _flight_of(db, order.flight_id)
    from_city = _city_of(db, order.from_city_id)
    to_city = _city_of(db, order.to_city_id)
    data = to_order_out(order, flight, from_city, to_city)
    user = db.query(User).filter(User.id == order.user_id).first()
    data["userName"] = user.username if user else ""
    return data


def admin_handle_order(db: Session, admin: AdminUser, order_no: str, action: str, remark: str | None) -> dict:
    """异常订单处置：取消 + 备注，写入流转留痕（ADMIN）。"""
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise BizException(3004)
    if order.status != "TICKETED":
        raise BizException(3016)
    _write_status_log(db, order, order.status, "CANCELLED", constants.ACTION_ADMIN_CANCEL,
                      constants.OPERATOR_ADMIN, admin.id, remark)
    order.status = "CANCELLED"
    order.updated_at = datetime.now()
    db.commit()
    return {"orderNo": order.order_no, "status": "CANCELLED"}
