"""
Creative Radar — 卡片 API 模块
"""
from fastapi import APIRouter
from backend.app.database.database import get_db
from backend.app.database.models import CreativeCard, CreativeItem

router = APIRouter()


@router.get("/")
def get_cards():
    """获取所有卡片。"""
    db = next(get_db())
    try:
        cards = db.query(CreativeCard).all()
        return {
            "cards": [
                {
                    "id": c.id,
                    "item_id": c.item_id,
                    "ai_summary": c.ai_summary,
                    "recommendation": c.recommendation,
                    "creative_core": c.creative_core,
                    "visual_analysis": c.visual_analysis,
                    "creative_tricks": c.creative_tricks,
                    "imitation_method": c.imitation_method,
                    "application": c.application,
                    "ai_prompt": c.ai_prompt,
                }
                for c in cards
            ],
            "total": len(cards),
        }
    finally:
        db.close()


@router.get("/item/{item_id}")
def get_card(item_id: str):
    """获取某个条目的卡片。"""
    db = next(get_db())
    try:
        card = db.query(CreativeCard).filter(CreativeCard.item_id == item_id).first()
        if not card:
            return {"error": "Card not found"}, 404
        return {
            "id": card.id,
            "item_id": card.item_id,
            "ai_summary": card.ai_summary,
            "recommendation": card.recommendation,
            "creative_core": card.creative_core,
            "visual_analysis": card.visual_analysis,
            "creative_tricks": card.creative_tricks,
            "imitation_method": card.imitation_method,
            "application": card.application,
            "ai_prompt": card.ai_prompt,
        }
    finally:
        db.close()
