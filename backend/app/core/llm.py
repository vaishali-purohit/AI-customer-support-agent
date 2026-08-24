import os
from importlib import import_module
from typing import Any, Optional

from app.core.constants import LLM_MODEL, LLM_MAX_TOKENS

_client: Optional[Any] = None


# Returns a singleton Anthropic client, creating it on first call
def get_client() -> Any:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        try:
            anthropic = import_module("anthropic")
        except ImportError as exc:
            raise RuntimeError("The anthropic package is not installed") from exc
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


# Generates a response from the LLM using the provided messages and system prompt
def generate(messages: list[dict], system: str = "", model: str = LLM_MODEL, max_tokens: int = LLM_MAX_TOKENS) -> str:
    client = get_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text
