from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from .. import constants, validators
from ..dependencies import order_not_found
from ..exceptions import BizException
from ..models import City, Flight, Order, OrderStatusLog
from ..redis_client import get_kv


def _flight_of(db: Session, flight_id: int) -> Flight:
    return db.get(Flight, flight_id)


def _city_of(db: Session, city_id: int) -> City:
    return db.get(City, city_id)


def _city_by_code(db: Session, code: str) -> City | None:
    return db.query(City).filter(City.city_code == code, City.status == 1).first()


def _unit_price(flight: Flight, seat_class: str) -> float:
    field = constants.SEAT_PRICE_FIELD[seat_class]
    return float(getattr(flight, field))


def _take_seats(db: Session, flight_id: int, count: int) -> bool:
    """原子扣减余票：条件更新，并发下不会超卖。"""
    affected = db.query(Flight).filter(
        Flight.id == flight_id,
        Flight.seat_remain >= count,
    ).update({Flight.seat_remain: Flight.seat_remain - count}, synchronize_session=False)
    return bool(affected)


def _release_seats(db: Session, flight_id: int, count: int):
    """回补余票（取消、改单减少票数、改签航班时使用）。"""
    db.query(Flight).filter(Flight.id == flight_id).update(
        {Flight.seat_remain: Flight.seat_remain + count}, synchronize_session=False
    )


def _write_status_log(db: Session, order: Order, from_status: str | None, to_status: str,
                      action: str, operator_type: str, operator_id: int | None, remark: str | None = None):
    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=from_status,
        to_status=to_status,
        action=action,
        operator_type=operator_type,
        operator_id=operator_id,
        operate_time=datetime.now(),
        remark=remark,
    ))


def to_order_out(order: Order, flight: Flight, from_city: City, to_city: City) -> dict:
    return {
        "orderNo": order.order_no,
        "flightNo": flight.flight_no,
        "flightDate": order.flight_date.strftime("%m/%d/%y"),
        "departTime": flight.depart_time,
        "arriveTime": flight.arrive_time,
        "airline": flight.airline,
        "fromCity": from_city.city_code,
        "fromCityName": from_city.city_name,
        "toCity": to_city.city_code,
        "toCityName": to_city.city_name,
        "passengerName": order.passenger_name,
        "ticketCount": order.ticket_count,
        "seatClass": order.seat_class,
        "seatClassName": constants.SEAT_CLASS_LABELS.get(order.seat_class, order.seat_class),
        "unitPrice": float(order.unit_price),
        "totalPrice": float(order.total_price),
        "status": order.status,
        "statusName": constants.ORDER_STATUS.get(order.status, order.status),
        "version": order.version,
        "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updatedAt": order.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _order_with_detail(db: Session, order: Order) -> dict:
    flight = _flight_of(db, order.flight_id)
    from_city = _city_of(db, order.from_city_id)
    to_city = _city_of(db, order.to_city_id)
    return to_order_out(order, flight, from_city, to_city)


def create_order(db: Session, user_id: int, payload) -> dict:
    """新建订单（OR-01 ~ OR-10）：校验 → 计价 → 生成订单号 → 落库并留痕。"""
    flight_date, date_code = validators.validate_flight_date(payload.flightDate)
    if date_code == 3001:
        raise BizException(3001, f"此日期后的航班日期有效{validators.format_date(validators.today())}")
    if date_code:
        raise BizException(date_code)

    code = validators.validate_cities(payload.fromCity, payload.toCity)
    if code:
        raise BizException(code)
    from_city = _city_by_code(db, payload.fromCity)
    to_city = _city_by_code(db, payload.toCity)
    if not from_city or not to_city:
        raise BizException(3010)

    flight = db.query(Flight).filter(
        Flight.flight_no == payload.flightNo,
        Flight.status == 1,
        Flight.from_city_id == from_city.id,
        Flight.to_city_id == to_city.id,
    ).first()
    if not flight:
        raise BizException(3011)

    ticket_count = payload.ticketCount or 1
    if not (1 <= ticket_count <= 9):
        raise BizException(3007)

    seat_class = (payload.seatClass or "ECONOMY").upper()
    if seat_class not in constants.SEAT_CLASSES:
        raise BizException(3012)

    passenger_name = (payload.passengerName or "").strip()
    if not passenger_name:
        raise BizException(3013)

    unit_price = _unit_price(flight, seat_class)
    total_price = unit_price * ticket_count

    if not _take_seats(db, flight.id, ticket_count):
        raise BizException(3014)

    order_no = _generate_order_no(db)
    order = Order(
        order_no=order_no,
        user_id=user_id,
        flight_id=flight.id,
        flight_date=flight_date,
        passenger_name=passenger_name,
        from_city_id=from_city.id,
        to_city_id=to_city.id,
        ticket_count=ticket_count,
        seat_class=seat_class,
        unit_price=unit_price,
        total_price=total_price,
        status="TICKETED",
    )
    db.add(order)
    db.flush()
    _write_status_log(db, order, None, "TICKETED", constants.ACTION_CREATE, constants.OPERATOR_USER, user_id)
    db.commit()
    return {"orderNo": order_no, "totalPrice": round(total_price, 2), "status": "TICKETED"}


def _generate_order_no(db: Session) -> str:
    """订单号：业务前缀 + 日期 + 序列（FR202609170001），Redis 自增保证唯一。

    内存降级模式下服务重启后计数器会丢失，首次使用时从库中当天最大订单号续起，
    避免与已有订单号重复。
    """
    today_code = datetime.now().strftime("%Y%m%d")
    seq_key = constants.KEY_ORDER_SEQ.format(today_code)
    kv = get_kv()
    if kv.ttl(seq_key) == -2:
        row = db.query(func.max(Order.order_no)).filter(
            Order.order_no.like(f"FR{today_code}%")
        ).scalar()
        if row:
            kv.set(seq_key, int(row[10:]))
    seq = kv.incr(seq_key)
    kv.expire(seq_key, _seconds_until_midnight())
    return f"FR{today_code}{seq:04d}"


def _seconds_until_midnight() -> int:
    from datetime import timedelta

    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(60, int((midnight - now).total_seconds()))


def list_orders(db: Session, user_id: int, status: str | None = None) -> list[dict]:
    q = db.query(Order).filter(Order.user_id == user_id)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.created_at.desc()).all()
    return [_order_with_detail(db, o) for o in orders]


