# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by opening a [private security advisory](https://github.com/aakashsharan/research-vault/security/advisories/new) on GitHub.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

You should receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible.

## Security Best Practices

When using Research Vault:

1. **Never commit `.env` files** - Use `.env.example` as a template
2. **Rotate exposed keys immediately** - If you accidentally commit an API key, rotate it
3. **Keep dependencies updated** - Run `npm audit` and check for Python CVEs regularly
4. **Use HTTPS in production** - Never expose the API over plain HTTP
5. **Run locally only** - This MVP has no authentication; do not expose to the internet

## Security Features

- **Pre-commit hooks**: Automatically scan for secrets before commits (detect-secrets, gitleaks)
- **Security check script**: Run `bash scripts/security_check.sh` to verify no secrets are exposed
- **Dependabot**: Automated dependency security updates enabled
