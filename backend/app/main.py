import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .exceptions import AuthException, BizException
from .routers import admin_router, auth_router, base_router, order_router, user_router
from .scheduler import auto_done_loop
from .seed import init_schema, seed_if_empty

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_schema()
    seed_if_empty()
    task = asyncio.create_task(auto_done_loop())
    yield
    task.cancel()


app = FastAPI(title="航班预订系统", version="1.0", lifespan=lifespan)

origins = ["*"] if settings.cors_origins == "*" else settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(base_router.router)
app.include_router(order_router.router)
app.include_router(admin_router.router)


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )


@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(status_code=401, content={"code": 401, "message": exc.message, "data": None})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("未处理异常: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"code": 500, "message": "系统繁忙，请稍后再试", "data": None})
