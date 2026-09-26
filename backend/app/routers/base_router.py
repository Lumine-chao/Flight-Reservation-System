from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..services import flight_service

router = APIRouter(prefix="/api", tags=["基础数据与航班"])


@router.get("/base/cities")
def cities(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": flight_service.list_cities(db)}


@router.get("/flights")
def flights(fromCity: str = Query(...), toCity: str = Query(...),
            user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": flight_service.search_flights(db, fromCity, toCity)}


@router.get("/flights/{flight_no}")
def flight_detail(flight_no: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": flight_service.flight_detail(db, flight_no)}
