"""
Creative Radar — 每日采集脚本

用法：
    python scripts/daily_collect.py
    python scripts/daily_collect.py --source youtube --source rss --limit 100
    python scripts/daily_collect.py --dry-run   # 只显示不入库
"""
import argparse
import sys
from pathlib import Path

# 确保项目根目录在路径
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.database import init_db, SessionLocal
from backend.app.database.models import CreativeItem
from backend.app.collectors import base, rss, behance as behance_mod, dribbble as dribbble_mod, bilibili as bilibili_mod, topys as topys_mod, pinterest as pinterest_mod


# 默认源（RSS 测试源）
RSS_SOURCES = [
    ("youtube", "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw", "video_creative"),
    ("mozilla_hacks", "https://hacks.mozilla.org/feed/", "ai_creative"),
    ("smashing", "https://www.smashingmagazine.com/feed/", "visual_design"),
]

# 第一梯队数据源配置（API 密钥需自行填写）
FIRST_TIER_SOURCES = {
    "behance": {
        "cls": behance_mod.BehanceCollector,
        "config": {"api_key": "", "username": "creative", "max_items": 100},
    },
    "dribbble": {
        "cls": dribbble_mod.DribbbleCollector,
        "config": {"api_key": "", "user_id": "1", "max_items": 100},
    },
    "bilibili": {
        "cls": bilibili_mod.BilibiliCollector,
        "config": {"cookies": {}, "aspect_ids": [1, 2, 3], "max_items": 100},
    },
    "pinterest": {
        "cls": pinterest_mod.PinterestCollector,
        "config": {"access_token": "", "board_id": None, "max_items": 100},
    },
    "topys": {
        "cls": topys_mod.TopysCollector,
        "config": {"max_items": 100},
    },
}

# 顺序：RSS 测试源 + 第一梯队源
DEFAULT_SOURCES = ["youtube", "mozilla_hacks", "smashing", "behance", "dribbble", "bilibili", "pinterest", "topys"]

def collect_sources(sources, dry_run=False):
    # 执行采集并入库
    init_db()
    db = SessionLocal()
# 执行采集并入库
    init_db()
    db = SessionLocal()

    # 构建采集器实例
    collector_map = {}

    # RSS 测试源
    rss_sources = [
        ("youtube", "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw", "video_creative"),
        ("mozilla_hacks", "https://hacks.mozilla.org/feed/", "ai_creative"),
        ("smashing", "https://www.smashingmagazine.com/feed/", "visual_design"),
    ]
    for name, url, cat in rss_sources:
        collector_map[name] = rss.RSSCollector(url, name=name, category=cat, max_items=100)

    # 第一梯队源
    first_tier_sources = {
        "behance": {
            "cls": behance_mod.BehanceCollector,
            "config": {"api_key": "", "username": "creative", "max_items": 100},
        },
        "dribbble": {
            "cls": dribbble_mod.DribbbleCollector,
            "config": {"api_key": "", "user_id": "1", "max_items": 100},
        },
        "bilibili": {
            "cls": bilibili_mod.BilibiliCollector,
            "config": {"cookies": {}, "aspect_ids": [1, 2, 3], "max_items": 100},
        },
        "pinterest": {
            "cls": pinterest_mod.PinterestCollector,
            "config": {"access_token": "", "board_id": None, "max_items": 100},
        },
        "topys": {
            "cls": topys_mod.TopysCollector,
            "config": {"max_items": 100},
        },
    }
    collector_map.update(first_tier_sources)

    total_collected = 0
    for name in sources:
        if name not in collector_map:
            print(f"[跳过] {name}: 未找到采集器")
            continue

        collector = collector_map[name]
        if not collector.enabled:
            print(f"[跳过] {name}: 未启用")
            continue

        print(f"[采集] {name} ...", end=" ")
        try:
            items = collector.fetch(100)
            saved = 0
            for item in items:
                item_id = item["source"] + "-" + str(item["source_url"])[:40]
                existing = db.query(CreativeItem).filter_by(id=item_id).first()
                if existing:
                    continue
                db_item = CreativeItem(
                    id=item_id,
                    source=item["source"],
                    source_url=item["source_url"],
                    title=item["title"],
                    description=item["description"],
                    author=item["author"],
                    published_at=item["published_at"],
                    content_type=item["content_type"],
                    category=item["category"],
                    tags=item["tags"],
                    thumbnail=item["thumbnail"],
                    media_url=item["media_url"],
                    language=item["language"],
                    raw=item["raw"],
                    status="collected",
                    score=0.0,
                    top_candidate=False,
                    dedup_key="",
                )
                db.add(db_item)
                saved += 1
                total_collected += 1

            db.commit()
            if dry_run:
                print(f"[{len(items)} 条，{saved} 条入库（dry-run）]")
            else:
                print(f"[{len(items)} 条，{saved} 条入库]")
        except Exception as e:
            print(f"[失败] {e}")

    db.close()
    return total_collected

