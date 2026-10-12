"""
Creative Radar — Pydantic 数据模型（请求/响应）

用于 API 输入校验与输出序列化。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── 采集项 ──────────────────────────────────────────
class CreativeItemBase(BaseModel):
    source: str
    source_url: str
    title: str | None = None
    description: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    content_type: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    thumbnail: str | None = None
    media_url: str | None = None
    language: str = "en"
    raw: dict[str, Any] | None = None


class CreativeItemCreate(CreativeItemBase):
    pass


class CreativeItemOut(CreativeItemBase):
    id: str
    status: str
    score: float
    top_candidate: bool
    dedup_key: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreativeItemListOut(BaseModel):
    items: list[CreativeItemOut]
    total: int


# ── 分析卡片 ────────────────────────────────────────
class CreativeCardBase(BaseModel):
    ai_summary: str | None = None
    recommendation: str | None = None
    creative_core: str | None = None
    visual_analysis: str | None = None
    creative_tricks: str | None = None
    imitation_method: str | None = None
    application: str | None = None
    ai_prompt: str | None = None


class CreativeCardCreate(CreativeCardBase):
    pass


class CreativeCardOut(CreativeCardBase):
    id: str
    item_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── 收藏 ────────────────────────────────────────────
class FavoriteBase(BaseModel):
    user: str = "default"
    item_id: str


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteOut(FavoriteBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── 配置 ────────────────────────────────────────────
class SettingsBase(BaseModel):
    ai_provider: str = "lmstudio"
    ai_base_url: str = "http://127.0.0.1:1234/v1"
    ai_api_key: str = "lm-studio"
    ai_model: str = "Qwen"
    ai_temperature: float = 0.3
    ai_max_tokens: int = 2048

    daily_enabled: bool = True
    smtp_host: str | None = None
    smtp_port: int = 465
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None
    email_to: str | None = None
    daily_count: int = 20
    daily_time: str = "08:00"

    sources: dict[str, bool] | None = None


class SettingsOut(SettingsBase):
    id: int

    class Config:
        from_attributes = True


class SettingsUpdate(SettingsBase):
    pass
