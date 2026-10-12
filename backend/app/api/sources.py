"""
Creative Radar — 空路由模块（占位）
"""
from fastapi import APIRouter

"""
Creative Radar — 数据源 API 模块
"""
from fastapi import APIRouter
from backend.app.collectors import (
    rss,
    behance,
    dribbble,
    bilibili,
    pinterest,
    topys,
)

router = APIRouter()


@router.get("/")
def list_sources():
    """返回当前可用的采集源列表。"""
    sources = [
        {"name": "youtube", "class": "RSSCollector", "enabled": True},
        {"name": "mozilla_hacks", "class": "RSSCollector", "enabled": True},
        {"name": "smashing", "class": "RSSCollector", "enabled": True},
        {"name": "behance", "class": "BehanceCollector", "enabled": False},
        {"name": "dribbble", "class": "DribbbleCollector", "enabled": False},
        {"name": "bilibili", "class": "BilibiliCollector", "enabled": True},
        {"name": "pinterest", "class": "PinterestCollector", "enabled": False},
        {"name": "topys", "class": "TopysCollector", "enabled": True},
    ]
    return {"sources": sources}
