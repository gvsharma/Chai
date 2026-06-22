from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

from shared.llm.base import LLMProvider

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL_NAME = "deepseek/deepseek-chat-v3"
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 60
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

EMAIL_SUMMARY_SYSTEM_PROMPT = (
    "You are an executive assistant.\n\n"
    "Summarize the following emails.\n\n"
    "Return:\n\n"
    "1. Executive Summary\n"
    "2. Important Emails\n"
    "3. Action Items\n"
    "4. Urgent Follow Ups\n\n"
    "Keep the response concise."
)


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter returns a non-retryable error."""


class OpenRouterProvider(LLMProvider):
    """OpenRouter chat-completions provider."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.model_name = model_name or os.environ.get("MODEL_NAME", DEFAULT_MODEL_NAME)
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouterProvider")

    def summarize(self, text: str) -> str:
        return self.generate(text, system_prompt=EMAIL_SUMMARY_SYSTEM_PROMPT)

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._chat_completion(messages)

    def _chat_completion(self, messages: list[dict[str, str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
        }

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            started = time.perf_counter()
            try:
                response = self._session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                )
                duration_ms = (time.perf_counter() - started) * 1000

                if response.status_code in RETRYABLE_STATUS_CODES:
                    retry_after = self._retry_after_seconds(response)
                    logger.warning(
                        "OpenRouter retryable response status=%s attempt=%s/%s duration_ms=%.1f retry_after=%s",
                        response.status_code,
                        attempt,
                        self.max_retries,
                        duration_ms,
                        retry_after,
                    )
                    if attempt < self.max_retries:
                        time.sleep(retry_after)
                        continue
                    raise OpenRouterError(
                        f"OpenRouter request failed after {self.max_retries} attempts "
                        f"(status={response.status_code}): {response.text}"
                    )

                if not response.ok:
                    logger.error(
                        "OpenRouter request failed status=%s duration_ms=%.1f body=%s",
                        response.status_code,
                        duration_ms,
                        response.text,
                    )
                    raise OpenRouterError(
                        f"OpenRouter request failed (status={response.status_code}): {response.text}"
                    )

                data = response.json()
                self._log_token_usage(data, duration_ms)
                return self._extract_content(data)

            except (requests.Timeout, requests.ConnectionError) as exc:
                duration_ms = (time.perf_counter() - started) * 1000
                last_error = exc
                logger.warning(
                    "OpenRouter transport error attempt=%s/%s duration_ms=%.1f error=%s",
                    attempt,
                    self.max_retries,
                    duration_ms,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(self._backoff_seconds(attempt))
                    continue
                raise OpenRouterError(
                    f"OpenRouter request failed after {self.max_retries} attempts: {exc}"
                ) from exc

        raise OpenRouterError(f"OpenRouter request failed: {last_error}")

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(f"Unexpected OpenRouter response shape: {data}") from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterError("OpenRouter returned an empty response")

        return content.strip()

    @staticmethod
    def _log_token_usage(data: dict[str, Any], duration_ms: float) -> None:
        usage = data.get("usage")
        if isinstance(usage, dict):
            logger.info(
                "OpenRouter completion duration_ms=%.1f prompt_tokens=%s completion_tokens=%s total_tokens=%s",
                duration_ms,
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
            )
        else:
            logger.info("OpenRouter completion duration_ms=%.1f (token usage unavailable)", duration_ms)

    @staticmethod
    def _retry_after_seconds(response: requests.Response) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        return 1.0

    @staticmethod
    def _backoff_seconds(attempt: int) -> float:
        return min(2 ** (attempt - 1), 8.0)
