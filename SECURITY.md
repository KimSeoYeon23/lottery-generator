# Security Policy

## Supported Versions

This project is in early development. Security fixes are applied to the default branch.

## Reporting a Vulnerability

Please report security issues privately when possible. If GitHub Security Advisories are enabled for this repository, use a private advisory. Otherwise, contact the maintainer through the GitHub profile associated with this repository.

Do not open a public issue for vulnerabilities involving:

- Account credentials.
- Session cookies.
- Purchase request manipulation.
- Balance lookup behavior.
- Credential file permissions.
- Sensitive logs or screenshots.

When reporting, include:

- A short description of the issue.
- Steps to reproduce.
- The affected file or endpoint.
- The expected impact.
- Whether real credentials or real purchases were involved.

## Sensitive Areas

This project includes code paths that interact with a lottery account and purchase flow. Extra care is required around:

- `backend/client.py`
- `backend/views.py`
- `~/.lottery/credentials.json`
- `/api/save-credentials`
- `/api/balance`
- `/api/buy`
- `/api/buy-pension`

## Credential Handling

The app can save credentials locally to:

```text
~/.lottery/credentials.json
```

The file is written with owner-only permissions, but this is not a substitute for a full secret-management system. Do not use real credentials on shared machines, public servers, or untrusted environments.

## Responsible Testing

Use mock mode or test accounts whenever possible. Do not run automated tests that submit real purchases unless you intentionally initiated and reviewed the transaction.

## Disclosure

Please allow time for investigation before public disclosure. The maintainer will prioritize issues that can expose credentials, submit unintended purchases, or leak account data.
