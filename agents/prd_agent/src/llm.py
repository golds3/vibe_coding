"""Utility helpers for configuring and accessing a shared LLM client."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

_MODEL_OVERRIDE: Optional[str] = None
_TEMPERATURE_OVERRIDE: Optional[float] = None


def configure_llm(model: str | None = None, temperature: float | None = None) -> None:
    """Allow CLI or tests to override the default LLM settings."""
    global _MODEL_OVERRIDE, _TEMPERATURE_OVERRIDE
    if model:
        _MODEL_OVERRIDE = model
    if temperature is not None:
        _TEMPERATURE_OVERRIDE = temperature
    get_llm.cache_clear()  # type: ignore[attr-defined]


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return a cached ChatOpenAI instance configured via env/CLI overrides."""
    model = _MODEL_OVERRIDE or os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature = (
        _TEMPERATURE_OVERRIDE
        if _TEMPERATURE_OVERRIDE is not None
        else float(os.getenv("LLM_TEMPERATURE", "0.15"))
    )
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    default_headers: Dict[str, str] = {}
    if not api_key:
        # Allow LangSmith style API key mapping if running against self-hosted endpoints.
        api_key = os.getenv("LANGCHAIN_API_KEY", "")
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=base_url,
        api_key=api_key or None,
        default_headers=default_headers or None,
    )


__all__ = ["configure_llm", "get_llm"]
