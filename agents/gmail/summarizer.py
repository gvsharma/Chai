from __future__ import annotations

import json
import logging
import os
from typing import Any, Protocol

from agents.gmail.email_reader import EmailMessage, format_emails_for_prompt
from shared.llm.base import LLMProvider
from shared.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

SUMMARY_BANNER = "=" * 48


class EmailReader(Protocol):
    def fetch_emails(self, max_emails: int) -> list[EmailMessage]:
        """Return up to max_emails messages."""


class GmailApiEmailReader:
    """Read Gmail messages via the Gmail API using a service-account or OAuth token."""

    def __init__(self, credentials_json: str | None = None) -> None:
        self._credentials_json = credentials_json or os.environ.get("GMAIL_CREDENTIALS_JSON", "")

    def fetch_emails(self, max_emails: int) -> list[EmailMessage]:
        if not self._credentials_json:
            raise ValueError("GMAIL_CREDENTIALS_JSON is required to read Gmail messages")

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "google-api-python-client and google-auth are required for Gmail API access"
            ) from exc

        credentials_info = json.loads(self._credentials_json)
        credentials = Credentials.from_authorized_user_info(credentials_info)
        service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

        list_response = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_emails, labelIds=["INBOX"])
            .execute()
        )
        message_refs = list_response.get("messages", [])

        emails: list[EmailMessage] = []
        for message_ref in message_refs:
            message_id = message_ref["id"]
            message = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format="metadata", metadataHeaders=["From", "Subject"])
                .execute()
            )
            headers = {
                header["name"]: header["value"]
                for header in message.get("payload", {}).get("headers", [])
            }
            emails.append(
                EmailMessage(
                    sender=headers.get("From", "unknown"),
                    subject=headers.get("Subject", "(no subject)"),
                    snippet=message.get("snippet", ""),
                )
            )

        return emails


def summarize_emails(
    *,
    max_emails: int,
    email_reader: EmailReader | None = None,
    llm_provider: LLMProvider | None = None,
) -> str:
    """Read emails, summarize with the configured LLM provider, and log to CloudWatch."""
    reader = email_reader or GmailApiEmailReader()
    provider = llm_provider or get_llm_provider()

    emails = reader.fetch_emails(max_emails)
    logger.info("Fetched %s emails for summarization", len(emails))

    prompt = format_emails_for_prompt(emails)
    summary = provider.summarize(prompt)
    formatted = format_summary_log(summary)
    logger.info("%s", formatted)
    return formatted


def format_summary_log(summary: str) -> str:
    return (
        f"{SUMMARY_BANNER}\n\n"
        "CHAI GMAIL SUMMARY\n\n"
        f"{summary.strip()}\n\n"
        f"{SUMMARY_BANNER}"
    )


def handle_summarize_action(event: dict[str, Any]) -> dict[str, Any]:
    max_emails = int(event.get("max_emails", 100))
    summary = summarize_emails(max_emails=max_emails)
    return {
        "statusCode": 200,
        "action": "summarize",
        "email_count": max_emails,
        "summary": summary,
    }
