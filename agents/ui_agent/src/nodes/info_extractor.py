"""Node that infers information architecture for each detected page."""
from __future__ import annotations

from typing import List

from src.state import InformationBlock, UIState


class InfoExtractorNode:
    """Creates section/data point groupings per page."""

    COMMON_SECTIONS = ["Hero", "Highlights", "Featured Items", "Metrics", "Actions"]

    def _derive_sections(self, page_name: str, summary: str) -> List[str]:
        seeds = []
        lowered = summary.lower()
        if "data" in lowered or "指标" in summary:
            seeds.append("Key Metrics")
        if "流程" in summary or "flow" in lowered:
            seeds.append("User Journey")
        if "设置" in page_name or "settings" in lowered:
            seeds.append("Preferences")
        seeds.extend(self.COMMON_SECTIONS)
        return list(dict.fromkeys(seeds))

    def _derive_tasks(self, summary: str) -> List[str]:
        tasks = []
        if "注册" in summary or "signup" in summary.lower():
            tasks.append("完成注册或登录")
        if "购买" in summary or "checkout" in summary.lower():
            tasks.append("完成下单流程")
        if not tasks:
            tasks.append("浏览内容并触发主要 CTA")
        return tasks

    def __call__(self, state: UIState) -> UIState:
        pages = state.get("pages", [])
        info_blocks: List[InformationBlock] = []
        for page in pages:
            summary = page.get("summary", "")
            sections = self._derive_sections(page.get("name", ""), summary)
            info_blocks.append(
                {
                    "page": page.get("name", "Screen"),
                    "sections": sections,
                    "data_points": [
                        "主标题与副标题",
                        "价值陈述",
                        "CTA 按钮与状态",
                    ],
                    "user_tasks": self._derive_tasks(summary),
                }
            )
        return {**state, "information_blocks": info_blocks}
