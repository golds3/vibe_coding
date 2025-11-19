"""Architecture planning node leveraging an LLM."""
from __future__ import annotations

from textwrap import dedent
from typing import Callable, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import PRDState
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are a software architect. Given the product context and preferred programming "
    "language, recommend popular mainstream frameworks (no hallucinations) widely adopted "
    "for building business software in that ecosystem. Return JSON with:\n"
    "{\n"
    '  "business_architecture": string,\n'
    '  "technical_architecture": string,\n'
    '  "data_flow": string,\n'
    '  "scalability": string,\n'
    '  "frameworks": {\n'
    '       "language": string,\n'
    '       "rationale": string,\n'
    '       "backend": [string,...],\n'
    '       "frontend": [string,...],\n'
    '       "orchestration": [string,...]\n'
    "  }\n"
    "}\n"
    "Explain why each framework grouping fits the problem."
)


class ArchitectureNode:
    """Prompts the user for a tech stack (if needed) and calls the LLM."""

    _LANGUAGE_ALIASES: Dict[str, tuple[str, ...]] = {
        "python": ("python", "py"),
        "javascript": ("javascript", "js", "typescript", "ts", "node"),
        "java": ("java",),
        "go": ("go", "golang"),
    }

    def __init__(self, ask_fn: Callable[[str], str] | None = None) -> None:
        self._ask_fn = ask_fn or (lambda prompt: input(prompt))

    def _normalize_language(self, raw: str) -> str:
        candidate = raw.strip().lower()
        if not candidate:
            return "python"
        for lang, aliases in self._LANGUAGE_ALIASES.items():
            if candidate in aliases:
                return lang
        return candidate

    def __call__(self, state: PRDState) -> PRDState:
        raw_lang = state.get("tech_stack") or self._ask_fn("你想用什么语言开发？(默认 Python)：")
        normalized_lang = self._normalize_language(raw_lang)
        llm = get_llm()

        context = dedent(
            f"""
            Project: {state.get('project_name')}
            Domain: {state.get('domain')}
            Goal: {state.get('project_goal')}
            Preferred Language: {normalized_lang}
            """
        ).strip()
        result = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"{context}\nRespond ONLY with JSON."),
            ]
        )
        payload = extract_json(message_to_str(result))
        frameworks = payload.get("frameworks", {})

        return {
            **state,
            "tech_stack": normalized_lang,
            "frameworks": frameworks,
            "business_architecture": payload.get("business_architecture", ""),
            "technical_architecture": payload.get("technical_architecture", ""),
            "data_flow": payload.get("data_flow", ""),
            "scalability": payload.get("scalability", ""),
        }
