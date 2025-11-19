"""Node that builds a UI prompt and renders an HTML mockup screenshot."""
from __future__ import annotations

from pathlib import Path
from typing import List

from src import image_gen
from src.state import ComponentBlueprint, LayoutInstruction, UIState


class ImageGenNode:
    """Generates a UI render via the image_gen helper."""

    def __init__(self, size: str = "1440x1024") -> None:
        self.size = size

    def _summarize_components(self, blueprints: List[ComponentBlueprint]) -> str:
        lines = []
        for blueprint in blueprints:
            page = blueprint.get("page", "Screen")
            comps = ", ".join(blueprint.get("components", [])[:6])
            lines.append(f"{page}: {comps}")
        return "; ".join(lines)

    def _summarize_layout(self, layouts: List[LayoutInstruction]) -> str:
        desc = []
        for layout in layouts:
            desc.append(
                f"{layout.get('page','Screen')} uses {layout.get('grid','grid')} with flow {layout.get('flow','')}"
            )
        return "; ".join(desc)

    def _build_prompt(self, state: UIState) -> str:
        style = state.get("preferred_style", "极简")
        components = self._summarize_components(state.get("component_tree", []))
        layouts = self._summarize_layout(state.get("layout_plan", []))
        interactions = "; ".join(
            f"{item.get('trigger')} -> {item.get('response')}"
            for item in state.get("interaction_map", [])
        )
        prompt = (
            f"Design a {style} SaaS web UI."  # base context
            f" Components: {components}."
            f" Layout rules: {layouts}."
            f" Interaction affordances: {interactions}."
            " Use sharp typography, professional spacing, export as high fidelity product shot."
        )
        return prompt

    def __call__(self, state: UIState) -> UIState:
        prompt = self._build_prompt(state)
        outputs_dir = Path(__file__).resolve().parents[2] / "outputs"
        html_path = outputs_dir / "ui_design.html"
        image_bytes = image_gen.text2im(
            prompt=prompt, size=self.size, state=state, html_output_path=html_path
        )
        return {
            **state,
            "ui_prompt": prompt,
            "image_bytes": image_bytes,
            "ui_document_path": str(html_path.resolve()),
        }
