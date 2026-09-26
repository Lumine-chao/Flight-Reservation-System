from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    db_url: str = "mysql+pymysql://flight:flight123456@127.0.0.1:3306/flight_reservation?charset=utf8mb4"
    # 留空时使用内存缓存（本地无 Redis 演示）；Docker 部署时注入 redis://redis:6379/0
    redis_url: str = ""
    force_memory_cache: bool = False

    customer_jwt_secret: str = "flight-customer-secret-change-me"
    admin_jwt_secret: str = "flight-admin-secret-change-me"
    jwt_expire_hours: int = 2

    login_fail_limit: int = 4
    lock_minutes: int = 15
    reset_fail_limit: int = 3

    auto_done_interval_seconds: int = 300

    cors_origins: str = "*"


settings = Settings()
