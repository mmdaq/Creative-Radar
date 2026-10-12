"""
Creative Radar — 数据库连接与会话管理
"""
import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 项目根目录（两级向上）
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/creative_radar.db",
)

# SQLite 需要检查同一时间的连接
connect_args = {"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator:
    """FastAPI 依赖注入：每个请求一个会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """创建所有表。"""
    from .models import Base

    Base.metadata.create_all(bind=engine)
    print(f"[db] 已初始化，数据库: {DATABASE_URL}")


def reset_db() -> None:
    """删除并重建所有表（仅用于开发调试）。"""
    from .models import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(f"[db] 已重置，数据库: {DATABASE_URL}")
