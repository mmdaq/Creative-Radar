"""
Creative Radar — 采集 API 模块

数据采集管理接口。
"""
from fastapi import APIRouter
from backend.app.collectors import base, rss
from backend.app.database.database import get_db

router = APIRouter()


@router.get("/sources")
def list_sources():
    """返回当前可用的采集源列表。"""
    sources = []
    for name, collector_cls in [
        ("youtube", rss.RSSCollector),
        ("mozilla_hacks", rss.RSSCollector),
        ("smashing", rss.RSSCollector),
        ("behance", base.BehanceCollector),
        ("dribbble", base.DribbbleCollector),
        ("bilibili", base.BilibiliCollector),
        ("pinterest", base.PinterestCollector),
        ("topys", base.TopysCollector),
    ]:
        sources.append({
            "name": name,
            "class": collector_cls.__name__,
            "enabled": collector_cls().enabled,
        })
    return {"sources": sources}


@router.post("/run")
async def run_collect():
    """手动触发采集任务。"""
    from backend.app.services.crawl import crawl_all

    try:
        results = await crawl_all()
        return {
            "status": "success",
            "collected": results["collected"],
            "saved": results["saved"],
            "sources": results["sources"],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/items")
def get_items():
    """获取所有采集项（用于列表展示）。"""
    db = next(get_db())
    try:
        from .items import list_items
        return list_items()
    finally:
        db.close()


@router.post("/collect")
async def trigger_collect():
    """触发一次完整采集（用于管理后台）。"""
    from backend.app.services.crawl import crawl_all

    results = await crawl_all()
    return {
        "status": "success",
        "message": f"采集完成：{results['collected']} 条，保存 {results['saved']} 条",
        "results": results,
    }
