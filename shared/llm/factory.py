from __future__ import annotations

import os

from shared.llm.base import LLMProvider
from shared.llm.openrouter_provider import OpenRouterProvider

SUPPORTED_PROVIDERS = frozenset({"openrouter"})


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """Return an LLM provider based on LLM_PROVIDER environment variable."""
    name = (provider_name or os.environ.get("LLM_PROVIDER", "openrouter")).strip().lower()

    if name == "openrouter":
        return OpenRouterProvider()

    raise ValueError(
        f"Unsupported LLM provider: {name!r}. Supported providers: {sorted(SUPPORTED_PROVIDERS)}"
    )
