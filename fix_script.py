# 修复 daily_collect.py 的函数结构问题
path = "scripts/daily_collect.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 找到有问题的区域：DEFAULT_SOURCES 后面应该跟函数定义
old = """DEFAULT_SOURCES = ["youtube", "mozilla_hacks", "smashing", "behance", "dribbble", "bilibili", "pinterest", "topys"]


    total_collected = 0
    for name in sources:"""

new = """DEFAULT_SOURCES = ["youtube", "mozilla_hacks", "smashing", "behance", "dribbble", "bilibili", "pinterest", "topys"]


def collect_sources(sources: list[str], dry_run: bool = False) -> int:
    """执行采集并入库。"""
    init_db()
    db = SessionLocal()

    # 构建采集器实例
    collector_map: dict[str, base.BaseCollector] = {}"""

if old in content:
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("修复成功")
else:
    print("未找到需要替换的文本")
    idx = content.find("total_collected = 0")
    if idx != -1:
        print(repr(content[idx-90:idx+30]))
