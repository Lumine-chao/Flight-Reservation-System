from fastapi import Depends, Header
from sqlalchemy.orm import Session

from . import constants
from .config import settings
from .database import get_db
from .exceptions import AuthException, BizException
from .models import AdminUser, User
from .redis_client import get_kv
from .security import decode_token


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:].strip()


def _auth_fail():
    raise AuthException(constants.ERRORS[constants.AUTH_ERROR_CODE])


def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    token = parse_bearer(authorization)
    if not token:
        _auth_fail()
    try:
        payload = decode_token(token, settings.customer_jwt_secret)
    except Exception:
        _auth_fail()
    if payload.get("type") != "customer":
        _auth_fail()
    if get_kv().get(constants.KEY_TOKEN_BLACKLIST.format(payload["jti"])):
        _auth_fail()
    user = db.get(User, int(payload["sub"]))
    if not user or user.status != 1:
        _auth_fail()
    # 密码重置后 token_version 递增，旧令牌全部失效（UR-13）
    if int(payload.get("ver", 0)) != user.token_version:
        _auth_fail()
    return user


def get_current_admin(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> AdminUser:
    token = parse_bearer(authorization)
    if not token:
        _auth_fail()
    try:
        payload = decode_token(token, settings.admin_jwt_secret)
    except Exception:
        _auth_fail()
    if payload.get("type") != "admin":
        _auth_fail()
    if get_kv().get(constants.KEY_TOKEN_BLACKLIST.format(payload["jti"])):
        _auth_fail()
    admin = db.get(AdminUser, int(payload["sub"]))
    if not admin or admin.status != 1:
        _auth_fail()
    return admin


def order_not_found():
    """越权或订单不存在统一提示，不泄露订单存在性（OR-14、BR-18）。"""
    raise BizException(3004, http_status=403)
