# Security Policy

## Reporting a Vulnerability
If you discover a security issue, do **not** open a public issue. Report privately.

## Secrets
- Never commit `.env` files, API keys, tokens, or private keys.
- Use `configs/global/env.example` as your template.
- Prefer pulling secrets at runtime (Bitwarden CLI, 1Password, etc.)
- Secret scanning in CI (gitleaks) is included.
