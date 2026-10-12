"""
Creative Radar — 空路由模块（占位）
"""
from fastapi import APIRouter

"""
Creative Radar — 收藏 API 模块
"""
from fastapi import APIRouter
from backend.app.database.database import get_db
from backend.app.database.models import Favorite

router = APIRouter()


@router.get("/")
def get_favorites():
    """获取所有收藏。"""
    db = next(get_db())
    try:
        favorites = db.query(Favorite).all()
        return {
            "favorites": [
                {
                    "id": f.id,
                    "item_id": f.item_id,
                    "user": f.user,
                    "created_at": f.created_at.isoformat(),
                }
                for f in favorites
            ],
            "total": len(favorites),
        }
    finally:
        db.close()


@router.post("/")
def toggle_favorite(item_id: str, user: str = "default"):
    """添加或取消收藏。"""
    db = next(get_db())
    try:
        # 检查是否已存在
        existing = db.query(Favorite).filter(Favorite.item_id == item_id).first()
        if existing:
            db.delete(existing)
            db.commit()
            return {"status": "removed", "item_id": item_id}
        else:
            fav = Favorite(item_id=item_id, user=user)
            db.add(fav)
            db.commit()
            return {"status": "added", "item_id": item_id}
    finally:
        db.close()
