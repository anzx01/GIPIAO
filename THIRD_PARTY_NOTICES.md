# Third-Party Notices

This repository depends on open-source packages installed by `pip` and `pnpm`.
Dependency source code is not vendored in this repository.

## Frontend Dependency Scan

`pnpm licenses list --prod` reported production dependency licenses including:

- MIT
- ISC
- BSD-3-Clause
- Apache-2.0
- 0BSD
- MIT AND ISC
- CC-BY-4.0 for `caniuse-lite` browser compatibility data

## Backend Dependencies

Backend dependencies are declared in `requirements.txt`. Before a public release
or commercial distribution, run a Python license scanner in your target
environment, for example:

```bash
pip install pip-licenses
pip-licenses --from=mixed --format=markdown
```

## Data Providers

AkShare and Tushare data/service terms are separate from their client libraries
and separate from this project's MIT license. Do not redistribute provider data
unless your account and the provider's terms allow it.
