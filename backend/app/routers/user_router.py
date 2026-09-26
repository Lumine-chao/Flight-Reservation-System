from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import RegisterIn
from ..services import user_service

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    data = user_service.register(
        db,
        payload.username,
        payload.password,
        payload.confirmPassword,
        payload.securityQuestion,
        payload.securityAnswer,
    )
    return {"code": 0, "message": "注册成功", "data": data}


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": user_service.me(db, user)}
