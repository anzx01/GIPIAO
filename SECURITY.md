# Security Policy

## Secrets

Never commit real credentials, API tokens, database URLs, private keys, cookies,
session tokens, logs, cached market data, generated reports, or local `.env`
files.

Generate a JWT secret locally:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

If a token has ever been committed, rotate it at the provider immediately. If
the repository has already been pushed, remove it from Git history before making
the repository public.

## Pre-Push Check

Run:

```bash
git add -A
python scripts/compliance_check.py
```

This script checks Git-tracked files for common secret patterns and files that
should stay local.

## Reporting

Please report vulnerabilities privately to the repository maintainer instead of
opening a public issue with exploitable details.
