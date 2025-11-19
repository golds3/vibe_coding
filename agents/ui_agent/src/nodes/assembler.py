"""Assembler node writes generated image bytes and metadata to disk."""
from __future__ import annotations

from pathlib import Path

from src.state import UIState


class AssemblerNode:
    """Persists the generated PNG and accompanying prompt for inspection."""

    def __init__(self, output_path: str = "outputs/ui_design.png") -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.output_path = project_root / output_path
        self.alt_output_path = project_root / "outputs/ui_homepage.png"

    def _write_metadata(self, state: UIState) -> None:
        meta_path = self.output_path.with_suffix(".txt")
        lines = [
            "# UI Design Summary",
            f"Style: {state.get('preferred_style', '未指定')}",
            f"HTML Mockup: {state.get('ui_document_path', 'N/A')}",
            "",
            "## Prompt",
            state.get("ui_prompt", ""),
        ]
        meta_path.write_text("\n".join(lines), encoding="utf-8")

    def __call__(self, state: UIState) -> UIState:
        image_bytes: bytes | None = state.get("image_bytes")
        if not image_bytes:
            raise ValueError("image_bytes missing from state, image generation failed")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_bytes(image_bytes)
        self.alt_output_path.write_bytes(image_bytes)
        self._write_metadata(state)
        absolute_path = str(self.output_path.resolve())
        return {**state, "image_path": absolute_path}
