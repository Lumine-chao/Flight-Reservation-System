# -*- coding: utf-8 -*-
"""一次性迁移：城市体系升级（20 城 -> 350 城 + 省份字段）。

- 给 city 表补充 province 列（若缺失）
- 重建业务基础数据（城市/航班按新种子；用户与管理账号保留）
运行：python -m sql.migrate  （在 backend 目录下）
"""
import sys


def main():
    sys.path.insert(0, r"e:\项目1\1\flight-reservation\backend")
    from sqlalchemy import text

    from app.database import SessionLocal, engine
    from app.seed import init_schema, seed_if_empty

    init_schema()

    with engine.connect() as conn:
        cols = {row[0] for row in conn.execute(text("SHOW COLUMNS FROM city"))}
    if "province" not in cols:
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE city ADD COLUMN `province` VARCHAR(64) NOT NULL DEFAULT '' AFTER `city_name`"
            ))
        print("已补充 city.province 列")
    else:
        print("city.province 列已存在")

    seed_if_empty()

    with SessionLocal() as db:
        total = db.execute(text("SELECT COUNT(*) FROM city")).scalar()
        prov = db.execute(text("SELECT COUNT(DISTINCT province) FROM city")).scalar()
        flights = db.execute(text("SELECT COUNT(*) FROM flight")).scalar()
        print(f"迁移完成：城市 {total} 个、省份/地区 {prov} 个、航班 {flights} 条")


if __name__ == "__main__":
    main()
