# -*- coding: utf-8 -*-
"""为无航线的有机场城市生成到枢纽的往返航线。

产出 backend/sql/flights_fill.py，供 seed.py 合并使用。
票价与时长统一由 sql/pricing.py 按真实距离计算，本文件只生成航线。

枢纽选择：优先挂本省省会/枢纽；若该城市距本省枢纽不足 250 公里
（现实中不存在这种短途航班，如昌吉→乌鲁木齐、佛山→广州），
则改挂到最近的大型航空枢纽（北京/上海/广州/成都/乌鲁木齐等），
且距离不少于 700 公里。
"""
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from sql.cities_data import PROVINCE_CITIES
from sql.pricing import duration_min, haversine_km

# 各省枢纽（须是已被跨省主干线覆盖的城市）
HUB = {
    "北京市": "beijing", "上海市": "shanghai", "天津市": "tianjin", "重庆市": "chongqing",
    "河北省": "shijiazhuang", "山西省": "taiyuan", "内蒙古自治区": "huhehaote",
    "辽宁省": "shenyang", "吉林省": "changchun", "黑龙江省": "haerbin",
    "江苏省": "nanjing", "浙江省": "hangzhou", "安徽省": "hefei",
    "福建省": "fuzhou", "江西省": "nanchang", "山东省": "jinan",
    "河南省": "zhengzhou", "湖北省": "wuhan", "湖南省": "changsha",
    "广东省": "guangzhou", "广西壮族自治区": "nanning", "海南省": "haikou",
    "四川省": "chengdu", "贵州省": "guiyang", "云南省": "kunming",
    "西藏自治区": "lasa", "陕西省": "xian", "甘肃省": "lanzhou",
    "青海省": "xining", "宁夏回族自治区": "yinchuan", "新疆维吾尔自治区": "urumqi",
    "台湾省": "taibei", "香港特别行政区": "xianggang", "澳门特别行政区": "aomen",
}

# 大型枢纽：短途城市改挂这些（均为已被主干线覆盖的城市）
MAJOR_HUBS = ["beijing", "shanghai", "guangzhou", "chengdu",
              "urumqi", "haerbin", "kunming", "xian", "shenzhen", "hangzhou"]

MIN_FEEDER_KM = 250   # 距本省枢纽短于此值，不设"到省会"支线
MAJOR_MIN_KM = 700    # 改挂大型枢纽时的最小距离

# 各省主力航司（真实存在，用于替换原虚构的"祥云航空"）
PROV_AIRLINES = {
    "北京市": ["中国国际航空", "中国联合航空"],
    "上海市": ["吉祥航空", "春秋航空", "中国东方航空"],
    "天津市": ["天津航空", "中国国际航空"],
    "重庆市": ["西部航空", "重庆航空"],
    "河北省": ["河北航空", "中国东方航空"],
    "山西省": ["中国东方航空", "中国国际航空"],
    "内蒙古自治区": ["天骄航空", "中国国际航空"],
    "辽宁省": ["中国南方航空", "中国国际航空"],
    "吉林省": ["中国南方航空", "中国国际航空"],
    "黑龙江省": ["龙江航空", "中国南方航空"],
    "江苏省": ["中国东方航空", "吉祥航空"],
    "浙江省": ["长龙航空", "中国东方航空"],
    "安徽省": ["中国东方航空", "中国国际航空"],
    "福建省": ["厦门航空", "福州航空"],
    "江西省": ["江西航空", "中国东方航空"],
    "山东省": ["山东航空", "中国东方航空"],
    "河南省": ["中国南方航空", "中国东方航空"],
    "湖北省": ["中国东方航空", "中国南方航空"],
    "湖南省": ["湖南航空", "中国南方航空"],
    "广东省": ["中国南方航空", "深圳航空"],
    "广西壮族自治区": ["北部湾航空", "中国南方航空"],
    "海南省": ["海南航空", "中国南方航空"],
    "四川省": ["四川航空", "成都航空"],
    "贵州省": ["多彩贵州航空", "中国南方航空"],
    "云南省": ["昆明航空", "祥鹏航空", "瑞丽航空"],
    "西藏自治区": ["西藏航空", "中国国际航空"],
    "陕西省": ["长安航空", "中国东方航空"],
    "甘肃省": ["中国东方航空", "中国国际航空"],
    "青海省": ["中国东方航空", "中国国际航空"],
    "宁夏回族自治区": ["中国东方航空", "中国国际航空"],
    "新疆维吾尔自治区": ["乌鲁木齐航空", "天津航空", "中国南方航空"],
    "台湾省": ["中华航空", "长荣航空"],
    "香港特别行政区": ["国泰航空", "香港航空"],
    "澳门特别行政区": ["澳门航空"],
}

