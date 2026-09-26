from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_admin
from ..models import AdminUser
from ..schemas import AdminHandleIn, AdminLoginIn, CityCreateIn, CityStatusIn, FlightUpsertIn
from ..services import admin_service

router = APIRouter(prefix="/api/admin", tags=["管理端"])


@router.post("/login")
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)):
    data = admin_service.admin_login(db, payload.username, payload.password)
    return {"code": 0, "message": "登录成功", "data": data}


@router.get("/cities")
def list_cities(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": admin_service.list_all_cities(db)}


@router.post("/cities")
def create_city(payload: CityCreateIn, admin: AdminUser = Depends(get_current_admin),
                db: Session = Depends(get_db)):
    return {"code": 0, "message": "城市保存成功", "data": admin_service.create_city(db, payload.cityCode, payload.cityName, payload.province)}


@router.put("/cities/{city_id}/status")
def update_city_status(city_id: int, payload: CityStatusIn, admin: AdminUser = Depends(get_current_admin),
                       db: Session = Depends(get_db)):
    return {"code": 0, "message": "状态已更新", "data": admin_service.update_city_status(db, city_id, payload.status)}


@router.get("/flights")
def list_flights(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": admin_service.list_all_flights(db)}


@router.post("/flights")
def upsert_flight(payload: FlightUpsertIn, admin: AdminUser = Depends(get_current_admin),
                  db: Session = Depends(get_db)):
    return {"code": 0, "message": "航班保存成功", "data": admin_service.upsert_flight(db, payload)}


@router.get("/orders")
def admin_orders(orderNo: str | None = Query(None), passengerName: str | None = Query(None),
                 flightDate: str | None = Query(None), status: str | None = Query(None),
                 admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {
        "code": 0,
        "message": "ok",
        "data": admin_service.admin_search_orders(db, orderNo, passengerName, flightDate, status),
    }


@router.post("/orders/{order_no}/handle")
def handle_order(order_no: str, payload: AdminHandleIn, admin: AdminUser = Depends(get_current_admin),
                 db: Session = Depends(get_db)):
    data = admin_service.admin_handle_order(db, admin, order_no, payload.action, payload.remark)
    return {"code": 0, "message": "订单处置完成", "data": data}
