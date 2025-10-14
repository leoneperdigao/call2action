# GitHub Configuration

This directory contains all GitHub-specific configuration files for the Call2Action project.

## Contents

### Workflows (`.github/workflows/`)

#### `ci.yml` - Continuous Integration
Runs on every push and pull request to main, develop, and feature branches.

**Jobs:**
- **Lint**: Checks code formatting with Black and linting with Ruff
- **Test**: Runs tests across multiple OS (Ubuntu, macOS) and Python versions (3.10-3.13)
  - Includes code coverage reporting with Codecov
- **Type Check**: Runs mypy for static type checking
- **Security**: Runs Bandit for security linting and Safety for dependency vulnerability checks

**Required Secrets:**
- `OPENAI_API_KEY`: OpenAI API key for running tests (optional, tests will skip if not present)
- `CODECOV_TOKEN`: Token for uploading coverage reports to Codecov

#### `release.yml` - Release Automation
Triggered when a version tag (v*.*.*) is pushed.

**Jobs:**
- Builds the Python package
- Creates a GitHub release with release notes
- Publishes to PyPI

**Required Secrets:**
- `PYPI_API_TOKEN`: Token for publishing to PyPI

#### `codeql.yml` - Code Security Analysis
Runs CodeQL security analysis on pushes, pull requests, and weekly schedule.

**Purpose:**
- Identifies security vulnerabilities
- Detects code quality issues
- Runs security-and-quality queries

### Issue Templates (`.github/ISSUE_TEMPLATE/`)

#### `bug_report.yml`
Structured template for reporting bugs with fields for:
- Bug description
- Reproduction steps
- Expected vs actual behavior
- Environment details (Python version, OS, package version)
- Configuration details
- Error logs

#### `feature_request.yml`
Template for proposing new features with:
- Problem statement
- Proposed solution
- Alternatives considered
- Use case description
- Priority level

#### `config.yml`
Configuration for issue templates with links to:
- GitHub Discussions
- Documentation
- Configuration help

### Other Configuration Files

#### `CODEOWNERS`
Defines code ownership and automatic review requests.
- Default owner: @leoneperdigao
- Ensures proper review for all changes

#### `PULL_REQUEST_TEMPLATE.md`
Comprehensive PR template with sections for:
- Description and type of change
- Related issues
- Testing details and coverage
- Configuration changes checklist
- Breaking changes documentation

#### `copilot-instructions.md`
**Robust GitHub Copilot configuration** that defines:
- Project architecture and patterns
- Code standards and style guidelines
- Type hints and documentation requirements
- Testing best practices
- Common code patterns and examples
- Security considerations
- Performance optimization guidelines

This ensures consistent, high-quality AI-assisted code generation that follows project standards.

#### `dependabot.yml`
Automated dependency updates configuration:
- Weekly updates for Python dependencies
- Weekly updates for GitHub Actions
- Automatic labeling and commit message formatting
- Ignores major version updates to maintain stability

#### `FUNDING.yml`
Placeholder for project funding/sponsorship options.

## Setup Instructions

### 1. Required Secrets

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

```
OPENAI_API_KEY          # For running integration tests (optional)
CODECOV_TOKEN           # For code coverage reporting (optional)
PYPI_API_TOKEN          # For automated releases to PyPI
```

### 2. Enable Workflows

Ensure GitHub Actions are enabled in your repository settings.

### 3. Configure Branch Protection

Recommended branch protection rules for `main` and `develop`:

**Main Branch:**
- Require pull request reviews before merging
- Require status checks to pass (CI, Type Check, Security)
- Require branches to be up to date before merging
- Require linear history
- Do not allow force pushes
- Do not allow deletions

**Develop Branch:**
- Require status checks to pass (CI, Type Check)
- Require branches to be up to date before merging

### 4. Enable Dependabot

Dependabot is automatically configured via `dependabot.yml`. Ensure Dependabot alerts are enabled in:
- Settings > Code security and analysis > Dependabot alerts
- Settings > Code security and analysis > Dependabot security updates

### 5. Enable CodeQL

CodeQL will run automatically via the workflow. For additional security features:
- Settings > Code security and analysis > CodeQL analysis

### 6. Configure GitHub Copilot

The `copilot-instructions.md` file will automatically be used by GitHub Copilot to provide context-aware suggestions. No additional setup required for users with Copilot enabled.

## Usage

### Running CI Locally

Before pushing, you can run the CI checks locally:

```bash
# Formatting check
black --check src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/call2action --ignore-missing-imports

# Tests with coverage
pytest tests/ -v --cov=src/call2action --cov-report=term

# Security checks
bandit -r src/call2action
safety check
```

### Creating a Release

To create a new release:

1. Update version in `pyproject.toml`
2. Commit changes: `git commit -am "chore: bump version to X.Y.Z"`
3. Create and push tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. The release workflow will automatically:
   - Build the package
   - Create a GitHub release
   - Publish to PyPI

### Managing Dependencies

Dependabot will automatically create PRs for dependency updates. Review and merge them regularly to keep dependencies up-to-date.

## Monitoring

### CI Status

Monitor workflow runs in the "Actions" tab of your repository.

### Code Coverage

View coverage reports at: https://codecov.io/gh/leoneperdigao/call2action

### Security Alerts

Check security alerts in:
- Settings > Code security and analysis
- Security tab > Dependabot alerts
- Security tab > Code scanning alerts

## Contributing

When contributing:

1. Follow the PR template
2. Ensure all CI checks pass
3. Maintain or improve code coverage
4. Follow the coding standards in `copilot-instructions.md`
5. Update documentation as needed

## Troubleshooting

### CI Failing

**Black/Ruff Errors:**
```bash
# Auto-fix formatting
black src/ tests/
ruff check --fix src/ tests/
```

**Test Failures:**
```bash
# Run tests locally with verbose output
pytest tests/ -v -s
```

**Type Errors:**
```bash
# Check types locally
mypy src/call2action --ignore-missing-imports
```

### Dependabot Issues

If Dependabot PRs are failing:
1. Check the logs in the PR
2. Test the update locally
3. May need to update code for compatibility

### Release Issues

If release workflow fails:
1. Verify `PYPI_API_TOKEN` is set correctly
2. Check that version number is unique
3. Ensure build passes locally: `python -m build`

## Best Practices

1. **Never commit secrets** - Use environment variables and GitHub Secrets
2. **Keep dependencies updated** - Review Dependabot PRs regularly
3. **Monitor security alerts** - Address vulnerabilities promptly
4. **Maintain test coverage** - Aim for >80% coverage
5. **Write descriptive commits** - Use conventional commits format
6. **Review CI logs** - Understand why builds fail
7. **Update documentation** - Keep this README and others up-to-date

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
