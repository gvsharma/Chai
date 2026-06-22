# CHAI

Cognitive Hub for Automation & Intelligence — application code for CHAI agents.

Infrastructure lives in [Chai-Infra](https://github.com/gvsharma/Chai-Infra).

## Gmail agent

The `gmail-agent` Lambda summarizes inbox emails using the configured LLM provider.

Sample EventBridge / test event:

```json
{
  "action": "summarize",
  "max_emails": 100
}
```

See `events/gmail_summarize.json` and `docs/ENVIRONMENT.md` for configuration details.

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Layout

```
agents/gmail/     Gmail Lambda handler and summarization flow
shared/llm/       Provider-agnostic LLM abstraction (OpenRouter today)
events/           Sample Lambda events
tests/            Unit tests
docs/             Environment variable reference
```
