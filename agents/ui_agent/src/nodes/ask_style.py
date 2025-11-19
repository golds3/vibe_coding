"""Human-in-the-loop node that captures preferred visual style."""
from __future__ import annotations

from langgraph.types import interrupt

from src.state import UIState


class AskStyleNode:
    """Pauses the graph to ask the operator for a UI style preference."""

    OPTIONS = {
        "A": "极简",
        "B": "暗黑",
        "C": "玻璃拟态",
        "D": "Material Design",
        "E": "插画风",
    }

    QUESTION = (
        "请问你偏好的 UI 风格是？\n"
        "A. 极简\n"
        "B. 暗黑\n"
        "C. 玻璃拟态\n"
        "D. Material Design\n"
        "E. 插画风\n"
        "请输入 A/B/C/D/E："
    )

    def _normalize(self, answer: str | None) -> str:
        if not answer:
            return self.OPTIONS["A"]
        answer = answer.strip()
        upper = answer.upper()
        if upper in self.OPTIONS:
            return self.OPTIONS[upper]
        for value in self.OPTIONS.values():
            if value in answer:
                return value
        return self.OPTIONS["A"]

    def __call__(self, state: UIState) -> UIState:
        answer = interrupt({"message": self.QUESTION})
        style = self._normalize(answer if isinstance(answer, str) else str(answer))
        return {**state, "preferred_style": style, "style_question": self.QUESTION}
