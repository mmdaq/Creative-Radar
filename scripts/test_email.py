"""
Creative Radar — 邮件服务测试

测试邮件发送功能。
用法：
    python -m backend.app.services.email
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.database import init_db, get_db
from backend.app.database.models import CreativeItem
from backend.app.services.email import email_service


def test_email_send():
    """测试邮件发送。"""
    init_db()
    print("数据库初始化完成")

    # 查询今日精选
    db = next(get_db())
    try:
        from backend.app.database.models import CreativeCard
        items = (
            db.query(CreativeItem)
            .join(CreativeCard)
            .filter(CreativeItem.top_candidate == True)
            .order_by(CreativeItem.score.desc())
            .limit(10)
            .all()
        )
    finally:
        db.close()

    if not items:
        print("没有精选条目，无法测试邮件")
        return

    print(f"找到 {len(items)} 条精选条目")

    # 模拟设置
    from backend.app.config import settings

    print(f"\n配置:")
    print(f"  邮件启用: {settings.EMAIL_ENABLED}")
    print(f"  SMTP 主机: {settings.SMTP_HOST}")
    print(f"  SMTP 端口: {settings.SMTP_PORT}")
    print(f"  发件人: {settings.EMAIL_FROM}")
    print(f"  收件人: {settings.EMAIL_TO}")

    if not settings.EMAIL_ENABLED:
        print("\n邮件未启用（查看 .env 文件设置 EMAIL_ENABLED=true）")
        return

    # 构建测试数据
    items_data = []
    for item in items[:10]:
        items_data.append({
            "id": item.id,
            "source": item.source,
            "source_url": item.source_url,
            "title": item.title or "无标题",
            "recommendation": item.description or "",
            "creative_analysis": item.description or "",
            "imitation_method": "模仿步骤1/2/3",
            "thumbnail": item.thumbnail or "",
        })

    trends = ["#设计", "#AI", "#创意"]
    recommendation = "今天最值得尝试：巨型物体 + 微缩人物 + 电影镜头"

    print(f"\n构建邮件:")
    print(f"  标题: {email_service()._build_subject(items_data)}")
    print(f"  收件人: {email_service().email_to}")

    # 执行发送
    success = asyncio.run(email_service().send_daily_digest(
        items=items_data,
        trends=trends,
        recommendation=recommendation,
    ))

    if success:
        print("\n✅ 邮件发送成功！")
    else:
        print("\n❌ 邮件发送失败（请检查 .env 配置）")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_email_send())
