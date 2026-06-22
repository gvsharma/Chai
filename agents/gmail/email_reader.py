from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    sender: str
    subject: str
    snippet: str


def format_emails_for_prompt(emails: list[EmailMessage]) -> str:
    """Build a single prompt from email metadata."""
    if not emails:
        return "No emails were found."

    sections: list[str] = []
    for index, email in enumerate(emails, start=1):
        sections.append(
            "\n".join(
                [
                    f"Email {index}:",
                    f"From: {email.sender}",
                    f"Subject: {email.subject}",
                    f"Snippet: {email.snippet}",
                ]
            )
        )
    return "\n\n".join(sections)
