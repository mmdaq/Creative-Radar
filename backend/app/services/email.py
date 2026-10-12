"""
Creative Radar — 邮件发送服务

基于 aiosmtplib 实现 SMTP 邮件发送。
支持 QQ/163/Gmail/Outlook/企业邮箱。
"""
import asyncio
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
EMAIL_TEMPLATE_PATH = PROJECT_ROOT / "email" / "daily_digest.html"

# 导入全局配置
from backend.app.config import settings

try:
    from aiosmtplib import SMTP
    from aiosmtplib.errors import SMTPException
except ImportError:
    SMTP = smtplib.SMTP
    SMTPException = smtplib.SMTPException


class EmailService:
    """邮件发送服务。"""

    def __init__(self, settings: Any):
        self.enabled = settings.EMAIL_ENABLED
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_to = settings.EMAIL_TO
        self.daily_time = settings.DAILY_SEND_TIME

    def is_enabled(self) -> bool:
        """检查邮件是否已启用。"""
        return self.enabled and bool(self.smtp_host and self.email_to)

    def render_template(self, items: list[dict], trends: list[str], recommendation: str) -> str:
        """渲染邮件模板。"""
        from datetime import datetime

        now = datetime.now()
        today_date = now.strftime("%Y年%m月%d日")

        # 取前10条
        top_items = items[:10]

        # 读模板
        with open(EMAIL_TEMPLATE_PATH, encoding="utf-8") as f:
            template = f.read()

        # 替换变量
        rendered = template.replace("{today_date}", today_date)
        rendered = rendered.replace("{items}", str(top_items))
        rendered = rendered.replace("{trends}", str(trends))
        rendered = rendered.replace("{recommendation}", recommendation or "")

        return rendered

    async def send_mail(self, subject: str, body: str, items: list[dict] | None = None) -> bool:
        """
        发送邮件。
        如果邮件配置未启用，直接返回 False。
        """
        if not self.is_enabled():
            return False

        try:
            message = EmailMessage()
            message["From"] = self.email_from
            message["To"] = self.email_to
            message["Subject"] = subject
            message.set_content(body)  # 纯文本内容

            # 如果启用了 HTML 模板，添加 HTML 版本
            if items is not None:
                html_body = self.render_template(items, [], "")
                message.add_alternative(html_body, subtype="html")

            # 异步发送
            await SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                timeout=30,
            ).send_message(message)

            return True

        except Exception as e:
            print(f"[邮件] 发送失败: {e}")
            return False

    async def send_daily_digest(
        self,
        items: list[dict],
        trends: list[str] | None = None,
        recommendation: str | None = None,
    ) -> bool:
        """
        发送每日摘要邮件。
        """
        if not self.is_enabled():
            return False

        subject = self._build_subject(items)
        body = self.render_template(items or [], trends or [], recommendation or "")
        return await self.send_mail(subject, body, items)

    def _build_subject(self, items: list[dict]) -> str:
        """构建邮件标题。"""
        from datetime import datetime

        date_str = datetime.now().strftime("%Y-%m-%d")
        count = len(items[:10])
        return f"🔥 Creative Radar｜{date_str}｜今日{count}个值得偷学的创意"


# 单例（使用全局配置实例化）
email_service = EmailService(settings)
