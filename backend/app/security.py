"""密码加密（BCrypt）与 JWT 令牌签发/校验。"""
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_token(payload: dict, secret: str, expires_hours: int | None = None) -> tuple[str, int]:
    """返回 (token, 过期时间戳秒)。"""
    hours = expires_hours or settings.jwt_expire_hours
    exp = _now_utc() + timedelta(hours=hours)
    body = {
        **payload,
        "jti": uuid.uuid4().hex,
        "iat": _now_utc(),
        "exp": exp,
    }
    token = jwt.encode(body, secret, algorithm="HS256")
    return token, int(exp.timestamp())


def create_customer_token(user_id: int, username: str, token_version: int) -> tuple[str, int]:
    return create_token(
        {"sub": str(user_id), "username": username, "type": "customer", "ver": token_version},
        settings.customer_jwt_secret,
    )


def create_admin_token(admin_id: int, username: str, role: str) -> tuple[str, int]:
    return create_token(
        {"sub": str(admin_id), "username": username, "type": "admin", "role": role},
        settings.admin_jwt_secret,
    )


def decode_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=["HS256"])
