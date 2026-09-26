# -*- coding: utf-8 -*-
"""统一航班计价：按城市间大圆距离计算三舱价格与飞行时长。

    经济舱 = clamp(250 + 0.5 × 公里, 250, 2000)，取整到 10 元
    商务舱 = 经济舱 × 2.7，头等舱 = 经济舱 × 3.5，取整到 10 元
    飞行时长 = 40 分钟 + 公里 / 750 km/h，取整到 5 分钟

主干线与支线全部走这里，保证同距离同价；种子文件只存航线，不存价格。
"""
import math

from sql.coords import CITY_LATLON

EARTH_KM = 6371.0
ECON_BASE = 250.0
ECON_PER_KM = 0.5
ECON_MIN = 250.0
ECON_MAX = 2000.0
BIZ_RATIO = 2.7
FIRST_RATIO = 3.5
CRUISE_KM_PER_MIN = 12.5  # 750 km/h
CLIMB_MIN = 40.0


def haversine_km(a: str, b: str) -> float:
    """两城市间大圆距离（公里）。"""
    lat1, lon1 = CITY_LATLON[a]
    lat2, lon2 = CITY_LATLON[b]
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(h))


def _round10(value: float) -> int:
    return int(round(value / 10.0) * 10)


def price_economy(km: float) -> int:
    return _round10(min(ECON_MAX, max(ECON_MIN, ECON_BASE + ECON_PER_KM * km)))


def price_business(economy: int) -> int:
    return _round10(economy * BIZ_RATIO)


def price_first(economy: int) -> int:
    return _round10(economy * FIRST_RATIO)


def duration_min(km: float) -> int:
    return int(round((CLIMB_MIN + km / CRUISE_KM_PER_MIN) / 5) * 5)
