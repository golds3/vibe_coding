"""Shared utilities for parsing language model responses."""
from __future__ import annotations

import json
import re
from typing import Any, Dict

from langchain_core.messages import BaseMessage


def message_to_str(message: BaseMessage | str) -> str:
    """Normalize message content (which could be dict/list) to a string."""
    if isinstance(message, str):
        return message
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for chunk in content:
            if isinstance(chunk, dict) and "text" in chunk:
                parts.append(str(chunk["text"]))
            elif isinstance(chunk, str):
                parts.append(chunk)
        return "".join(parts)
    return str(content)


def extract_json(text: str) -> Dict[str, Any]:
    """Attempt to extract a JSON object from potentially noisy text."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = cleaned[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass
    return {}


__all__ = ["extract_json", "message_to_str"]
