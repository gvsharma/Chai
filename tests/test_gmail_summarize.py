from __future__ import annotations

from agents.gmail.email_reader import EmailMessage, format_emails_for_prompt
from agents.gmail.summarizer import format_summary_log, summarize_emails
from shared.llm.base import LLMProvider


class FakeEmailReader:
    def fetch_emails(self, max_emails: int) -> list[EmailMessage]:
        return [
            EmailMessage(
                sender="alice@example.com",
                subject="Quarterly review",
                snippet="Please review the attached deck.",
            ),
            EmailMessage(
                sender="bob@example.com",
                subject="Urgent: invoice",
                snippet="Payment is due today.",
            ),
        ][:max_emails]


class FakeLLMProvider(LLMProvider):
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    def summarize(self, text: str) -> str:
        self.last_prompt = text
        return (
            "Executive Summary:\nTwo emails reviewed.\n\n"
            "Important Emails:\n- Quarterly review\n- Urgent invoice\n\n"
            "Action Items:\n- Review deck\n\n"
            "Urgent Follow Ups:\n- Pay invoice today"
        )

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return self.summarize(prompt)


def test_format_emails_for_prompt_includes_metadata() -> None:
    emails = [
        EmailMessage(sender="a@example.com", subject="Hello", snippet="Hi there"),
    ]

    prompt = format_emails_for_prompt(emails)

    assert "From: a@example.com" in prompt
    assert "Subject: Hello" in prompt
    assert "Snippet: Hi there" in prompt


def test_summarize_emails_builds_prompt_and_formats_log() -> None:
    reader = FakeEmailReader()
    provider = FakeLLMProvider()

    result = summarize_emails(max_emails=2, email_reader=reader, llm_provider=provider)

    assert provider.last_prompt is not None
    assert "alice@example.com" in provider.last_prompt
    assert "CHAI GMAIL SUMMARY" in result
    assert "Executive Summary:" in result
    assert result.startswith("=" * 48)


def test_format_summary_log_wraps_content() -> None:
    formatted = format_summary_log("Line one")

    assert formatted.startswith("=" * 48)
    assert "CHAI GMAIL SUMMARY" in formatted
    assert "Line one" in formatted
