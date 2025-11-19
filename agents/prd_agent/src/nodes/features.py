"""Feature planning node backed by an LLM."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import FeatureSpec, PRDState
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are a product requirement expert. Given the context, propose 3-5 core features. "
    "Return JSON with a `features` array. Each feature must contain:\n"
    "{\n"
    '  "name": string,\n'
    '  "description": string,\n'
    '  "inputs": [string,...],\n'
    '  "outputs": [string,...],\n'
    '  "preconditions": [string,...],\n'
    '  "postconditions": [string,...],\n'
    '  "edge_cases": [string,...],\n'
    '  "dependencies": [string,...]\n'
    "}\n"
    "Focus on practical workflows that align with the stated domain."
)


class FeatureNode:
    """Creates a feature backlog using the LLM response."""

    def __call__(self, state: PRDState) -> PRDState:
        llm = get_llm()
        context = (
            f"Project: {state.get('project_name')}\n"
            f"Domain: {state.get('domain')}\n"
            f"Goal: {state.get('project_goal')}\n"
        )
        result = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"{context}\nRespond ONLY with JSON."),
            ]
        )
        payload = extract_json(message_to_str(result))
        features: list[FeatureSpec] = payload.get("features", [])
        return {**state, "features": features}
