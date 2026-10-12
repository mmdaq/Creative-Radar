"""
Creative Radar — 数据采集服务

统一的采集入口：调用所有采集器，整理结果，入库。
"""
from typing import Any

from backend.app.collectors import base as collectors_base
from backend.app.database.database import SessionLocal
from backend.app.database.models import CreativeItem


def get_collectors() -> list:
    """注册所有采集器。"""
    from backend.app.collectors import (
        rss,
        behance,
        dribbble,
        bilibili,
        pinterest,
        topys,
    )

    collectors = [
        ("youtube", rss.RSSCollector("https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw", name="youtube", category="video_creative", max_items=100)),
        ("mozilla_hacks", rss.RSSCollector("https://hacks.mozilla.org/feed/", name="mozilla_hacks", category="ai_creative", max_items=100)),
        ("smashing", rss.RSSCollector("https://www.smashingmagazine.com/feed/", name="smashing", category="visual_design", max_items=100)),
    ]

    # API 数据源（需配置密钥）
    # from backend.app.collectors import behance as behance_mod, dribbble as dribbble_mod
    # collectors.append(("behance", behance_mod.BehanceCollector(api_key="", username="creative", max_items=100)))
    # collectors.append(("dribbble", dribbble_mod.DribbbleCollector(api_key="", user_id="1", max_items=100)))

    return collectors


def _save_items(items: list[dict]) -> int:
    """
    将采集到的条目保存到数据库。
    返回保存成功的条目数。
    """
    from backend.app.database.models import CreativeItem

    db = next(get_db())
    try:
        count = 0
        for item in items:
            # 生成唯一 ID
            item_id = item["source"] + "-" + str(item["source_url"])[:40]

            # 去重检查
            existing = (
                db.query(CreativeItem)
                .filter(CreativeItem.id == item_id)
                .first()
            )
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
            count += 1

        db.commit()
        return count
    except Exception as e:
        db.rollback()
        print(f"[crawl] 保存失败: {e}")
        return 0
    finally:
        db.close()


async def crawl_all() -> dict[str, Any]:
    """
    执行所有采集器，整理结果，入库。
    返回：{collected: N, saved: N, sources: [...]}
    """
    results = {
        "collected": 0,
        "saved": 0,
        "sources": [],
    }

    for name, collector in get_collectors():
        try:
            if not collector.enabled:
                continue

            items = collector.fetch(100)
            if not items:
                continue

            saved = _save_items(items)
            results["collected"] += len(items)
            results["saved"] += saved
            results["sources"].append({
                "name": name,
                "collected": len(items),
                "saved": saved,
            })
            print(f"[crawl] {name}: 采集 {len(items)} 条，保存 {saved} 条")

        except Exception as e:
            print(f"[crawl] {name} 采集失败: {e}")
            results["sources"].append({
                "name": name,
                "collected": 0,
                "saved": 0,
                "error": str(e),
            })

    return results
