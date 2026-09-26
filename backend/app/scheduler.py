"""订单状态自动流转定时任务：每日扫描航班日期已过的 TICKETED 订单批量置为 DONE。"""
import asyncio
import logging

from .config import settings
from .database import SessionLocal
from .services.order_service import auto_done_orders

logger = logging.getLogger("uvicorn.error")


async def auto_done_loop():
    while True:
        try:
            with SessionLocal() as db:
                count = auto_done_orders(db)
                if count:
                    logger.info("定时任务：%s 张订单已自动置为已完成", count)
        except Exception:
            logger.exception("定时任务执行失败")
        await asyncio.sleep(settings.auto_done_interval_seconds)
