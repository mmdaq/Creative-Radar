"""
Creative Radar — AI 分析模块

统一调用 OpenAI Compatible API，实现：
- 8 问分析（摘要 / 推荐 / 创意核心 / 视觉 / 套路 / 模仿 / 应用 / 提示词）
- 创意评分（新颖度×30% + 视觉冲击×25% + 可模仿性×25% + 学习价值×20%）
"""
from typing import Any

from backend.app.config import settings


class AIClient:
    """OpenAI Compatible API 客户端（使用配置文件中的设置）。"""

    def __init__(
        self,
        provider: str = "lmstudio",
        base_url: str = "http://127.0.0.1:1234/v1",
        api_key: str = "lm-studio",
        model: str = "Qwen",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        self.provider = provider
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(self, role: str, content: str, **kwargs) -> dict[str, Any]:
        """调用 OpenAI Compatible API。"""
        try:
            import openai

            client = openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": role, "content": content}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            return {
                "success": True,
                "content": resp.choices[0].message.content,
                "raw": resp,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class AIAnalyzer:
    """AI 分析器。负责 8 问分析和创意评分。"""

    def __init__(self, client: AIClient | None = None):
        self.client = client or AIClient()

    def analyze(self, item: dict[str, Any]) -> dict[str, Any]:
        """对一条创意内容进行 8 问分析。"""
        prompt = self._build_analyzer_prompt(item)
        result = self.client.call(
            "user",
            prompt,
        )

        if not result["success"]:
            return self._empty_analysis()

        text = result["content"]

        # 尝试解析 JSON
        parsed = self._parse_json(text)

        if not parsed:
            return self._empty_analysis()

        return {
            "ai_summary": parsed.get("ai_summary", ""),
            "recommendation": parsed.get("recommendation", ""),
            "creative_core": parsed.get("creative_core", ""),
            "visual_analysis": parsed.get("visual_analysis", ""),
            "creative_tricks": parsed.get("creative_tricks", ""),
            "imitation_method": parsed.get("imitation_method", ""),
            "application": parsed.get("application", ""),
            "ai_prompt": parsed.get("ai_prompt", ""),
        }

    def score(self, item: dict[str, Any]) -> dict[str, Any]:
        """对创意进行评分。"""
        # 当前使用固定评分，实际生产环境下可调用 AI
        # 这里用固定分数以便快速演示
        score = self._fixed_score(item)
        return {
            "novelty": score,
            "visual_impact": score,
            "imitability": score,
            "learning_value": score,
            "score": score,
        }

    def _build_analyzer_prompt(self, item: dict[str, Any]) -> str:
        """构建 8 问分析提示词。"""
        title = item.get("title", "")
        source = item.get("source", "")
        category = item.get("category", "visual_design")
        tags = ", ".join(item.get("tags", [])) if item.get("tags") else ""
        description = item.get("description", "")
        author = item.get("author", "")
        source_url = item.get("source_url", "")
        published_at = item.get("published_at", "")

        return f"""
Title: {title}
Source: {source}
Category: {category}
Tags: {tags}
Description: {description}
Author: {author}
URL: {source_url}
Published At: {published_at}

请按 8 问分析：
1. 这是什么？（一句话概括）
2. 为什么值得看？（推荐理由）
3. 最核心创意是什么？（Creative Core）
4. 视觉上为什么有效？（构图/色彩/比例/材质/光影/镜头/节奏/字体/空间）
5. 用了什么创意套路？（尺度反差/视觉错觉/物体拟人/现实×幻想/旧物新用/反常识/极简/荒诞）
6. 如何模仿？（给出 3 步）
7. 如何应用到自己的项目？（广告/短视频/海报/AI图片/AI视频/品牌/产品）
8. AI 如何继续生成？（给出 Midjourney/Flux/SDXL/Qwen Image/视频 提示词）

只输出 JSON，不要任何解释。
"""

    def _build_scoring_prompt(self, item: dict[str, Any]) -> str:
        """构建评分提示词。"""
        title = item.get("title", "")
        source = item.get("source", "")
        category = item.get("category", "visual_design")
        ai_summary = item.get("ai_summary", "")
        creative_core = item.get("creative_core", "")
        visual_analysis = item.get("visual_analysis", "")
        imitation_method = item.get("imitation_method", "")

        return f"""
Title: {title}
Source: {source}
Category: {category}
AI Summary: {ai_summary}
Creative Core: {creative_core}
Visual Analysis: {visual_analysis}
Imitation Method: {imitation_method}

请按以下维度评分（0～10）：
1. 新颖度（0～10）
2. 视觉冲击力（0～10）
3. 可模仿性（0～10）
4. 学习价值（0～10）

Creative Score = 新颖度×0.30 + 视觉冲击力×0.25 + 可模仿性×0.25 + 学习价值×0.20

只输出 JSON：{{"novelty": N, "visual_impact": N, "imitability": N, "learning_value": N, "score": N}}
"""

    def _parse_json(self, text: str) -> dict[str, Any]:
        """尝试从文本中解析 JSON。"""
        import json

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        import re

        # 匹配 { ... } 块
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {}

    def _empty_analysis(self) -> dict[str, Any]:
        """返回空分析结果（API 调用失败时）。"""
        return {
            "ai_summary": "分析失败，请稍后重试。",
            "recommendation": "",
            "creative_core": "",
            "visual_analysis": "",
            "creative_tricks": "",
            "imitation_method": "",
            "application": "",
            "ai_prompt": "",
        }

    @staticmethod
    def _fixed_score(item: dict[str, Any]) -> float:
        """固定评分（演示用）。"""
        # 实际生产环境下，这里调用 AI 打分
        # 暂时使用基于标题长度、标签数量等简单指标
        import math

        title_len = len(item.get("title", ""))
        tags = item.get("tags", [])
        score = min(10.0, 4.0 + title_len * 0.3 + len(tags) * 1.0)
        return round(min(10.0, score), 2)
