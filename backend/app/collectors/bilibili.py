"""
Creative Radar — Bilibili 数据源采集器

Bilibili 官方 API（web dynamic feed）。
https://github.com/SocialSisterYi/bilibili-API-collect

抓取 Bilibili 的创意设计、AI、动画、影视、视觉、脑洞、教程内容。
"""
from datetime import datetime
from typing import Any

import requests

from .base import BaseCollector

# 创意设计相关的动态分区
# 关注的 UP 主推荐（可替换为自己的 mid 或使用推荐分区）
DEFAULT_ASPECT_IDS = [1, 2, 3]  # 高质量创意内容
DEFAULT_TYPE = 0  # 默认
DEFAULT_PAGE = 1


class BilibiliCollector(BaseCollector):
    """Bilibili 数据源采集器。"""

    name = "bilibili"
    supported_types = ["video", "image", "article"]
    update_frequency = "daily"

    DYNAMIC_URL = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed"

    def __init__(
        self,
        cookies: dict[str, str] | None = None,
        aspect_ids: list[int] | None = None,
        max_items: int = 100,
    ):
        self.cookies = cookies or {}
        self.aspect_ids = aspect_ids or DEFAULT_ASPECT_IDS
        self.max_items = max_items

    @property
    def enabled(self) -> bool:
        """默认启用（Bilibili 官方 API 公开）。"""
        return True

    def fetch(self, max_items: int = 100) -> list[dict]:
        """
        抓取 Bilibili 动态。
        注意：需要 cookies 才能获取完整数据，否则可能有限制。
        """
        # 这里使用公开的 feed 接口
        # 实际使用时可以添加 cookies 参数提升质量
        params = {
            "host_mid": 0,
            "type": DEFAULT_TYPE,
            "page": DEFAULT_PAGE,
            "tab": "all",
            "sort": "default",
            "jsonp": "jsonp",
        }

        try:
            resp = requests.get(
                self.DYNAMIC_URL,
                params=params,
                timeout=30,
                cookies=self.cookies,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise ValueError(f"Bilibili 采集失败: {e}")

        items = []
        items_data = data.get("data", {}).get("items", [])
        for item in items_data[: max_items]:
            items.append(self._parse_dynamic(item))
        return items

    def _parse_dynamic(self, item: dict[str, Any]) -> dict[str, Any]:
        """将 Bilibili 动态解析为统一格式。"""
        # 动态结构
        info = item.get("info", {})
        items = item.get("items", [])

        title = info.get("title", info.get("desc", ""))
        author = info.get("ups", [{}])[0].get("name", "") if info.get("ups") else ""

        # 发布时间
        pub_time = info.get("pub_text", "")
        published_at = None
        if pub_time:
            try:
                published_at = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
            except Exception:
                pass

        # 内容（斜体/段落等）
        content = ""
        if items:
            if items[0].get("type") == "rich_text":
                rich = items[0].get("rich_text", {})
                ogp = rich.get("ogp", [])
                content = " ".join(
                    [seg.get("text", "") for seg in ogp if seg.get("type") == "text"]
                )
            elif items[0].get("type") == "animated_image":
                content = "动图"

        # 描述
        description = info.get("desc", "")
        if not description and content:
            description = content[:500]

        # 链接
        arclink = info.get("arclink", "")
        link = arclink or info.get("share_url", "")

        # 图片（B站动态中的图片）
        thumbnail = None
        media_urls = []
        if items:
            if items[0].get("type") in ("image", "animated_image"):
                image_list = items[0].get("pic", [])
                if image_list:
                    thumbnail = image_list[0]
                    media_urls = [img.get("img_src", img.get("pic", "")) for img in image_list]

        # 标签（B站动态的标签）
        tags = []
        tags_data = info.get("tags", [])
        for tag in tags_data:
            if isinstance(tag, dict):
                tags.append(tag.get("tag_name", str(tag)))
            else:
                tags.append(str(tag))

        # 类型
        content_type = "video"
        if thumbnail and "img_src" in str(thumbnail):
            content_type = "image"
        elif "dynamic" in content.lower():
            content_type = "article"

        # 分类
        category = "video_creative"

        return {
            "source": "Bilibili",
            "source_url": link,
            "title": title,
            "description": description,
            "author": author,
            "published_at": published_at,
            "content_type": content_type,
            "category": category,
            "tags": tags,
            "thumbnail": thumbnail,
            "media_url": media_urls[0] if media_urls else None,
            "language": "zh",
            "raw": {
                "title": title,
                "desc": description,
                "pub_text": pub_time,
                "arclink": arclink,
                "author": author,
                "items": items,
            },
        }
