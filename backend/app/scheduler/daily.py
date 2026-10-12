"""
Creative Radar — 每日邮件调度器

每天 08:00 自动发送每日摘要邮件。
支持 APScheduler 和 Windows 任务计划程序。
"""
import asyncio
from datetime import datetime
from typing import Any

from ..database.database import get_db
from ..database.models import CreativeItem, CreativeCard
from .email import email_service


class DailyEmailScheduler:
    """每日邮件调度器。"""

    def __init__(self):
        self.days_until = 0

    async def get_today_items(self, limit: int = 10) -> list[dict]:
        """
        获取今日精选条目。
        查询顺序：top_candidate = True → score 排序 → 最新创建
        """
        db = next(get_db())
        try:
            query = (
                db.query(CreativeItem)
                .join(CreativeCard)
                .filter(CreativeItem.top_candidate == True)
                .order_by(CreativeItem.score.desc(), CreativeItem.created_at.desc())
                .limit(limit)
            )
            items = query.all()

            # 如果没有精选，则取最近的收集项
            if not items:
                query = (
                    db.query(CreativeItem)
                    .filter(CreativeItem.status == "collected")
                    .order_by(CreativeItem.created_at.desc())
                    .limit(limit)
                )
                items = query.all()

            # 转换为字典
            result = []
            for item in items:
                card = (
                    db.query(CreativeCard)
                    .filter(CreativeCard.item_id == item.id)
                    .first()
                )
                result.append({
                    "id": item.id,
                    "source": item.source,
                    "source_url": item.source_url,
                    "title": item.title or "无标题",
                    "description": item.description or "",
                    "author": item.author or "",
                    "published_at": item.published_at.isoformat() if item.published_at else "",
                    "content_type": item.content_type or "article",
                    "category": item.category or "visual_design",
                    "tags": item.tags or [],
                    "thumbnail": item.thumbnail or "",
                    "media_url": item.media_url or "",
                    "language": item.language or "en",
                    "raw": item.raw or {},
                    "status": item.status,
                    "score": item.score,
                    "top_candidate": item.top_candidate,
                    "dedup_key": item.dedup_key or "",
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                    "recommendation": card.recommendation or "",
                    "creative_analysis": card.creative_analysis or "",
                    "imitation_method": card.imitation_method or "",
                    "ai_prompt": card.ai_prompt or "",
                })
            return result
        finally:
            db.close()

    async def get_daily_trends(self, items: list[dict]) -> list[str]:
        """从今日条目中提取趋势标签。"""
        tags = set()
        for item in items:
            for tag in item.get("tags", []):
                if tag:
                    tags.add(tag)
        return sorted(tags)[:10]

    async def build_daily_recommendation(self, items: list[dict]) -> str:
        """生成每日推荐语（实际实现中可接入 AI 分析）。"""
        if not items:
            return "今天暂无精选创意，欢迎继续关注！"

        # 简单推荐：取评分最高的前3条，生成一句话推荐
        top_items = sorted(
            items,
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:3]

        lines = []
        for item in top_items:
            title = item.get("title", "未命名")
            score = item.get("score", 0)
            lines.append(f"★ {score:.0f}分：{title}")

        return "今日最值得尝试：\n" + "\n".join(lines)

    async def send_daily_email(self, delay_minutes: int = 0) -> bool:
        """
        发送每日摘要邮件。
        delay_minutes: 延迟发送的分钟数（用于测试）
        """
        import asyncio
        from datetime import datetime, timedelta

        # 计算下次发送时间
        now = datetime.now()
        next_time = now + timedelta(minutes=delay_minutes or 0)

        print(f"[邮件] 下次发送: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 1. 获取精选条目
            items = await self.get_today_items(limit=20)

            if not items:
                print("[邮件] 暂无精选条目，跳过发送")
                return False

            # 2. 生成趋势和推荐
            trends = await self.get_daily_trends(items)
            recommendation = await self.build_daily_recommendation(items)

            # 3. 发送邮件
            success = await email_service().send_daily_digest(
                items=items,
                trends=trends,
                recommendation=recommendation,
            )

            if success:
                print(f"[邮件] 发送成功！共 {len(items)} 条，收件人: {email_service().email_to}")
            else:
                print(f"[邮件] 发送失败或未启用")

            return success

        except Exception as e:
            print(f"[邮件] 发送异常: {e}")
            return False


# 全局调度器实例
scheduler = DailyEmailScheduler()


async def daily_send_task():
    """每日邮件发送任务入口（APScheduler 调度使用）。"""
    await scheduler.send_daily_email()


if __name__ == "__main__":
    # 测试入口
    asyncio.run(scheduler.send_daily_email())
