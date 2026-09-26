# -*- coding: utf-8 -*-
"""校验航班种子（含自动补齐）引用的城市代码都在城市数据中，且每个有机场城市都有航线。"""
import ast
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from sql.cities_data import PROVINCE_CITIES  # noqa: E402
from sql.flights_fill import FILL_FLIGHTS  # noqa: E402

# 提取 seed.py 中 SEED_FLIGHTS_BY_PROVINCE 字典的值
src = (BACKEND / "app" / "seed.py").read_text(encoding="utf-8")
tree = ast.parse(src)
used = set()
for node in ast.walk(tree):
    if not isinstance(node, ast.Assign):
        continue
    if not (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "SEED_FLIGHTS_BY_PROVINCE"):
        continue
    val = node.value
    if not isinstance(val, ast.Dict):
        continue
    for k, v in zip(val.keys, val.values):
        if isinstance(k, ast.Constant) and isinstance(v, ast.List):
            for el in v.elts:
                if (isinstance(el, ast.Tuple) and len(el.elts) >= 2
                        and isinstance(el.elts[0], ast.Constant)
                        and isinstance(el.elts[1], ast.Constant)):
                    used.add(el.elts[0].value)
                    used.add(el.elts[1].value)
    break

# 合并补齐文件航线
for _prov, routes in FILL_FLIGHTS.items():
    for r in routes:
        used.add(r[0])
        used.add(r[1])

codes = set(PROVINCE_CITIES.keys())
missing = sorted(c for c in used if c not in codes)
print("引用城市代码:", len(used))
print("缺失代码:", missing if missing else "无")

absent = sorted(c for c in codes if c not in used)
print("无任何航线的有机场城市:", len(absent))
if absent:
    for c in absent:
        print("   ", PROVINCE_CITIES[c][0] + "/" + PROVINCE_CITIES[c][1], c)