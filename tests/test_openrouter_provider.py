from __future__ import annotations

import json

import pytest
import responses

from shared.llm.openrouter_provider import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL_NAME,
    EMAIL_SUMMARY_SYSTEM_PROMPT,
    OpenRouterError,
    OpenRouterProvider,
)


@pytest.fixture
def provider() -> OpenRouterProvider:
    return OpenRouterProvider(api_key="test-key", session=__import__("requests").Session())


@responses.activate
def test_generate_returns_clean_text(provider: OpenRouterProvider) -> None:
    responses.add(
        responses.POST,
        f"{DEFAULT_BASE_URL}/chat/completions",
        json={
            "choices": [{"message": {"content": "  Hello world  "}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        },
        status=200,
    )

    result = provider.generate("Say hello", system_prompt="Be brief")

    assert result == "Hello world"
    assert len(responses.calls) == 1
    request_body = responses.calls[0].request.body
    assert request_body is not None
    assert DEFAULT_MODEL_NAME.encode() in request_body
    assert b"Be brief" in request_body


@responses.activate
def test_summarize_uses_executive_assistant_prompt(provider: OpenRouterProvider) -> None:
    responses.add(
        responses.POST,
        f"{DEFAULT_BASE_URL}/chat/completions",
        json={"choices": [{"message": {"content": "Summary"}}]},
        status=200,
    )

    provider.summarize("Email content")

    request_body = responses.calls[0].request.body
    assert request_body is not None
    payload = json.loads(request_body)
    assert payload["messages"][0]["content"] == EMAIL_SUMMARY_SYSTEM_PROMPT


@responses.activate
def test_retries_on_rate_limit(provider: OpenRouterProvider) -> None:
    responses.add(
        responses.POST,
        f"{DEFAULT_BASE_URL}/chat/completions",
        json={"error": "rate limited"},
        status=429,
        headers={"Retry-After": "0"},
    )
    responses.add(
        responses.POST,
        f"{DEFAULT_BASE_URL}/chat/completions",
        json={"choices": [{"message": {"content": "Recovered"}}]},
        status=200,
    )

    result = provider.generate("retry me")

    assert result == "Recovered"
    assert len(responses.calls) == 2


@responses.activate
def test_raises_on_non_retryable_error(provider: OpenRouterProvider) -> None:
    responses.add(
        responses.POST,
        f"{DEFAULT_BASE_URL}/chat/completions",
        json={"error": "bad request"},
        status=400,
    )

    with pytest.raises(OpenRouterError, match="status=400"):
        provider.generate("fail")


def test_requires_api_key() -> None:
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider(api_key="")
