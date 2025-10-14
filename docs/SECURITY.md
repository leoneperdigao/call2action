# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

The Call2Action team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities via one of the following methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to the Security tab of this repository
   - Click "Report a vulnerability"
   - Fill in the details

2. **Email**
   - Send an email to: [Your security email]
   - Include "SECURITY" in the subject line
   - Provide detailed information about the vulnerability

### What to Include

When reporting a security vulnerability, please include:

- Type of vulnerability (e.g., injection, XSS, CSRF, etc.)
- Full paths of affected source files
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue (what an attacker can do)
- Any suggested fixes (optional)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**: Varies based on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

### What to Expect

1. **Acknowledgment**: We'll acknowledge receipt of your vulnerability report
2. **Investigation**: We'll investigate and validate the reported vulnerability
3. **Update**: We'll keep you informed of the progress
4. **Fix**: We'll develop and test a fix
5. **Release**: We'll release a patched version
6. **Credit**: We'll publicly thank you (unless you prefer to remain anonymous)

## Security Best Practices

When using Call2Action, follow these security best practices:

### API Keys and Secrets

- **Never commit API keys** to version control
- Store sensitive data in environment variables (`.env` file)
- Use `.env` file and add it to `.gitignore`
- Rotate API keys regularly
- Use different API keys for development and production

### Input Validation

- Validate all audio/video file inputs
- Sanitize filenames to prevent path traversal
- Limit file sizes to prevent DoS attacks
- Verify file types before processing

### Configuration

- Review default settings in `config.py`
- Use appropriate Whisper model sizes (larger models = more resources)
- Set reasonable token limits for OpenAI API calls
- Configure rate limiting for API calls
- Monitor API usage and costs

### Dependencies

- Keep dependencies up to date
- Review Dependabot security alerts promptly
- Run `safety check` regularly to scan for vulnerabilities
- Use virtual environments to isolate dependencies

### Running in Production

- Use least-privilege principles for API keys
- Enable logging and monitoring
- Set appropriate timeouts for all external API calls
- Implement error handling to prevent information leakage
- Sanitize all outputs before displaying to users

## Known Security Considerations

### External API Dependencies

This project depends on external services:

1. **OpenAI API**
   - Sends transcript data to OpenAI for summarization
   - Data is processed according to [OpenAI's Data Usage Policy](https://openai.com/policies/usage-policies)
   - Consider data sensitivity before processing

2. **Faster Whisper**
   - Runs locally or on specified device
   - No external data transmission
   - Model files downloaded from Hugging Face

### Data Privacy

- Audio/video files are processed locally during transcription
- Transcripts are sent to OpenAI API for summarization
- Output files are saved locally in the `output/` directory
- **Important**: Do not process confidential audio without proper authorization

### Rate Limiting

- OpenAI API has rate limits
- Implement appropriate backoff strategies
- Monitor API usage to avoid unexpected costs

## Security Updates

We release security updates as part of our regular release cycle:

- Critical vulnerabilities: Emergency release
- High severity: Next patch release
- Medium/Low severity: Next minor release

Subscribe to releases to stay informed:
- Watch this repository
- Star the repository for updates
- Enable GitHub notifications

## Disclosure Policy

- We follow coordinated vulnerability disclosure
- Security issues will be disclosed after a fix is available
- Credit will be given to researchers who report vulnerabilities
- We maintain a security changelog in release notes

## Security Scanning

This project uses:

- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **CodeQL**: Semantic code analysis
- **Dependabot**: Automated dependency updates

These tools run automatically in CI/CD pipelines.

## Acknowledgments

We'd like to thank the following security researchers for their contributions:

<!-- Add security researchers who have responsibly disclosed vulnerabilities -->

---

Thank you for helping keep Call2Action and its users safe!