def search_orders(db: Session, user_id: int, order_no: str | None = None,
                  passenger_name: str | None = None, flight_date: str | None = None) -> list[dict]:
    """按订单号 / 乘机人 / 航班日期检索本人订单（OR-14 ~ OR-17）。"""
    if order_no:
        order = db.query(Order).filter(Order.order_no == order_no, Order.user_id == user_id).first()
        if not order:
            order_not_found()
        return [_order_with_detail(db, order)]

    if passenger_name:
        orders = db.query(Order).filter(
            Order.user_id == user_id, Order.passenger_name == passenger_name
        ).order_by(Order.created_at.desc()).all()
        if not orders:
            raise BizException(3002)
        return [_order_with_detail(db, o) for o in orders]

    if flight_date:
        d = validators.parse_flight_date(flight_date)
        if d is None:
            raise BizException(3008)
        orders = db.query(Order).filter(Order.user_id == user_id, Order.flight_date == d) \
            .order_by(Order.created_at.desc()).all()
        if not orders:
            raise BizException(3003)
        return [_order_with_detail(db, o) for o in orders]

    return list_orders(db, user_id)


def get_order_detail(db: Session, user_id: int, order_no: str) -> dict:
    order = db.query(Order).filter(Order.order_no == order_no, Order.user_id == user_id).first()
    if not order:
        order_not_found()
    data = _order_with_detail(db, order)
    logs = db.query(OrderStatusLog).filter(OrderStatusLog.order_id == order.id) \
        .order_by(OrderStatusLog.operate_time.asc()).all()
    data["statusLog"] = [
        {
            "fromStatus": log.from_status,
            "toStatus": log.to_status,
            "toStatusName": constants.ORDER_STATUS.get(log.to_status, log.to_status),
            "action": log.action,
            "operatorType": log.operator_type,
            "operatorId": log.operator_id,
            "operateTime": log.operate_time.strftime("%Y-%m-%d %H:%M:%S"),
            "remark": log.remark,
        }
        for log in logs
    ]
    return data


def _find_flight_for_route(db: Session, from_city: City, to_city: City, flight_no: str | None) -> Flight:
    q = db.query(Flight).filter(
        Flight.status == 1,
        Flight.from_city_id == from_city.id,
        Flight.to_city_id == to_city.id,
    )
    if flight_no:
        q = q.filter(Flight.flight_no == flight_no)
    return q.first()


