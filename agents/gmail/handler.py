from __future__ import annotations

import logging
from typing import Any

from agents.gmail.summarizer import handle_summarize_action

logger = logging.getLogger(__name__)


def handler(event: dict[str, Any] | None, context: Any) -> dict[str, Any]:
    """AWS Lambda entrypoint for the CHAI Gmail agent."""
    event = event or {}
    action = event.get("action", "summarize")
    function_name = getattr(context, "function_name", "gmail-agent")

    logger.info("CHAI Gmail agent invoked function=%s action=%s", function_name, action)

    if action == "summarize":
        return handle_summarize_action(event)

    logger.error("Unsupported Gmail agent action: %s", action)
    return {
        "statusCode": 400,
        "error": f"Unsupported action: {action}",
    }
