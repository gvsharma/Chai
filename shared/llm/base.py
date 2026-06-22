from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Provider-agnostic interface for text generation and summarization."""

    @abstractmethod
    def summarize(self, text: str) -> str:
        """Summarize the given text."""

    @abstractmethod
    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Generate a response for the given prompt."""
