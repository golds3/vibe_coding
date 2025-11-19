"""Non-functional requirement node that taps an LLM."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import PRDState
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are responsible for non-functional requirements of a PRD. "
    "Return JSON with:\n"
    "{\n"
    '  "nfr": {\n'
    '       "performance": string,\n'
    '       "security": string,\n'
    '       "scalability": string,\n'
    '       "observability": string,\n'
    '       "internationalization": string,\n'
    '       "external_services": string\n'
    "  },\n"
    '  "risks": [string,...],\n'
    '  "glossary": [string,...]\n'
    "}\n"
    "Tailor the response to the product domain."
)


class NfrNode:
    """Adds NFRs, dependencies, and risks via LLM output."""

    def __call__(self, state: PRDState) -> PRDState:
        llm = get_llm()
        context = (
            f"Project: {state.get('project_name')}\n"
            f"Domain: {state.get('domain')}\n"
            f"Architecture frameworks: {state.get('frameworks', {})}\n"
        )
        result = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"{context}\nRespond ONLY with JSON."),
            ]
        )
        payload = extract_json(message_to_str(result))
        return {
            **state,
            "nfr": payload.get("nfr", {}),
            "risks": payload.get("risks", []),
            "glossary": payload.get("glossary", []),
        }
