"""
Creative Radar — Dribbble 数据源采集器

Dribbble 官方 API（v2）。
需要 API key：https://developers.dribbble.com/

抓取用户的作品（shots），包括 UI / 网页 / 插画 / 动效。
"""
from typing import Any

import requests

from .base import BaseCollector


class DribbbleCollector(BaseCollector):
    """Dribbble 数据源采集器。"""

    name = "dribbble"
    supported_types = ["image", "video", "project", "article"]
    update_frequency = "daily"

    SHOTS_URL = "https://api.dribbble.com/v2/user/{user_id}/shots"

    def __init__(
        self,
        api_key: str,
        user_id: str = "1",
        max_items: int = 100,
    ):
        self.api_key = api_key
        self.user_id = user_id
        self.max_items = max_items

    @property
    def enabled(self) -> bool:
        """API Key 为空时不启用。"""
        return bool(self.api_key)

    def fetch(self, max_items: int = 100) -> list[dict]:
        """从 Dribbble API 抓取作品。"""
        if not self.api_key:
            raise ValueError("Dribbble 采集需要 API Key（https://developers.dribbble.com/）")

        url = self.SHOTS_URL.format(user_id=self.user_id)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        params = {
            "page": 1,
            "per_page": min(max_items, 100),
        }

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items = []
        shots = data.get("shots", [])
        for shot in shots[: max_items]:
            items.append(self._parse_shot(shot))
        return items

    def _parse_shot(self, shot: dict[str, Any]) -> dict[str, Any]:
        """将 Dribbble shot 解析为统一格式。"""
        title = shot.get("title", "")
        description = shot.get("description", "")
        created_at = shot.get("created_at")
        if created_at:
            try:
                from datetime import datetime

                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                created_at = None

        # 缩略图和大图
        thumbnail = shot.get("image") or shot.get("preview_url")
        media_url = shot.get("image_large") or shot.get("url")

        # 作者
        author = shot.get("player", {}).get("name", "")

        # 标签
        tags = [tag.get("name", "") for tag in shot.get("tags", [])]
        # 类别
        category = shot.get("category", "")
        if category:
            tags.append(category)

        # 链接
        link = shot.get("url", "")

        return {
            "source": "Dribbble",
            "source_url": link,
            "title": title,
            "description": description,
            "author": author,
            "published_at": created_at,
            "content_type": "image" if thumbnail else "project",
            "category": category or "visual_design",
            "tags": tags,
            "thumbnail": thumbnail,
            "media_url": media_url,
            "language": "en",
            "raw": {
                "title": title,
                "description": description,
                "created_at": created_at,
                "url": link,
                "player": shot.get("player", {}),
                "tags": shot.get("tags", []),
                "image": shot.get("image"),
            },
        }
