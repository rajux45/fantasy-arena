from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    env: str = "development"
    app_name: str = "fantasy-arena"
    secret_key: str = "change-me-development-only"
    algorithm: str = "HS256"
    access_token_ttl_min: int = 30
    refresh_token_ttl_days: int = 14

    database_url: str = "postgresql+psycopg://fantasy:fantasy@localhost:5432/fantasy_arena"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    cors_origins: str = "http://localhost:3000,http://localhost:19006"

    pii_encryption_key: str = ""

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    msg91_auth_key: str = ""
    msg91_sender_id: str = "FANTAS"

    digio_client_id: str = ""
    digio_client_secret: str = ""
    digio_base_url: str = "https://ext.digio.in:444"

    roanuz_project_key: str = ""
    roanuz_api_key: str = ""

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_pass: str = ""
    email_from: str = "no-reply@fantasy-arena.example"

    geoip_db_path: str = ""
    sentry_dsn: str = ""

    rg_daily_deposit_limit: int = Field(default=2_500_000)  # paise
    deposit_min_paise: int = 10_000          # ₹100
    deposit_max_paise: int = 10_000_000      # ₹1,00,000
    withdrawal_min_paise: int = 10_000       # ₹100
    withdrawal_max_paise: int = 10_000_000   # ₹1,00,000

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.env.lower() in {"dev", "development", "local"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
