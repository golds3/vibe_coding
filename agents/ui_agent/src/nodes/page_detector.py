"""Node responsible for detecting candidate UI pages from raw PRD text."""
from __future__ import annotations

import re
from typing import List

from src.state import PageSummary, UIState


class PageDetectorNode:
    """Extracts potential pages/sections and assigns intent + priority."""

    def _extract_headings(self, text: str) -> List[str]:
        pattern = re.compile(r"^#+\s+(.+)$", re.MULTILINE)
        matches = pattern.findall(text)
        return [m.strip() for m in matches if m.strip()]

    def _infer_summary(self, heading: str, prd_text: str) -> str:
        window = 200
        idx = prd_text.find(heading)
        if idx == -1:
            snippet = prd_text[:window]
        else:
            snippet = prd_text[idx : idx + window]
        snippet = re.sub(r"\s+", " ", snippet)
        return snippet.strip() or "核心路径说明"

    def __call__(self, state: UIState) -> UIState:
        prd_text = state.get("prd_text", "").strip()
        headings = self._extract_headings(prd_text)
        if not headings:
            headings = ["Homepage", "Details", "Settings"]
        pages: List[PageSummary] = []
        for idx, heading in enumerate(headings, start=1):
            summary = self._infer_summary(heading, prd_text)
            pages.append(
                {
                    "name": heading,
                    "summary": summary,
                    "intent": "引导用户完成核心任务",
                    "priority": idx,
                }
            )
        return {**state, "pages": pages}
