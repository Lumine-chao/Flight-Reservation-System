# -*- coding: utf-8 -*-
"""校验 coords.py 与 cities_data.py 键集一致。"""
import sys
sys.path.insert(0, r"E:\项目1\project2\flight-reservation\backend")
from sql.cities_data import PROVINCE_CITIES, CITY_TOTAL
from sql.coords import CITY_LATLON

cities = set(PROVINCE_CITIES.keys())
coords = set(CITY_LATLON.keys())
print("城市数:", len(cities), " 声明总数:", CITY_TOTAL, " 坐标数:", len(coords))
miss = sorted(cities - coords)
extra = sorted(coords - cities)
print("缺坐标的城市:", miss if miss else "无")
print("多余坐标键:", extra if extra else "无")
bad = [(k, v) for k, v in CITY_LATLON.items() if not (3 <= v[0] <= 54 and 73 <= v[1] <= 136)]
print("坐标越界(不在中国范围):", bad if bad else "无")