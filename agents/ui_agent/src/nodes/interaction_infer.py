"""Node that infers interaction logic and transitions."""
from __future__ import annotations

from typing import List

from src.state import InteractionModel, UIState


class InteractionInferNode:
    """Describes how users interact with the inferred component tree."""

    def __call__(self, state: UIState) -> UIState:
        interactions: List[InteractionModel] = []
        for blueprint in state.get("component_tree", []):
            page = blueprint.get("page", "Screen")
            components = blueprint.get("components", [])
            if not components:
                continue
            interactions.append(
                {
                    "trigger": f"用户点击 {components[0]} CTA",
                    "response": f"在 {page} 中展示底部抽屉并引导填写核心信息",
                    "feedback": "提供即时校验、loading 动画与成功 toast",
                    "priority": "P0",
                }
            )
            interactions.append(
                {
                    "trigger": "滚动至指标区块",
                    "response": "触发数字动画，同时固定导航与 CTA",
                    "feedback": "背景模糊 + 轻微缩放，确保注意力集中",
                    "priority": "P1",
                }
            )
        return {**state, "interaction_map": interactions}
