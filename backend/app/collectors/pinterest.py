"""
Creative Radar — Pinterest 数据源采集器

Pinterest 官方 API（v5 Pins Search）。
需要访问令牌：https://developers.pinterest.com/

抓取视觉设计、艺术、摄影、插画、产品、概念设计相关的 Pin。
"""
from typing import Any

import requests

from .base import BaseCollector

# 默认的轻量级授权
# 实际使用时需要通过 OAuth 获取访问令牌
DEFAULT_AUTHORIZATION = "Bearer access_token"


class PinterestCollector(BaseCollector):
    """Pinterest 数据源采集器。"""

    name = "pinterest"
    supported_types = ["image", "video", "project", "article"]
    update_frequency = "daily"

    # 官方 API 端点（需要 OAuth 访问令牌）
    PINS_SEARCH_URL = "https://api.pinterest.com/v5/pins/search"
    USERS_SEARCH_URL = "https://api.pinterest.com/v5/users/search"

    def __init__(
        self,
        access_token: str,
        board_id: str | None = None,
        max_items: int = 100,
    ):
        self.access_token = access_token
        self.board_id = board_id
        self.max_items = max_items

    @property
    def enabled(self) -> bool:
        """访问令牌为空时不启用。"""
        return bool(self.access_token)

    def fetch(self, max_items: int = 100) -> list[dict]:
        """从 Pinterest API 抓取内容。"""
        if not self.access_token:
            raise ValueError("Pinterest 采集需要访问令牌（https://developers.pinterest.com/）")

        # 查询参数
        params: dict[str, Any] = {
            "limit": min(max_items, 100),
            "fields": "id,name,media,published_at,board,target,content_type",
        }

        try:
            resp = requests.get(
                self.PINS_SEARCH_URL,
                params=params,
                timeout=30,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise ValueError(f"Pinterest 采集失败: {e}")

        items = []
        # API 数据结构可能因版本而异
        pins = data.get("data", {}).get("pins", [])
        if not pins:
            # 可能返回 top_pins
            pins = data.get("data", {}).get("top_pins", [])

        for pin in pins[: max_items]:
            items.append(self._parse_pin(pin))
        return items

    def _parse_pin(self, pin: dict[str, Any]) -> dict[str, Any]:
        """将 Pinterest Pin 解析为统一格式。"""
        title = pin.get("name", "") or pin.get("official_title", "")
        description = pin.get("description", "") or pin.get("official_description", "")
        created_at = pin.get("created_at")

        # 发布时间
        published_at = None
        if created_at:
            try:
                from datetime import datetime

                published_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                published_at = None

        # 媒体
        thumbnail = None
        media_url = None
        media = pin.get("media", [])
        if media:
            for m in media:
                if m.get("id"):
                    thumbnail = m.get("image", {}).get("source") or m.get("url")
                    break
            if not thumbnail:
                thumbnail = media[0].get("url")

        # 链接
        link = pin.get("url", "")

        # 作者
        author = pin.get("owner", {}).get("username", "")

        # 标签/板块
        tags = []
        board = pin.get("board", {})
        category = board.get("name", "")
        if category:
            tags.append(category)
        # 内容类型
        content_type = pin.get("content_type", "image")

        return {
            "source": "Pinterest",
            "source_url": link,
            "title": title,
            "description": description,
            "author": author,
            "published_at": published_at,
            "content_type": content_type,
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
                "owner": pin.get("owner", {}),
                "media": pin.get("media", []),
                "board": board,
            },
        }
