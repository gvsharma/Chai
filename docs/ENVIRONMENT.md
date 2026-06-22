# Environment variables

CHAI agents read configuration from Lambda environment variables (or local `.env` for development).

## LLM provider

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `openrouter` | LLM backend to use. Currently supported: `openrouter`. |
| `OPENROUTER_API_KEY` | Yes (for OpenRouter) | — | API key from [OpenRouter](https://openrouter.ai/). |
| `OPENROUTER_BASE_URL` | No | `https://openrouter.ai/api/v1` | OpenRouter API base URL. |
| `MODEL_NAME` | No | `deepseek/deepseek-chat-v3` | Model identifier passed to OpenRouter chat completions. |

## Gmail agent

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AGENT_TYPE` | No | — | Set to `gmail` in infrastructure for the Gmail Lambda. |
| `GMAIL_CREDENTIALS_JSON` | Yes (for live Gmail reads) | — | OAuth authorized-user JSON used by the Gmail API client. Store in AWS Secrets Manager or SSM and inject at deploy time; do not commit secrets. |
| `CHAI_DATA_BUCKET` | No | — | S3 bucket for agent state (provided by Terraform). |
| `CHAI_ENVIRONMENT` | No | — | Deployment environment name (for example `dev`). |
| `AGENT_NAME` | No | — | Lambda agent name (for example `gmail-agent`). |

## Example Lambda environment (gmail-agent)

```hcl
environment_variables = {
  AGENT_TYPE          = "gmail"
  LLM_PROVIDER        = "openrouter"
  OPENROUTER_API_KEY  = "<from-secrets-manager>"
  MODEL_NAME          = "deepseek/deepseek-chat-v3"
  GMAIL_CREDENTIALS_JSON = "<from-secrets-manager>"
}
```

## Local development

```bash
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=sk-or-...
export MODEL_NAME=deepseek/deepseek-chat-v3
export GMAIL_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"..."}'
```

Run the Gmail summarize handler locally:

```bash
python -c "from agents.gmail.handler import handler; print(handler({'action':'summarize','max_emails':5}, None))"
```
