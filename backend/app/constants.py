"""错误码、提示语、业务枚举集中管理，与需求文档中的中文文案一一对应。"""

# ============ 错误码与提示语 ============
ERRORS: dict[int, str] = {
    # 注册 UR-01 ~ UR-06
    1001: "用户名不能为空",
    1002: "用户名不能由纯数字组成，请重新输入",
    1003: "用户名不能由数字开头，请重新输入",
    1004: "用户名长度必须至少为4个字符",
    1005: "用户名不能超过8位，请重新输入",
    1006: "该用户名已被注册",
    1007: "密码为8～20位，且需同时包含字母与数字",
    1008: "两次输入的密码不一致，请重新输入",
    1009: "请选择安全问题并填写答案",
    1010: "密码不能与用户名相同",
    1011: "密码不能为连续或重复字符，请重新设置",
    1012: "用户名只能由字母和数字组成，请重新输入",
    1013: "安全问题答案长度须为2～30位",
    # 登录 LR-01 ~ LR-14
    1101: "请输入用户名",
    1102: "请输入密码",
    1103: "用户名不能由纯数字组成，请重新输入",
    1104: "用户名不能由数字开头，请重新输入",
    1105: "密码错误，请重试",
    1106: "密码错误次数过多，账号已锁定，请15分钟后重试",
    # 安全问题与密码重置 UR-07 ~ UR-13
    1201: "该用户名不存在",
    1202: "安全问题答案错误，请重新输入",
    1203: "尝试次数过多，请稍后再试",
    1204: "密码为8～20位，且需同时包含字母与数字",
    1205: "新密码不能与当前密码相同，请重新设置",
    # 订单 OR-01 ~ OR-27
    3001: "此日期后的航班日期有效{}",
    3002: "没有该客户提交的订单，请重新输入",
    3003: "找不到任何订单，请重试",
    3004: "订单号不存在",
    3005: "该订单不支持修改，如需变更请先取消后重新预订",
    3006: "订单号不可修改",
    3007: "单次最多可预订9张机票",
    3008: "航班日期格式不正确，请按mm/dd/yy输入",
    3009: "起点与终点不能为同一城市，请重新选择",
    3010: "城市不存在或已停用，请重新选择",
    3011: "该航线不存在该航班，请重新选择",
    3012: "舱位类型无效，请重新选择",
    3013: "请输入乘机人姓名",
    3014: "该航班余票不足，请调整票数或选择其他航班",
    3015: "订单已被其他操作更新，请刷新后重试",
    3016: "订单当前状态不可取消",
    # 管理端
    5001: "管理员账号或密码错误",
    5002: "管理员账号已停用",
    5003: "无权限执行该操作",
    5004: "城市编码已存在",
    5005: "航班号已存在",
    # 通用
    401: "未登录或登录已过期",
    500: "系统繁忙，请稍后再试",
}

AUTH_ERROR_CODE = 401
FORBIDDEN_ERROR_CODE = 403

# ============ 订单状态 ============
ORDER_STATUS = {
    "TICKETED": "已出票",
    "DONE": "已完成",
    "CANCELLED": "已取消",
}
# 状态机：每个状态允许流转到的下一个状态集合
ORDER_STATE_TRANSITIONS: dict[str, list[str]] = {
    "TICKETED": ["DONE", "CANCELLED"],
    "DONE": [],
    "CANCELLED": [],
}

# 状态流转动作
ACTION_CREATE = "CREATE"
ACTION_UPDATE = "UPDATE"
ACTION_CANCEL = "CANCEL"
ACTION_AUTO_DONE = "AUTO_DONE"
ACTION_ADMIN_CANCEL = "ADMIN_CANCEL"

# 操作人类型
OPERATOR_USER = "USER"
OPERATOR_SYSTEM = "SYSTEM"
OPERATOR_ADMIN = "ADMIN"

# ============ 舱位 ============
SEAT_CLASSES = ["ECONOMY", "BUSINESS", "FIRST"]
SEAT_CLASS_LABELS = {"ECONOMY": "经济舱", "BUSINESS": "商务舱", "FIRST": "头等舱"}
# 舱位 → 航班表价格字段
SEAT_PRICE_FIELD = {"ECONOMY": "price_economy", "BUSINESS": "price_business", "FIRST": "price_first"}

# ============ 预设安全问题 ============
SECURITY_QUESTION_PRESETS = [
    "您母亲的名字是？",
    "您的小学校名是？",
    "您最喜欢的城市是？",
    "您的第一辆车品牌是？",
    "您最好的朋友名字是？",
]

# ============ Redis Key 前缀 ============
KEY_LOGIN_FAIL = "login:fail:{}"
KEY_TOKEN_BLACKLIST = "token:blacklist:{}"
KEY_RESET_FAIL = "reset:{}"
KEY_ORDER_SEQ = "order:seq:{}"


def message(code: int, **kwargs) -> str:
    msg = ERRORS.get(code, ERRORS[500])
    try:
        return msg.format(**kwargs) if kwargs else msg
    except (KeyError, IndexError):
        return msg
