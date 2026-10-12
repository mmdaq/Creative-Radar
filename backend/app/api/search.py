"""
Creative Radar — 空路由模块（占位）
"""
from fastapi import APIRouter

"""
Creative Radar — 搜索 API 模块
"""
from fastapi import APIRouter
from backend.app.database.database import get_db
from backend.app.database.models import CreativeItem

router = APIRouter()


@router.get("/")
def search_items(
    q: str = "",
    category: str = "",
    source: str = "",
    date_from: str = "",
    date_to: str = "",
    limit: int = 50,
):
    """搜索创意内容。"""
    db = next(get_db())
    try:
        query = db.query(CreativeItem)

        if q:
            like = f"%{q}%"
            query = query.filter(
                (CreativeItem.title.ilike(like))
                | (CreativeItem.description.ilike(like))
                | (CreativeItem.tags.any().ilike(like))
            )
        if category:
            query = query.filter(CreativeItem.category == category)
        if source:
            query = query.filter(CreativeItem.source == source)
        if date_from:
            query = query.filter(CreativeItem.published_at >= date_from)
        if date_to:
            query = query.filter(CreativeItem.published_at <= date_to)

        items = query.limit(limit).all()

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
                    "tags": item.tags,
                }
                for item in items
            ],
            "total": len(items),
        }
    finally:
        db.close()
