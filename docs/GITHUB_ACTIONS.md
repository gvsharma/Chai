# GitHub Actions — CHAI app CI/CD

Infrastructure and OIDC roles are provisioned by [Chai-Infra](https://github.com/gvsharma/Chai-Infra). See that repo's [docs/GITHUB_ACTIONS.md](https://github.com/gvsharma/Chai-Infra/blob/main/docs/GITHUB_ACTIONS.md) for full setup.

## Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR / push to `main` | Run `pytest` |
| `deploy-lambda.yml` | Push to `main` (agent paths) or manual | Package and deploy `gmail-agent` Lambda |

## Required GitHub configuration

After Chai-Infra Terraform apply:

| Setting | Type | Source |
|---------|------|--------|
| `AWS_LAMBDA_DEPLOY_ROLE_ARN` | Secret | `terraform output -json lambda_deploy_github_setup` |
| `AWS_REGION` | Variable | `us-east-1` |
| `GMAIL_LAMBDA_FUNCTION_NAME` | Variable | `gmail-agent` |
| `development` | Environment | Optional approval gate for deploy |

## Local packaging

```bash
chmod +x scripts/package-lambda.sh
scripts/package-lambda.sh gmail
# artifact: dist/lambda-gmail.zip
```

## Lambda secrets

Configure in AWS (not in GitHub):

- `OPENROUTER_API_KEY`
- `GMAIL_CREDENTIALS_JSON`

See [docs/ENVIRONMENT.md](./ENVIRONMENT.md).
