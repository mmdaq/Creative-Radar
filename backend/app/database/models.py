"""
Creative Radar — 数据库模型

SQLAlchemy 2.0 风格。
底层使用 SQLite（V1.0），未来升级为 PostgreSQL 无需改逻辑模型。
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column


class Base(DeclarativeBase):
    pass


# ── 采集项 ──────────────────────────────────────────
class CreativeItem(Base):
    """一个原始创意条目，来自数据源采集。"""

    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, index=True)
    source_url: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    thumbnail: Mapped[str | None] = mapped_column(String, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, default="en")
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # 处理状态
    status: Mapped[str] = mapped_column(String, default="collected")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    top_candidate: Mapped[bool] = mapped_column(Boolean, default=False)

    # 去重键
    dedup_key: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    cards: Mapped[list["CreativeCard"]] = relationship(back_populates="item", cascade="all, delete-orphan")


# ── 分析卡片 ────────────────────────────────────────
class CreativeCard(Base):
    """AI 分析生成的卡片。"""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    item_id: Mapped[str] = mapped_column(String, ForeignKey("items.id"), unique=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    creative_core: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    creative_tricks: Mapped[str | None] = mapped_column(Text, nullable=True)
    imitation_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    application: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    item: Mapped["CreativeItem"] = relationship(back_populates="cards")


# ── 收藏 ────────────────────────────────────────────
class Favorite(Base):
    """用户收藏。V1.0 无登录，默认单账户。"""

    __tablename__ = "favorites"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    item_id: Mapped[str] = mapped_column(String, ForeignKey("items.id"), index=True)
    user: Mapped[str] = mapped_column(String, default="default")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── 配置 ────────────────────────────────────────────
class Settings(Base):
    """单行配置。"""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    ai_provider: Mapped[str] = mapped_column(String, default="lmstudio")
    ai_base_url: Mapped[str] = mapped_column(String, default="http://127.0.0.1:1234/v1")
    ai_api_key: Mapped[str] = mapped_column(String, default="lm-studio")
    ai_model: Mapped[str] = mapped_column(String, default="Qwen")
    ai_temperature: Mapped[float] = mapped_column(Float, default=0.3)
    ai_max_tokens: Mapped[int] = mapped_column(Integer, default=2048)

    daily_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    smtp_host: Mapped[str | None] = mapped_column(String, nullable=True)
    smtp_port: Mapped[int] = mapped_column(Integer, default=465)
    smtp_user: Mapped[str | None] = mapped_column(String, nullable=True)
    smtp_password: Mapped[str | None] = mapped_column(String, nullable=True)
    email_from: Mapped[str | None] = mapped_column(String, nullable=True)
    email_to: Mapped[str | None] = mapped_column(String, nullable=True)
    daily_count: Mapped[int] = mapped_column(Integer, default=20)
    daily_time: Mapped[str] = mapped_column(String, default="08:00")

    # 数据源开关
    sources: Mapped[dict[str, bool] | None] = mapped_column(JSON, nullable=True)
