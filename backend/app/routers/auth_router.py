from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, parse_bearer
from ..exceptions import AuthException
from ..models import User
from ..schemas import LoginIn, ResetPasswordIn, SecurityQuestionIn
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    data = auth_service.login(db, payload.username, payload.password)
    return {"code": 0, "message": "登录成功", "data": data}


@router.get("/security-question")
def security_question(username: str, db: Session = Depends(get_db)):
    return {"code": 0, "message": "ok", "data": auth_service.get_security_question(db, username)}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    message = auth_service.reset_password(db, payload.username, payload.securityAnswer, payload.newPassword)
    return {"code": 0, "message": message, "data": None}


@router.post("/logout")
def logout(authorization: str | None = Header(None), user: User = Depends(get_current_user)):
    token = parse_bearer(authorization)
    auth_service.logout(token)
    return {"code": 0, "message": "已退出登录", "data": None}


@router.post("/refresh")
def refresh(authorization: str | None = Header(None)):
    token = parse_bearer(authorization)
    if not token:
        raise AuthException()
    data = auth_service.refresh(token)
    return {"code": 0, "message": "ok", "data": data}
