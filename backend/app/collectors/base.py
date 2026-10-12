"""
Creative Radar — 数据源采集基类

所有数据源采集器继承此类，实现统一的采集接口。
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseCollector(ABC):
    """数据源采集基类。"""

    name: str = "base"
    supported_types: list[str] = ["image", "video", "article", "project"]
    update_frequency: str = "daily"

    @property
    def enabled(self) -> bool:
        """是否启用。子类可覆盖，默认总是启用。"""
        return True

    @abstractmethod
    def fetch(self, max_items: int = 100) -> list[dict]:
        """
        从数据源抓取原始条目。
        返回值：原始条目列表，每条包含:
        - source: 数据源名
        - source_url: 来源链接
        - title: 标题
        - description: 描述
        - author: 作者
        - published_at: 发布时间（datetime）
        - content_type: 类型
        - category: 分类
        - tags: 标签列表
        - thumbnail: 缩略图
        - media_url: 媒体地址
        - language: 语言
        - raw: 原始数据
        """
        raise NotImplementedError

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        """规范化原始条目为统一格式。子类可覆盖。"""
        return raw


class CollectorManager:
    """采集器管理器：按需实例化并执行采集。"""

    def __init__(self, enabled_sources: list[str] | None = None):
        self._enabled_sources = enabled_sources or []

    def register(self, collector: BaseCollector) -> None:
        """注册一个采集器。"""
        setattr(self, collector.name, collector)

    def collect(self, max_items_per_source: int = 100) -> list[dict]:
        """执行所有已启用采集器。"""
        results = []
        for name, collector in self.__class__.__dict__.items():
            if isinstance(collector, BaseCollector):
                if self._enabled_sources and name not in self._enabled_sources:
                    continue
                if not collector.enabled:
                    continue
                try:
                    items = collector.fetch(max_items_per_source)
                    results.extend(items)
                except Exception as e:
                    print(f"[collect] {name} 采集失败: {e}")
        return results
