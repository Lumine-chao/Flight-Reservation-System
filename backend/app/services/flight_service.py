from sqlalchemy.orm import Session

from .. import constants
from ..exceptions import BizException
from ..models import City, Flight


def _flight_out(flight: Flight, from_city: City, to_city: City) -> dict:
    return {
        "id": flight.id,
        "flightNo": flight.flight_no,
        "fromCity": from_city.city_code,
        "fromCityName": from_city.city_name,
        "toCity": to_city.city_code,
        "toCityName": to_city.city_name,
        "departTime": flight.depart_time,
        "arriveTime": flight.arrive_time,
        "airline": flight.airline,
        "priceEconomy": float(flight.price_economy),
        "priceBusiness": float(flight.price_business),
        "priceFirst": float(flight.price_first),
        "seatRemain": flight.seat_remain,
        "status": flight.status,
    }


def list_cities(db: Session) -> list[dict]:
    cities = db.query(City).filter(City.status == 1).order_by(City.id.asc()).all()
    return [
        {"id": c.id, "cityCode": c.city_code, "cityName": c.city_name, "province": c.province, "status": c.status}
        for c in cities
    ]


def search_flights(db: Session, from_city_code: str, to_city_code: str) -> list[dict]:
    """按航线与日期筛选航班（OR-01、OR-05）。"""
    if from_city_code == to_city_code:
        raise BizException(3009)
    from_city = db.query(City).filter(City.city_code == from_city_code).first()
    to_city = db.query(City).filter(City.city_code == to_city_code).first()
    if not from_city or not to_city:
        raise BizException(3010)
    flights = db.query(Flight).filter(
        Flight.status == 1,
        Flight.from_city_id == from_city.id,
        Flight.to_city_id == to_city.id,
    ).order_by(Flight.depart_time.asc()).all()
    return [_flight_out(f, from_city, to_city) for f in flights]


def flight_detail(db: Session, flight_no: str) -> dict:
    flight = db.query(Flight).filter(Flight.flight_no == flight_no, Flight.status == 1).first()
    if not flight:
        raise BizException(3011)
    from_city = db.get(City, flight.from_city_id)
    to_city = db.get(City, flight.to_city_id)
    return _flight_out(flight, from_city, to_city)
