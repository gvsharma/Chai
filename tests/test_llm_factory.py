from __future__ import annotations

import os

import pytest

from shared.llm.factory import get_llm_provider
from shared.llm.openrouter_provider import OpenRouterProvider


def test_factory_returns_openrouter_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    provider = get_llm_provider()

    assert isinstance(provider, OpenRouterProvider)


def test_factory_defaults_to_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    provider = get_llm_provider()

    assert isinstance(provider, OpenRouterProvider)


def test_factory_rejects_unknown_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "bedrock")

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider()
