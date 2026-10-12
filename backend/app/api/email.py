"""
Creative Radar — 邮件 API 模块

邮件发送与管理接口。
"""
from fastapi import APIRouter
from backend.app.services.email import email_service


router = APIRouter()


@router.get("/status")
def email_status():
    """返回邮件配置状态。"""
    return {
        "enabled": email_service.is_enabled(),
        "smtp_host": email_service.smtp_host,
        "smtp_port": email_service.smtp_port,
        "email_from": email_service.email_from,
        "email_to": email_service.email_to,
    }


@router.post("/test")
async def test_email():
    """测试邮件发送。"""
    from backend.app.services.email import email_service

    success = await email_service.send_mail(
        subject="🔥 Creative Radar｜测试邮件",
        body="这是一封测试邮件。",
    )
    return {"status": "success" if success else "failed"}


@router.post("/send-digest")
async def send_daily_digest():
    """手动触发每日摘要邮件发送（用于管理后台）。"""
    from backend.app.scheduler.daily import scheduler

    success = await scheduler.send_daily_email()
    return {"status": "success" if success else "failed"}


@router.get("/digest-preview")
async def get_daily_digest_preview():
    """获取每日摘要邮件预览（仅展示内容，不发送）。"""
    from backend.app.scheduler.daily import scheduler

    items = await scheduler.get_today_items(limit=10)
    trends = await scheduler.get_daily_trends(items)
    recommendation = await scheduler.build_daily_recommendation(items)

    return {
        "subject": email_service._build_subject(items),
        "preview": email_service.render_template(items, trends, recommendation),
    }
