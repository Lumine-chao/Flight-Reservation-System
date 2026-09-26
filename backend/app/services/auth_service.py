from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import constants, validators
from ..config import settings
from ..exceptions import AuthException, BizException
from ..models import User
from ..redis_client import get_kv
from ..security import (
    check_password,
    create_customer_token,
    decode_token,
    hash_password,
)

LOCK_KEY_TTL = settings.lock_minutes * 60


def clear_login_fail(db: Session, user: User):
    """登录成功或解锁时清零 Redis 计数与数据库 fail_count、locked_until。"""
    get_kv().delete(constants.KEY_LOGIN_FAIL.format(user.username))
    user.fail_count = 0
    user.locked_until = None


def login(db: Session, username: str, password: str) -> dict:
    """登录（LR-01 ~ LR-14）：按「用户名为空 → 密码为空 → 用户名格式 → 锁定状态 → 密码比对」顺序校验。"""
    code = validators.validate_username_login(username)
    if code:
        raise BizException(code)
    if not password:
        raise BizException(1102)

    user = db.query(User).filter(User.username == username).first()
    kv = get_kv()
    fail_key = constants.KEY_LOGIN_FAIL.format(username)

    # 锁定到期后自动解锁：清空锁定状态与失败计数
    if user and user.locked_until and user.locked_until <= datetime.now():
        clear_login_fail(db, user)

    # 锁定期间一律拒绝登录（LR-13）
    if user and user.locked_until and user.locked_until > datetime.now():
        remain_seconds = int((user.locked_until - datetime.now()).total_seconds())
        minutes = max(1, round(remain_seconds / 60))
        raise BizException(1107, f"账号已锁定，请{minutes}分钟后重试", data={"remainSeconds": remain_seconds})

    # 用户名不存在时仅 Redis 计数、不回写数据库，并统一按密码错误提示（避免账号枚举）
    if not user:
        if kv.get(fail_key) is None:
            kv.set(fail_key, 0, ex=LOCK_KEY_TTL)
        kv.incr(fail_key)
        kv.expire(fail_key, LOCK_KEY_TTL)
        raise BizException(1105, data={"failCount": None, "remainTimes": None})

    if kv.get(fail_key) is None and user.fail_count:
        kv.set(fail_key, user.fail_count, ex=LOCK_KEY_TTL)

    if not check_password(password, user.password_hash):
        count = kv.incr(fail_key)
        kv.expire(fail_key, LOCK_KEY_TTL)
        if count >= settings.login_fail_limit:
            # 第 4 次失败：锁定 15 分钟并回写数据库（LR-12）
            user.fail_count = count
            user.locked_until = datetime.now() + timedelta(minutes=settings.lock_minutes)
            db.commit()
            raise BizException(1106)
        raise BizException(1105, data={"failCount": count, "remainTimes": settings.login_fail_limit - count})

    # 登录成功（LR-14）
    clear_login_fail(db, user)
    user.last_login_at = datetime.now()
    db.commit()
    token, expires_at = create_customer_token(user.id, user.username, user.token_version)
    return {"token": token, "expiresAt": expires_at, "username": user.username}


def logout(token: str):
    """登出：令牌加入黑名单并在剩余有效期内拦截（T-03）。"""
    try:
        payload = decode_token(token, settings.customer_jwt_secret)
    except Exception:
        return
    exp = payload.get("exp")
    jti = payload.get("jti")
    if not jti or not exp:
        return
    remain = exp - int(datetime.now().timestamp())
    if remain > 0:
        get_kv().set(constants.KEY_TOKEN_BLACKLIST.format(jti), "1", ex=remain)


def get_security_question(db: Session, username: str) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user or user.status != 1:
        raise BizException(1201)
    return {"securityQuestion": user.security_question}


def reset_password(db: Session, username: str, answer: str, new_password: str) -> str:
    """安全问题重置密码（UR-07 ~ UR-13）。"""
    kv = get_kv()
    reset_key = constants.KEY_RESET_FAIL.format(username)
    if kv.get(reset_key) == "locked":
        raise BizException(1203)

    user = db.query(User).filter(User.username == username).first()
    if not user or user.status != 1:
        raise BizException(1201)

    # 答案比对：去除首尾空格并转大写（UR-10）
    if not check_password(validators.normalize_answer(answer), user.security_answer_hash):
        if kv.get(reset_key) is None:
            kv.set(reset_key, 0)
        count = kv.incr(reset_key)
        if count >= settings.reset_fail_limit:
            # 连续答错 3 次：当日禁止重置（UR-11），TTL 至自然日 24:00
            kv.set(reset_key, "locked", ex=_seconds_until_midnight())
            raise BizException(1203)
        kv.expire(reset_key, _seconds_until_midnight())
        raise BizException(1202, data={"remainTimes": settings.reset_fail_limit - count})

    code = validators.validate_password_reset(new_password, username, user.password_hash, check_password)
    if code:
        raise BizException(code)

    # 重置成功：写入新密码密文，token_version 递增使全部旧令牌失效（UR-13）
    user.password_hash = hash_password(new_password)
    user.token_version += 1
    kv.delete(reset_key)
    db.commit()
    return "密码重置成功，请重新登录"


def refresh(token: str) -> dict:
    """令牌续期（API-16）：临近过期时换取新令牌。"""
    try:
        payload = decode_token(token, settings.customer_jwt_secret)
    except Exception:
        raise AuthException()
    if payload.get("type") != "customer":
        raise AuthException()
    jti = payload.get("jti")
    if jti and get_kv().get(constants.KEY_TOKEN_BLACKLIST.format(jti)):
        raise AuthException()
    new_token, expires_at = create_customer_token(
        int(payload["sub"]), payload.get("username", ""), int(payload.get("ver", 0))
    )
    return {"token": new_token, "expiresAt": expires_at}


def _seconds_until_midnight() -> int:
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(60, int((midnight - now).total_seconds()))
