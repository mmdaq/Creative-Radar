"""
Creative Radar — 配置

加载 .env 文件的配置（未提供时使用内置默认值）。
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 基础
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # AI
    AI_PROVIDER: str = "lmstudio"
    AI_BASE_URL: str = "http://127.0.0.1:1234/v1"
    AI_API_KEY: str = "lm-studio"
    AI_MODEL: str = "Qwen"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 2048

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/creative_radar.db"

    # 数据源
    SOURCE_PINTEREST: bool = True
    SOURCE_BEHANCE: bool = True
    SOURCE_DRIBBBLE: bool = True
    SOURCE_YOUTUBE: bool = True
    SOURCE_BILIBILI: bool = True
    SOURCE_TOPYS: bool = False

    # 邮件
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 465
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: str | None = None
    EMAIL_TO: str | None = None
    DAILY_SEND_TIME: str = "08:00"
    DAILY_COUNT: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
