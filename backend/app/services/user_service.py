from sqlalchemy.orm import Session

from .. import constants, validators
from ..exceptions import BizException
from ..models import User
from ..security import create_customer_token, hash_password
from .auth_service import clear_login_fail


def register(db: Session, username: str, password: str, confirm_password: str,
             security_question: str, security_answer: str) -> dict:
    """注册（UR-01 ~ UR-06）：校验通过后创建账号并自动登录，返回令牌。"""
    code = validators.validate_username_register(username)
    if code:
        raise BizException(code)
    code = validators.validate_password_register(password, username)
    if code:
        raise BizException(code)
    if password != confirm_password:
        raise BizException(1008)
    if security_question not in constants.SECURITY_QUESTION_PRESETS or not security_answer.strip():
        raise BizException(1009)
    code = validators.validate_security_answer(security_answer)
    if code:
        raise BizException(code)
    exists = db.query(User).filter(User.username == username).first()
    if exists:
        raise BizException(1006)

    user = User(
        username=username,
        password_hash=hash_password(password),
        security_question=security_question,
        security_answer_hash=hash_password(validators.normalize_answer(security_answer)),
    )
    db.add(user)
    db.flush()
    token, expires_at = create_customer_token(user.id, user.username, user.token_version)
    db.commit()
    return {"token": token, "expiresAt": expires_at, "username": user.username}


def me(db: Session, user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "securityQuestion": user.security_question,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
    }
