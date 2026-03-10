# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do Not

- **Do not** open a public issue
- **Do not** discuss the vulnerability publicly
- **Do not** submit a pull request with the fix publicly

### Do

1. **Email security reports to**: security@rotsl.dev
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix timeline**: Depends on severity
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days
  - Low: Next release

### Disclosure Policy

We follow responsible disclosure:
1. We confirm the vulnerability
2. We develop and test a fix
3. We notify affected users (if applicable)
4. We publicly disclose after fix is available

## Security Best Practices

When using ContextFusion:

### API Keys
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly

### Data Handling
- Be cautious with sensitive data in context blocks
- Review privacy scores for sensitive content
- Use appropriate retention policies

### Dependencies
- Keep dependencies updated
- Review security advisories for dependencies
- Use `pip-audit` to check for known vulnerabilities

## Security Features

ContextFusion includes security-focused features:

- **Privacy Scoring**: Identifies potentially sensitive content
- **Trust Scoring**: Evaluates source reliability
- **Content Validation**: Sanitizes ingested content
- **Audit Logging**: Tracks context usage

## Known Limitations

- OCR may extract sensitive text from images
- PDF parsing may not fully sanitize all content
- Code extraction may include credentials in comments

Review all extracted content before use in production.

## Contact

For security questions not related to vulnerabilities:
- GitHub Discussions: https://github.com/rotsl/context-fusion/discussions
- Email: security@rotsl.dev
