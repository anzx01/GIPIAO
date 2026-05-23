# Compliance Notes

This project is intended to publish source code only.

## What Must Not Be Committed

- `.env`, `.env.local`, API tokens, JWT secrets, database credentials, cookies,
  private keys, or local agent/tool configuration.
- Cached market, news, or financial datasets under `data/` or `api/data/`.
- Logs under `logs/` or `api/logs/`.
- Generated reports under `reports/`.
- Build outputs such as `node_modules/`, `.next/`, `dist/`, `build/`, and
  `*.tsbuildinfo`.
- Third-party skill packs, templates, or copied documentation unless their
  license permits redistribution and the license text is included.

## Data Sources

The application can fetch data through third-party libraries and services such
as AkShare and Tushare. Their software licenses and data/service terms are
separate from this repository's MIT license.

Before using or publishing fetched data, confirm that your data source account,
usage volume, redistribution, and commercial use comply with the provider's
current terms. Do not publish raw cached data from those providers unless you
have explicit permission.

## Investment Disclaimer

This project is for research, engineering, and demonstration purposes. It does
not provide investment advice, securities recommendations, trading signals, or
any guarantee of future performance.

## Release Checklist

1. Stage intended removals and additions with `git add -A`.
2. Run `python scripts/compliance_check.py`.
3. Confirm `git status --short` contains only intentional source/doc changes.
4. Confirm no real secrets appear in `git grep -n -I "TOKEN\|SECRET\|PASSWORD"`.
5. Rotate any token that was previously committed.
6. If a real secret was committed before first public release, rewrite local Git
   history or create a fresh repository before pushing.
