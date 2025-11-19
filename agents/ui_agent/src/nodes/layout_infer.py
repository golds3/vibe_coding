"""Node that infers layout descriptions for each page."""
from __future__ import annotations

from typing import List

from src.state import LayoutInstruction, UIState


class LayoutInferNode:
    """Produces layout tokens such as grid choice and flow."""

    def __call__(self, state: UIState) -> UIState:
        layout_plan: List[LayoutInstruction] = []
        for blueprint in state.get("component_tree", []):
            components = blueprint.get("components", [])
            layout_plan.append(
                {
                    "page": blueprint.get("page", "Screen"),
                    "grid": "12-column fluid grid with 64px margin",
                    "hero": components[0] if components else "Hero",
                    "flow": "Hero -> Highlight metrics -> Cards -> Action footer",
                    "responsive": "Collapse to stacked blocks on mobile, keep CTA sticky",
                    "emphasis": [components[0]] + components[1:3] if components else ["Hero"],
                }
            )
        return {**state, "layout_plan": layout_plan}
