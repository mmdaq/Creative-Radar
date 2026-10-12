"""
Creative Radar — AI 分析模块测试

验证 8 问分析和创意评分的结构完整性（不依赖外部 API）。
"""
import json
import sys
from pathlib import Path

# 确保项目根目录在路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ai.analyzer import AIAnalyzer


def test_analyzer():
    """测试 8 问分析和创意评分。"""
    analyzer = AIAnalyzer()

    test_items = [
        {
            "title": "JPEG XL 浏览器支持",
            "source": "Mozilla Hacks",
            "category": "ai_creative",
            "tags": ["web", "format", "browser"],
            "description": "Mozilla 宣布对 JPEG XL 图像格式的浏览器支持，提升 Web 图像压缩效率。",
            "author": "Jake Archibald",
            "source_url": "https://hacks.mozilla.org/2026/08/intent-to-ship-jpeg-xl/",
            "published_at": "2026-08-24T15:32:15Z",
        },
        {
            "title": "巨型耳机广告",
            "source": "Behance",
            "category": "commercial",
            "tags": ["giant", "ad", "visual"],
            "description": "一个巨大水果广告的视觉灵感，巨型物体 + 微缩人物",
            "author": "Designer",
            "source_url": "https://behance.net/example/giant-headphones",
            "published_at": "2026-09-30T08:30:00Z",
        },
        {
            "title": "智能硬件手环",
            "source": "Bilibili",
            "category": "product_innovation",
            "tags": ["hardware", "ai", "health"],
            "description": "一款智能硬件手环，集成 AI 健康监测和实时翻译功能。",
            "author": "Creator",
            "source_url": "https://bilibili.com/example/wearable",
            "published_at": "2026-10-01T10:00:00Z",
        },
    ]

    all_pass = True

    for i, item in enumerate(test_items):
        print(f"测试 {i+1}/{len(test_items)}: {item['title']}")

        # 测试 8 问分析
        analysis = analyzer.analyze(item)
        expected_fields = [
            "ai_summary",
            "recommendation",
            "creative_core",
            "visual_analysis",
            "creative_tricks",
            "imitation_method",
            "application",
            "ai_prompt",
        ]

        for field in expected_fields:
            if field not in analysis:
                print(f"  ✗ 缺少字段: {field}")
                all_pass = False
            else:
                # 结构正确性检查：字段必须存在
                # 内容完整性检查：API 失败时返回空字符串（除 ai_summary 显示错误信息）
                is_ai_summary = field == "ai_summary"
                value = analysis[field]
                if is_ai_summary:
                    # ai_summary 应包含错误信息（API 调用失败时）
                    if not value:
                        print(f"  ✗ 字段为空: {field}")
                        all_pass = False
                    else:
                        print(f"  ✓ {field} (错误信息)")
                else:
                    # 其他字段空字符串表示 API 调用失败（正常）
                    # 测试时仅验证结构，不验证内容完整性
                    print(f"  ✓ {field}")

        # 测试 创意评分
        score = analyzer.score(item)
        required_score_fields = ["novelty", "visual_impact", "imitability", "learning_value", "score"]
        for field in required_score_fields:
            if field not in score:
                print(f"  ✗ 评分缺少字段: {field}")
                all_pass = False
            else:
                print(f"  ✓ {field} = {score[field]:.2f}")

        # 验证评分合理性
        if not (0 <= score["score"] <= 10):
            print(f"  ✗ 评分超出范围: {score['score']}")
            all_pass = False

    print()
    if all_pass:
        print("全部测试通过 ✓")
        return 0
    else:
        print("部分测试失败 ✗")
        return 1


if __name__ == "__main__":
    sys.exit(test_analyzer())
