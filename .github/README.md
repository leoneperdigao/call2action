# .github Directory

This directory contains GitHub-specific configuration files for automated workflows, issue templates, and repository settings.

## 📁 Contents

### Workflows (`workflows/`)
- **`ci.yml`** - Continuous Integration pipeline
- **`codeql.yml`** - Security analysis
- **`release.yml`** - Automated releases

### Issue Templates (`ISSUE_TEMPLATE/`)
- **`bug_report.yml`** - Bug report template
- **`feature_request.yml`** - Feature request template
- **`config.yml`** - Issue template configuration

### Configuration Files
- **`copilot-instructions.md`** - GitHub Copilot AI configuration
- **`dependabot.yml`** - Automated dependency updates
- **`CODEOWNERS`** - Code ownership and review assignments
- **`PULL_REQUEST_TEMPLATE.md`** - Pull request template
- **`FUNDING.yml`** - Sponsorship configuration

### Documentation
- **Contributing Guide** → [`../docs/CONTRIBUTING.md`](../docs/CONTRIBUTING.md)
- **Security Policy** → [`../docs/SECURITY.md`](../docs/SECURITY.md)

> **Note**: GitHub looks for `CONTRIBUTING.md` and `SECURITY.md` in the `.github/` directory.
> We keep these in `/docs/` to avoid duplication. GitHub will still show the "Security" tab
> and link to contributing guidelines from the repository root.

## 📚 Full Documentation

For complete project documentation, see the [`/docs`](../docs) directory:
- [Contributing Guide](../docs/CONTRIBUTING.md)
- [Security Policy](../docs/SECURITY.md)
- [GitHub Configuration Guide](../docs/github-config.md)
- [GitHub Setup Instructions](../docs/github-setup.md)
- [GitHub Workflows Overview](../docs/github-overview.md)

## 🚀 Quick Start

1. **Enable workflows**: Workflows are automatically enabled
2. **Add secrets**: Settings > Secrets > Actions
   - `OPENAI_API_KEY`
   - `PYPI_API_TOKEN`
   - `CODECOV_TOKEN`
3. **Configure branch protection**: Settings > Branches
4. **Enable Dependabot**: Settings > Code security and analysis

For detailed setup instructions, see [`docs/github-setup.md`](../docs/github-setup.md).
