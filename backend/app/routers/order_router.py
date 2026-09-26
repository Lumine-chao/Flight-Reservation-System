from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import OrderCreateIn, OrderUpdateIn
from ..services import order_service

router = APIRouter(prefix="/api/orders", tags=["订单"])


@router.post("")
def create_order(payload: OrderCreateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = order_service.create_order(db, user.id, payload)
    return {"code": 0, "message": "订单创建成功", "data": data}


@router.get("")
def list_orders(status: str | None = Query(None), user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": order_service.list_orders(db, user.id, status)}


@router.get("/search")
def search_orders(orderNo: str | None = Query(None), passengerName: str | None = Query(None),
                  flightDate: str | None = Query(None), user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return {
        "code": 0,
        "message": "ok",
        "data": order_service.search_orders(db, user.id, orderNo, passengerName, flightDate),
    }


@router.get("/{order_no}")
def order_detail(order_no: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": order_service.get_order_detail(db, user.id, order_no)}


@router.put("/{order_no}")
def update_order(order_no: str, payload: OrderUpdateIn, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return {"code": 0, "message": "订单更新成功", "data": order_service.update_order(db, user.id, order_no, payload)}


@router.post("/{order_no}/cancel")
def cancel_order(order_no: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = order_service.cancel_order(db, user.id, order_no)
    return {"code": 0, "message": "订单已取消", "data": data}
