"""
Creative Radar — 数据列表 API 模块
"""
from fastapi import APIRouter
from backend.app.database.database import get_db
from backend.app.database.models import CreativeItem

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/")
def list_items():
    """获取所有采集项。"""
    db = next(get_db())
    try:
        items = db.query(CreativeItem).order_by(CreativeItem.created_at.desc()).all()
        return {
            "items": [
                {
                    "id": item.id,
                    "source": item.source,
                    "source_url": item.source_url,
                    "title": item.title,
                    "description": item.description,
                    "category": item.category,
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "content_type": item.content_type,
                    "status": item.status,
                    "score": item.score,
                    "top_candidate": item.top_candidate,
                }
                for item in items
            ],
            "total": len(items),
        }
    finally:
        db.close()


@router.get("/today")
def today_items():
    """获取今日精选。"""
    db = next(get_db())
    try:
        from backend.app.scheduler.daily import scheduler
        items = scheduler.get_today_items(limit=20)
        return {"items": items}
    finally:
        db.close()
