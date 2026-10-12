"""
Creative Radar — RSS 数据源采集器

基于 feedparser 抓取 RSS/Atom 订阅源。
"""
from datetime import datetime
from dateutil import parser
from typing import Any

import feedparser

from .base import BaseCollector


class RSSCollector(BaseCollector):
    """RSS 数据源采集器。"""

    name = "rss"
    supported_types = ["image", "article", "video"]
    update_frequency = "daily"

    def __init__(
        self,
        feed_url: str,
        name: str | None = None,
        category: str | None = None,
        max_items: int = 100,
    ):
        self.feed_url = feed_url
        self._source_name = name or feed_url.split("//")[-1].split("/")[0]
        self.category = category
        self.max_items = max_items

    @property
    def enabled(self) -> bool:
        """RSS 采集器默认启用。"""
        return True

    @property
    def source_name(self) -> str:
        """数据源显示名称。"""
        return self._source_name

    def fetch(self, max_items: int = 100) -> list[dict]:
        """抓取 RSS 订阅源，返回条目列表。"""
        feed = feedparser.parse(self.feed_url)
        # 安全读取错误信息（不同版本 feedparser 的 bozo/error 属性可能不同）
        if feed.bozo:
            error_msg = getattr(feed, "error", "未知解析错误")
            raise ValueError(f"RSS 解析失败: {error_msg}")
        if not feed.entries:
            raise ValueError(f"RSS 源无条目: {self.feed_url}")

        items = []
        for entry in feed.entries[: max_items]:
            items.append(self._parse_entry(entry))
        return items

    def _parse_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """将 feedparser entry 转为统一格式。"""
        # 发布时间
        published_at = None
        if hasattr(entry, "published") and entry.published:
            try:
                published_at = parser.parse(entry.published)
            except Exception:
                published_at = None
        elif hasattr(entry, "updated") and entry.updated:
            try:
                published_at = parser.parse(entry.updated)
            except Exception:
                published_at = None
        elif hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except Exception:
                published_at = None

        # 媒体封面（从 enclosure 或 description 中提取）
        thumbnail = None
        media_url = None
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enc in entry.enclosures:
                if "image" in enc.get("type", "") or "thumbnail" in enc.get("type", ""):
                    thumbnail = enc.get("href")
                    break
                if enc.get("type", "").startswith("image"):
                    media_url = enc.get("href")
                    break

        # 标签
        tags = []
        if hasattr(entry, "tags") and entry.tags:
            tags = [t.get("term", "") for t in entry.tags]
        if not tags and hasattr(entry, "categories") and entry.categories:
            tags = [c.get("term", "") for c in entry.categories]

        # 短描述（清理 HTML 标签）
        description = entry.get("summary", "")
        if hasattr(entry, "summary_detail") and entry.summary_detail:
            description = entry.summary_detail.get("value", "")

        return {
            "source": self.source_name,
            "source_url": entry.get("link", ""),
            "title": entry.get("title", ""),
            "description": description,
            "author": entry.get("author", ""),
            "published_at": published_at,
            "content_type": "image" if thumbnail or media_url else "article",
            "category": self.category,
            "tags": tags,
            "thumbnail": thumbnail,
            "media_url": media_url,
            "language": "en",
            "raw": {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "author": entry.get("author", ""),
            },
        }
