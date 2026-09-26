"""校验规则集中管理：前端即时校验 + 服务端强制校验共用同一套规则描述。"""
import re
from datetime import date, datetime

USERNAME_RE = re.compile(r"^[0-9A-Za-z]{2,8}$")
DATE_INPUT_FORMAT = "%m/%d/%y"


def today() -> date:
    return datetime.now().date()


def format_date(d: date) -> str:
    return d.strftime(DATE_INPUT_FORMAT)


# ============ 用户名 ============
def validate_username_register(username: str | None) -> int | None:
    """注册/密码重置场景的用户名校验，返回错误码或 None。"""
    if not username:
        return 1001
    if username.isdigit():
        return 1002
    if username[0].isdigit():
        return 1003
    if len(username) < 4:
        return 1004
    if len(username) > 8:
        return 1005
    if not USERNAME_RE.fullmatch(username):
        return 1012
    return None


def validate_username_login(username: str | None) -> int | None:
    """登录场景的用户名校验（LR-06、LR-07、LR-03~LR-05 的登录侧口径）。"""
    if not username:
        return 1101
    if username.isdigit():
        return 1103
    if username[0].isdigit():
        return 1104
    return None


# ============ 密码 ============
def _is_consecutive_or_repeated(password: str) -> bool:
    if len(set(password)) < 3:
        return True
    diffs = [ord(password[i + 1]) - ord(password[i]) for i in range(len(password) - 1)]
    if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
        return True
    return False


def validate_password_strength(password: str | None) -> int | None:
    """密码强度：8～20 位且同时包含字母与数字，返回错误码或 None。"""
    if not password:
        return 1007
    if not (8 <= len(password) <= 20):
        return 1007
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return 1007
    return None


def validate_password_register(password: str | None, username: str) -> int | None:
    code = validate_password_strength(password)
    if code:
        return code
    if password == username:
        return 1010
    if _is_consecutive_or_repeated(password):
        return 1011
    return None


def validate_password_reset(new_password: str | None, username: str, current_hash: str, check_password_fn) -> int | None:
    """重置场景：强度（1204）、不能与用户名相同（1010）、不能与当前密码相同（1205）。"""
    code = validate_password_strength(new_password)
    if code:
        return 1204
    if new_password == username:
        return 1010
    if check_password_fn(new_password, current_hash):
        return 1205
    return None


# ============ 安全问题答案 ============
def validate_security_answer(answer: str | None) -> int | None:
    if not answer or not answer.strip():
        return 1009
    if not (2 <= len(answer.strip()) <= 30):
        return 1013
    return None


def normalize_answer(answer: str) -> str:
    """答案比对口径：去除首尾空格并转大写（UR-10）。"""
    return answer.strip().upper()


# ============ 航班日期 ============
def parse_flight_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_INPUT_FORMAT).date()
    except ValueError:
        return None


def validate_flight_date(s: str | None) -> tuple[date | None, int | None]:
    """校验格式（3008）与晚于系统当前日期（3001）。"""
    d = parse_flight_date(s)
    if d is None:
        return None, 3008
    if d <= today():
        return None, 3001
    return d, None


# ============ 起终点 ============
def validate_cities(from_city: str, to_city: str) -> int | None:
    if from_city == to_city:
        return 3009
    return None