def update_order(db: Session, user_id: int, order_no: str, payload) -> dict:
    """更新订单（OR-18 ~ OR-22）：仅已出票且航班日期未到的订单可修改。

    并发安全分两层：余票用条件更新原子增减，订单行用 version 乐观锁，
    若读取后被其他请求改过，提交时抛 3015 而不是静默覆盖。
    """
    order = db.query(Order).filter(Order.order_no == order_no, Order.user_id == user_id).first()
    if not order:
        order_not_found()
    if payload.orderNo is not None:
        raise BizException(3006)
    if order.status != "TICKETED" or order.flight_date <= validators.today():
        raise BizException(3005)

    old_flight_id = order.flight_id
    old_count = order.ticket_count
    old_from = _city_of(db, order.from_city_id)
    old_to = _city_of(db, order.to_city_id)

    # 先把所有变更校验完并取值，最后统一写库，避免中途抛错留下半更新状态
    new_flight_date = order.flight_date
    if payload.flightDate is not None:
        new_flight_date, date_code = validators.validate_flight_date(payload.flightDate)
        if date_code == 3001:
            raise BizException(3001, f"此日期后的航班日期有效{validators.format_date(validators.today())}")
        if date_code:
            raise BizException(date_code)

    from_city, to_city = old_from, old_to
    flight = _flight_of(db, old_flight_id)
    if payload.fromCity is not None or payload.toCity is not None:
        new_from_code = payload.fromCity or old_from.city_code
        new_to_code = payload.toCity or old_to.city_code
        code = validators.validate_cities(new_from_code, new_to_code)
        if code:
            raise BizException(code)
        new_from = _city_by_code(db, new_from_code)
        new_to = _city_by_code(db, new_to_code)
        if not new_from or not new_to:
            raise BizException(3010)
        from_city, to_city = new_from, new_to
        # 起终点变化后 flight_id 必须属于新航线（OR-18、OR-20）
        new_flight = _find_flight_for_route(db, from_city, to_city, payload.flightNo)
        if not new_flight:
            raise BizException(3011)
        flight = new_flight
    elif payload.flightNo is not None:
        # 单独修改航班号：必须属于当前航线
        f = db.query(Flight).filter(
            Flight.flight_no == payload.flightNo,
            Flight.status == 1,
            Flight.from_city_id == from_city.id,
            Flight.to_city_id == to_city.id,
        ).first()
        if not f:
            raise BizException(3011)
        flight = f

    new_count = old_count
    if payload.ticketCount is not None:
        if not (1 <= payload.ticketCount <= 9):
            raise BizException(3007)
        new_count = payload.ticketCount

    new_seat_class = order.seat_class
    if payload.seatClass is not None:
        seat_class = payload.seatClass.upper()
        if seat_class not in constants.SEAT_CLASSES:
            raise BizException(3012)
        new_seat_class = seat_class

    new_passenger = order.passenger_name
    if payload.passengerName is not None:
        name = payload.passengerName.strip()
        if not name:
            raise BizException(3013)
        new_passenger = name

    # 余票调整：同航班只动差额；换航班则先占新航班，成功后再释放原航班
    if flight.id == old_flight_id:
        delta = new_count - old_count
        if delta > 0 and not _take_seats(db, flight.id, delta):
            db.rollback()
            raise BizException(3014)
        if delta < 0:
            _release_seats(db, flight.id, -delta)
    else:
        if not _take_seats(db, flight.id, new_count):
            db.rollback()
            raise BizException(3014)
        _release_seats(db, old_flight_id, old_count)

    order.flight_date = new_flight_date
    order.flight_id = flight.id
    order.from_city_id = from_city.id
    order.to_city_id = to_city.id
    order.passenger_name = new_passenger
    order.ticket_count = new_count
    order.seat_class = new_seat_class
    # 舱位或票数变更后服务端重算并回写（OR-22）
    order.unit_price = _unit_price(flight, new_seat_class)
    order.total_price = order.unit_price * new_count
    order.updated_at = datetime.now()

    _write_status_log(db, order, order.status, order.status, constants.ACTION_UPDATE,
                      constants.OPERATOR_USER, user_id)
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise BizException(3015)
    return _order_with_detail(db, order)


def cancel_order(db: Session, user_id: int, order_no: str) -> dict:
    """取消订单（OR-23 ~ OR-27）：写 CANCELLED 而非物理删除，记录保留可追溯。"""
    order = db.query(Order).filter(Order.order_no == order_no, Order.user_id == user_id).first()
    if not order:
        order_not_found()
    if order.status != "TICKETED" or order.flight_date <= validators.today():
        raise BizException(3016)

    # 先回补余票再改状态：条件更新不触发订单行的自动 flush，避免乐观锁提前冲突
    _release_seats(db, order.flight_id, order.ticket_count)
    _write_status_log(db, order, order.status, "CANCELLED", constants.ACTION_CANCEL,
                      constants.OPERATOR_USER, user_id)
    order.status = "CANCELLED"
    order.updated_at = datetime.now()
    try:
        db.commit()
    except StaleDataError:
        # 并发取消/改单：后到的请求整笔回滚，余票不会被重复回补
        db.rollback()
        raise BizException(3015)
    return {"orderNo": order.order_no, "status": "CANCELLED"}


def auto_done_orders(db: Session) -> int:
    """定时任务：将航班日期已过且状态为 TICKETED 的订单批量置为 DONE（SYSTEM 留痕）。"""
    expired = db.query(Order).filter(
        Order.status == "TICKETED", Order.flight_date < validators.today()
    ).all()
    count = 0
    for order in expired:
        _write_status_log(db, order, order.status, "DONE", constants.ACTION_AUTO_DONE,
                          constants.OPERATOR_SYSTEM, None)
        order.status = "DONE"
        order.updated_at = datetime.now()
        try:
            db.commit()
        except StaleDataError:
            # 用户在定时任务执行的同时取消/改单，跳过该单即可
            db.rollback()
            continue
        count += 1
    return count
