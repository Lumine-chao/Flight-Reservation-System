from . import constants


class BizException(Exception):
    """业务异常：返回 HTTP 200 + 业务错误码（越权场景使用 http_status=403）。"""

    def __init__(self, code: int, message: str | None = None, http_status: int = 200, data=None):
        self.code = code
        self.message = message or constants.message(code)
        self.http_status = http_status
        self.data = data
        super().__init__(self.message)


class AuthException(Exception):
    """未认证：返回 HTTP 401。"""

    def __init__(self, message: str = "未登录或登录已过期"):
        self.message = message
        super().__init__(message)
