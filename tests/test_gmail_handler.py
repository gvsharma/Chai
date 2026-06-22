from __future__ import annotations

from unittest.mock import patch

from agents.gmail.handler import handler


@patch("agents.gmail.handler.handle_summarize_action")
def test_handler_routes_summarize_action(mock_summarize) -> None:
    mock_summarize.return_value = {"statusCode": 200, "action": "summarize"}

    result = handler({"action": "summarize", "max_emails": 10}, None)

    mock_summarize.assert_called_once_with({"action": "summarize", "max_emails": 10})
    assert result["statusCode"] == 200


def test_handler_rejects_unknown_action() -> None:
    result = handler({"action": "archive"}, None)

    assert result["statusCode"] == 400
    assert "Unsupported action" in result["error"]
