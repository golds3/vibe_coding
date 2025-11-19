"""Data model planning node driven by an LLM."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import get_llm
from src.state import PRDState, TableSchema
from src.utils import extract_json, message_to_str

SYSTEM_PROMPT = (
    "You are a data architect. Provide a concise relational design for the product. "
    "Return JSON:\n"
    "{\n"
    '  "core_entities": [string,...],\n'
    '  "tables": [\n'
    "       {\n"
    '           "name": string,\n'
    '           "description": string,\n'
    '           "primary_key": string,\n'
    '           "fields": [\n'
    "                 {\"name\": string, \"type\": string, \"description\": string, \"constraints\": string}\n"
    "           ]\n"
    "       }\n"
    "  ],\n"
    '  "dto_contracts": [\n'
    "       {\"provider\": string, \"consumer\": string, \"payload\": object, \"notes\": string}\n"
    "  ]\n"
    "}\n"
    "Focus on the domain described."
)


class DataModelNode:
    """Defines entities, tables, and DTO contracts using an LLM."""

    def __call__(self, state: PRDState) -> PRDState:
        llm = get_llm()
        context = (
            f"Project: {state.get('project_name')}\n"
            f"Domain: {state.get('domain')}\n"
            f"Key Features: {[feature['name'] for feature in state.get('features', [])]}\n"
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
            "core_entities": payload.get("core_entities", []),
            "tables": payload.get("tables", []),
            "dto_contracts": payload.get("dto_contracts", []),
        }
