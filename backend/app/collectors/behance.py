"""
Creative Radar — Behance 数据源采集器

Adobe Behance 官方 API（v2）。
需要 API Key：https://www.behance.net/dev/api

抓取用户/组织的完整设计项目。
"""
from typing import Any

import requests

from .base import BaseCollector


class BehanceCollector(BaseCollector):
    """Behance 数据源采集器。"""

    name = "behance"
    supported_types = ["image", "video", "project", "article"]
    update_frequency = "daily"

    # Behance API endpoint
    USER_PROJECTS_URL = "https://api.behance.net/v2/users/{username}/projects"
    USER_GRID_URL = "https://api.behance.net/v2/groups/{username}/projects"
    SHARED_PROJECTS_URL = "https://api.behance.net/v2/users/{username}/shared_projects"

    # 项目类型：0=所有, 1=公开, 2=私有
    TYPE_ALL = 0

    def __init__(
        self,
        api_key: str,
        username: str = "default",
        max_items: int = 100,
    ):
        self.api_key = api_key
        self.username = username
        self.max_items = max_items

    @property
    def enabled(self) -> bool:
        """API Key 为空时不启用。"""
        return bool(self.api_key)

    def fetch(self, max_items: int = 100) -> list[dict]:
        """从 Behance API 抓取项目。"""
        if not self.api_key:
            raise ValueError("Behance 采集需要 API Key（https://www.behance.net/dev/api）")

        url = self.USER_PROJECTS_URL.format(username=self.username)
        headers = {
            "Authorization": f"{self.api_key}",
            "Content-Type": "application/json",
        }
        params = {
            "page": 1,
            "per_page": min(max_items, 100),
            "type": self.TYPE_ALL,
            "fields": "title,description,images,created_at,moderation_status,author,stats",
        }

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items = []
        projects = data.get("projects", [])
        for project in projects[: max_items]:
            items.append(self._parse_project(project))
        return items

    def _parse_project(self, project: dict[str, Any]) -> dict[str, Any]:
        """将 Behance 项目解析为统一格式。"""
        title = project.get("title", "")
        description = project.get("description", "")
        created_at = project.get("created_at")
        if created_at:
            try:
                from datetime import datetime

                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                created_at = None

        # 图片（第一张或最大的）
        thumbnail = None
        media_url = None
        images = project.get("images", {})
        if images:
            image_list = images.get("images", [])
            if image_list:
                thumbnail = image_list[0].get("image_link")
                # 如果有封面，优先用封面
                for img in image_list:
                    if img.get("type") == "cover":
                        thumbnail = img.get("image_link")
                        break
                if not thumbnail and len(image_list) > 1:
                    media_url = image_list[1].get("image_link") or thumbnail

        # 作者
        author = project.get("author", {}).get("name", "") if project.get("author") else ""

        # 标签
        tags = []
        # Behance 项目可能有 category
        category = project.get("category", "")
        if category:
            tags.append(category)

        # 链接
        link = project.get("url", "")

        return {
            "source": "Behance",
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
                "author": author,
                "images": project.get("images", {}),
            },
        }