DEP_SLOTS = ["07:20", "08:45", "10:10", "11:35", "13:00", "14:25", "15:50", "17:15", "18:40", "20:05"]


def hhmm(mins: int) -> str:
    return f"{mins // 60 % 24:02d}:{mins % 60:02d}"


def pick_hub(city: str, prov: str) -> tuple[str, float, bool]:
    """返回 (枢纽code, 距离km, 是否为改挂)。"""
    prov_hub = HUB.get(prov)
    if prov_hub and prov_hub != city:
        d = haversine_km(city, prov_hub)
        if d >= MIN_FEEDER_KM:
            return prov_hub, d, False
    # 短途：改挂最近的大型枢纽
    best, best_d = None, None
    for m in MAJOR_HUBS:
        if m == city:
            continue
        d = haversine_km(city, m)
        if d < MAJOR_MIN_KM:
            continue
        if best_d is None or d < best_d:
            best, best_d = m, d
    if best is None:
        raise SystemExit(f"{city} 找不到合适枢纽")
    return best, best_d, True


def main():
    seed_path = BACKEND / "app" / "seed.py"
    seed = seed_path.read_text(encoding="utf-8")
    pairs = re.findall(r'\("([a-z0-9\-]+)", "([a-z0-9\-]+)",', seed)
    covered = set()
    for a, b in pairs:
        covered.add(a)
        covered.add(b)

    all_codes = set(PROVINCE_CITIES.keys())
    gap = sorted(all_codes - covered)
    print(f"主干线覆盖 {len(covered)} 城，待补支线 {len(gap)} 城")

    prov_groups: dict[str, list] = {}
    reassigned = []
    for city in gap:
        prov, _name = PROVINCE_CITIES[city]
        hub, km, moved = pick_hub(city, prov)
        prov_groups.setdefault(prov, []).append((city, hub, km))
        if moved:
            reassigned.append((city, prov, hub, km))

    lines = [
        '# -*- coding: utf-8 -*-',
        '"""自动生成：无航线有机场城市到枢纽的往返航线（勿手改）。',
        '票价与时长由 sql/pricing.py 按距离计算。生成脚本：backend/sql/_gen_fill.py"""',
        '',
        'FILL_FLIGHTS = {',
    ]
    total = 0
    for prov in sorted(prov_groups):
        items = sorted(prov_groups[prov], key=lambda x: x[2])
        airlines = PROV_AIRLINES.get(prov, ["中国国际航空", "中国东方航空"])
        lines.append(f"    {prov!r}: [")
        for i, (city, hub, km) in enumerate(items):
            dur = duration_min(km)
            dep = DEP_SLOTS[i % len(DEP_SLOTS)]
            dh, dm = int(dep[:2]), int(dep[3:])
            arr = hhmm(dh * 60 + dm + dur)
            airline = airlines[i % len(airlines)]
            lines.append(f'        ({city!r}, {hub!r}, {dep!r}, {arr!r}, {airline!r}, 120),')
            lines.append(f'        ({hub!r}, {city!r}, {dep!r}, {arr!r}, {airline!r}, 118),')
            total += 2
        lines.append("    ],")
    lines.append("}")
    lines.append("")

    out = BACKEND / "sql" / "flights_fill.py"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"生成 {len(prov_groups)} 省、{total} 条航线 -> {out}")
    print(f"其中因距省会过近改挂大型枢纽的城市 {len(reassigned)} 个：")
    for city, prov, hub, km in reassigned:
        print(f"  {PROVINCE_CITIES[city][1]}({prov}) -> {PROVINCE_CITIES[hub][1]} {km:.0f}km")


if __name__ == "__main__":
    main()
