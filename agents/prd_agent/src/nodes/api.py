"""API contract planning node using an LLM."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import ApiSpec, PRDState
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are an API designer. Produce representative endpoints following RESTful style. "
    "Return JSON with `apis` array where each entry has:\n"
    "{\n"
    '  "name": string,\n'
    '  "url": string,\n'
    '  "method": string,\n'
    '  "request": [ { "name": string, "type": string, "required": bool, "description": string } ],\n'
    '  "response": [ { ... } ],\n'
    '  "errors": { "code": "description" },\n'
    '  "example": { "request": object, "response": object }\n'
    "}\n"
    "Ensure fields align with the data model."
)


class ApiNode:
    """Produces API contracts via the LLM."""

    def __call__(self, state: PRDState) -> PRDState:
        llm = get_llm()
        feature_names = [feature["name"] for feature in state.get("features", [])]
        context = (
            f"Project: {state.get('project_name')}\n"
            f"Domain: {state.get('domain')}\n"
            f"Features: {feature_names}\n"
            f"Entities: {state.get('core_entities', [])}\n"
        )
        result = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"{context}\nRespond ONLY with JSON."),
            ]
        )
        payload = extract_json(message_to_str(result))
        apis: list[ApiSpec] = payload.get("apis", [])
        return {**state, "apis": apis}
