"""Node that infers component tree and reusable modules."""
from __future__ import annotations

from typing import List

from src.state import ComponentBlueprint, UIState


class ComponentInferNode:
    """Translates information blocks into concrete UI components."""

    BASE_COMPONENTS = {
        "Hero": ["Top Navigation", "Logo", "Hero Title", "Primary CTA"],
        "Highlights": ["Stat Badge", "Illustration", "Secondary CTA"],
        "Featured Items": ["Card Grid", "Filter Tabs", "Hover Actions"],
        "Metrics": ["KPI Row", "Trend Sparkline", "Tag List"],
        "Actions": ["Floating CTA", "Context Menu", "Support Link"],
        "Preferences": ["Toggle Row", "Dropdown", "Save Banner"],
    }

    def __call__(self, state: UIState) -> UIState:
        blueprints: List[ComponentBlueprint] = []
        for block in state.get("information_blocks", []):
            components: List[str] = []
            for section in block.get("sections", []):
                components.extend(self.BASE_COMPONENTS.get(section, [f"Custom {section}"]))
            rationale = (
                "覆盖首屏叙事、内容陈列与引导动作，保证信息层级清晰且可扩展"
            )
            blueprints.append(
                {
                    "page": block.get("page", "Screen"),
                    "group": "Root",
                    "components": components,
                    "rationale": rationale,
                }
            )
        return {**state, "component_tree": blueprints}
