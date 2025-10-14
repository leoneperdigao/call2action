# Contributing to Call2Action

Thank you for your interest in contributing to Call2Action! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Ways to Contribute

- 🐛 Report bugs
- ✨ Suggest new features
- 📝 Improve documentation
- 🔧 Fix issues
- ✅ Add tests
- 🎨 Improve UI/UX
- 🌍 Add translations or language support

### Before You Start

1. Check existing [issues](https://github.com/leoneperdigao/call2action/issues) and [pull requests](https://github.com/leoneperdigao/call2action/pulls)
2. For major changes, open an issue first to discuss your idea
3. For bug fixes, you can submit a PR directly

## Development Setup

### Prerequisites

- Python 3.10 or higher
- `uv` package manager ([installation guide](https://github.com/astral-sh/uv))
- Git
- OpenAI API key (for testing)

### Setup Steps

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/call2action.git
   cd call2action
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/leoneperdigao/call2action.git
   ```

3. **Install Dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

5. **Verify Setup**
   ```bash
   pytest tests/ -v
   black --check src/ tests/
   ruff check src/ tests/
   ```

## Making Changes

### Branch Naming

Use descriptive branch names following this pattern:

- `feature/description-of-feature` - New features
- `bugfix/description-of-bug` - Bug fixes
- `hotfix/description-of-urgent-fix` - Urgent production fixes
- `docs/description-of-docs-change` - Documentation updates
- `refactor/description-of-refactor` - Code refactoring

Example: `feature/add-subtitle-generation`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```bash
feat(summarizer): add support for hierarchical summarization
fix(transcriber): handle empty audio files gracefully
docs(readme): update installation instructions
test(pipeline): add integration tests for full pipeline
```

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following project standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest tests/ -v --cov=src/call2action
   
   # Check formatting
   black src/ tests/
   
   # Run linter
   ruff check src/ tests/
   
   # Type checking
   mypy src/call2action --ignore-missing-imports
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```

5. **Keep Your Branch Updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

## Submitting Changes

### Pull Request Process

1. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template completely

2. **PR Requirements**
   - [ ] All tests pass
   - [ ] Code follows style guidelines (Black, Ruff)
   - [ ] New code has tests
   - [ ] Documentation is updated
   - [ ] PR description is complete
   - [ ] Commits follow conventional format

3. **Review Process**
   - Maintainers will review your PR
   - Address any requested changes
   - Keep the PR updated with main branch
   - Be responsive to feedback

4. **After Merge**
   - Delete your feature branch
   - Pull latest changes from upstream
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Coding Standards

### Python Style Guide

Follow the guidelines in `.github/copilot-instructions.md`:

- **Line length**: 100 characters
- **Formatter**: Black
- **Linter**: Ruff
- **Type hints**: Required for all functions
- **Docstrings**: Google-style for all public APIs

### Code Quality

```python
# Good example with type hints and docstring
from __future__ import annotations

def process_transcript(text: str, max_length: int = 1000) -> str:
    """Process and truncate transcript text.
    
    Args:
        text: The transcript text to process.
        max_length: Maximum length of output text.
        
    Returns:
        Processed transcript text.
        
    Raises:
        ValueError: If text is empty.
    """
    if not text:
        raise ValueError("Text cannot be empty")
    return text[:max_length]
```

### Project Structure

- `src/call2action/`: Source code
  - `config.py`: Configuration and settings
  - `models.py`: Pydantic data models
  - `pipeline.py`: Main processing pipeline
  - `transcriber.py`: Whisper integration
  - `summarizer.py`: LangChain/OpenAI integration
  - `prompts.py`: Prompt management

- `tests/`: Test files mirroring source structure
- `output/`: Generated outputs (not committed)

## Testing Guidelines

### Writing Tests

```python
import pytest
from call2action.models import TranscriptSegment

def test_transcript_segment_creation():
    """Test creating a transcript segment."""
    segment = TranscriptSegment(
        start=0.0,
        end=5.0,
        text="Hello, world!"
    )
    assert segment.start == 0.0
    assert segment.end == 5.0
    assert segment.text == "Hello, world!"

def test_transcript_segment_validation():
    """Test segment validation."""
    with pytest.raises(ValueError):
        TranscriptSegment(start=5.0, end=0.0, text="Invalid")
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pipeline.py -v

# Run with coverage
pytest tests/ --cov=src/call2action --cov-report=term

# Run only failed tests
pytest tests/ --lf
```

### Test Coverage

- Aim for >80% code coverage
- Test both success and failure cases
- Include edge cases
- Mock external dependencies (OpenAI, Whisper)

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include usage examples for complex functionality
- Keep comments up-to-date with code changes

### Project Documentation

Update relevant documentation when:
- Adding new features
- Changing configuration options
- Modifying CLI interface
- Updating dependencies
- Changing installation process

Files to update:
- `README.md`: Main project documentation
- `PROMPTS_README.md`: Prompt configuration guide
- `.github/copilot-instructions.md`: AI assistant guidelines
- Inline code comments

## Community

### Getting Help

- 💬 [GitHub Discussions](https://github.com/leoneperdigao/call2action/discussions) - Ask questions
- 🐛 [GitHub Issues](https://github.com/leoneperdigao/call2action/issues) - Report bugs
- 📚 [Documentation](https://github.com/leoneperdigao/call2action/blob/main/README.md) - Read docs

### Staying Updated

- Watch the repository for notifications
- Star the repository to bookmark it
- Follow the project for updates

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in the changelog
- Added to contributors list (coming soon)

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Open a new issue with the question label

---

Thank you for contributing to Call2Action! Your efforts help make this project better for everyone.
