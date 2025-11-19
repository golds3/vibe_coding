"""Intent node that leverages an LLM to interpret the raw user requirement."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import PRDState
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are a senior product strategist. Based on the provided requirement, "
    "summarize the product intent and return JSON with the following keys:\n"
    "{\n"
    '  "project_name": string,\n'
    '  "project_goal": string,\n'
    '  "background": string,\n'
    '  "value": string,\n'
    '  "user_segments": [string,...],\n'
    '  "vision": string,\n'
    '  "domain": one of ["blog","ecommerce","chat","analytics","generic"]\n'
    "}\n"
    "Be concise but informative. Always pick the closest domain."
)


class IntentNode:
    """Extracts context such as domain, goal, and audience via an LLM."""

    def __call__(self, state: PRDState) -> PRDState:
        llm = get_llm()
        user_input = state.get("user_input", "")
        result = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Requirement:\n{user_input}\nRespond ONLY with JSON following the schema."
                ),
            ]
        )
        payload = extract_json(message_to_str(result))
        domain = payload.get("domain", "generic")
        return {**state, **payload, "domain": domain}
