"""
Creative Radar — TOPYS 数据源采集器

TOPYS 设计新闻与灵感网站的 RSS 订阅源。

抓取视觉设计、创意、品牌、平面设计等内容。
"""
from .rss import RSSCollector


class TopysCollector(RSSCollector):
    """TOPYS 数据源采集器。"""

    name = "topys"
    supported_types = ["image", "article", "video"]
    update_frequency = "daily"

    def __init__(self, max_items: int = 100):
        super().__init__(
            feed_url="https://topys.com/feed",
            name="TOPYS",
            category="visual_design",
            max_items=max_items,
        )

    @property
    def enabled(self) -> bool:
        """默认启用（RSS 源可访问）。"""
        return True
