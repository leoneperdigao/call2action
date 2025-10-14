# GitHub Copilot Instructions for Call2Action

## Project Overview

Call2Action is a Python-based AI-powered video transcript pipeline that:
- Transcribes audio/video files using Faster Whisper
- Generates intelligent summaries using OpenAI GPT models with LangChain
- Implements hierarchical summarization for long transcripts
- Processes chunks in parallel for efficiency
- Provides configurable prompts via YAML

## Code Standards and Style

### Python Version
- **Required**: Python 3.10+
- Use modern Python features (type hints, dataclasses, pathlib, etc.)

### Code Formatting
- **Line length**: 100 characters (Black and Ruff configured)
- **Formatter**: Black with target versions py310, py311, py312
- **Linter**: Ruff with py310 target
- Use double quotes for strings
- Use trailing commas in multi-line structures

### Type Hints
- Always use type hints for function parameters and return values
- Use `from __future__ import annotations` for forward references
- Prefer modern union syntax: `str | None` over `Optional[str]`
- Use Pydantic models for configuration and data structures

### Imports
- Group imports: standard library, third-party, local
- Use absolute imports from `call2action.*`
- Avoid wildcard imports

### Documentation
- Use docstrings for all modules, classes, and functions
- Format: Google-style docstrings
- Include parameter types, return types, and exceptions
- Add usage examples for complex functions

## Architecture Patterns

### Configuration Management
- Use Pydantic Settings for environment-based configuration
- All settings in `config.py` with sensible defaults
- Support `.env` files for local development
- Configuration should be loaded from `prompts.yaml` for AI prompts

### Error Handling
- Use specific exception types, not bare `except:`
- Implement retry logic for external API calls (OpenAI, Whisper)
- Provide clear error messages with context
- Log errors appropriately using rich console output

### Data Models
- Use Pydantic models for all data structures
- Define models in `models.py`
- Include field descriptions and validation
- Use `model_validate` for parsing external data

### Processing Pipeline
- Follow single responsibility principle
- Each component (`Transcriber`, `Summarizer`) should be independent
- Use dependency injection for testing
- Implement caching to avoid reprocessing (save to `output/` directory)

### AI Integration
- Use LangChain for LLM interactions
- Implement hierarchical summarization for long texts
- Process chunks in parallel using `batch()` method
- Handle token limits gracefully (current: 8192 for final summaries)
- All prompts should be configurable via `prompts.yaml`

## Testing Guidelines

### Test Structure
- Place tests in `tests/` directory
- Mirror source structure: `test_<module>.py`
- Use pytest fixtures for reusable test data
- Mock external dependencies (OpenAI API, Whisper)

### Test Coverage
- Aim for >80% code coverage
- Test happy paths and error cases
- Include edge cases (empty inputs, very long inputs, etc.)
- Test configuration loading and validation

### Test Naming
- Use descriptive names: `test_<what>_<scenario>_<expected>`
- Example: `test_summarizer_handles_long_transcript_with_chunking`

## Dependencies

### Package Management
- Use `uv` for dependency management (fast, modern)
- Define dependencies in `pyproject.toml`
- Separate `dev` dependencies from runtime dependencies
- Pin major versions, allow minor/patch updates

### Key Dependencies
- **faster-whisper**: Speech-to-text transcription
- **openai**: OpenAI API client
- **langchain**: LLM orchestration and chain management
- **pydantic**: Data validation and settings management
- **rich**: Beautiful terminal output
- **pyyaml**: YAML configuration parsing

## File Organization

### Source Code
```
src/call2action/
├── __init__.py          # Package initialization
├── config.py            # Settings and configuration
├── models.py            # Pydantic data models
├── pipeline.py          # Main processing pipeline
├── transcriber.py       # Whisper transcription logic
├── summarizer.py        # LangChain summarization logic
└── prompts.py           # Prompt template management
```

### Output Structure
- Save transcripts: `output/<timestamp>_transcript.txt`
- Save segments: `output/<timestamp>_segments.txt`
- Save summaries: `output/<timestamp>_summary.txt`
- Use ISO format timestamps with sanitization

### Configuration Files
- `prompts.yaml`: AI prompt templates (user-customizable)
- `.env`: Environment variables (not committed)
- `pyproject.toml`: Project metadata and dependencies

## Common Patterns

### Caching Pattern
```python
output_file = self._get_output_path(audio_file, "transcript")
if output_file.exists() and not force_rerun:
    return self._load_from_cache(output_file)
# ... process and save ...
```

### Retry Pattern
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def api_call_with_retry():
    # ... API call logic ...
```

### Rich Console Output
```python
from rich.console import Console
from rich.progress import track

console = Console()
console.print("[bold green]✓[/bold green] Success message")
for item in track(items, description="Processing..."):
    # ... process item ...
```

### LangChain Integration
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model=self.settings.openai_model)
prompt = ChatPromptTemplate.from_messages([...])
chain = prompt | llm
result = chain.invoke({"input": data})
```

## AI Prompt Design

### Prompt Structure
- Load all prompts from `prompts.yaml`
- Use system and user message separation
- Include clear instructions and examples
- Support multi-language transcripts (translate to English)
- Handle various meeting types (technical, business, planning)

### Prompt Outputs
- Meeting overview and context
- Identified participants
- Key discussion points
- Decisions made (explicitly note when none were made)
- Action items and next steps
- Open questions or concerns

## CLI Design

### Command Structure
```bash
python -m call2action.main <audio_file> [--force-rerun]
```

### Output Format
- Use rich formatting for visual appeal
- Show progress indicators for long operations
- Display summary information at the end
- Include file paths for saved outputs
- Handle errors gracefully with clear messages

## Security Considerations

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all external inputs
- Sanitize filenames to prevent path traversal
- Use secure defaults for API configurations

## Performance Best Practices

- Cache expensive operations (transcription, summarization)
- Process transcript chunks in parallel
- Use streaming for large file operations
- Set appropriate timeouts for API calls
- Monitor token usage for cost optimization

## When Suggesting Code

1. **Follow existing patterns**: Match the style and structure of existing code
2. **Include type hints**: Always provide complete type annotations
3. **Add documentation**: Include docstrings and inline comments
4. **Handle errors**: Implement proper error handling and validation
5. **Write tests**: Suggest corresponding test cases for new functionality
6. **Consider performance**: Optimize for speed and memory usage
7. **Update configuration**: If adding features, update `prompts.yaml` or settings
8. **Maintain backward compatibility**: Don't break existing APIs without discussion

## Special Considerations

### Whisper Model Selection
- Default: `large-v3` for best accuracy
- Consider `base` for faster processing in tests
- Device selection: `cpu` vs `cuda` based on availability
- Compute type: `int8` for CPU, `float16` for GPU

### OpenAI Model Selection
- Default: `gpt-4o-mini` for cost-effectiveness
- Consider `gpt-4` for higher quality summaries
- Monitor token usage and costs
- Implement fallback strategies for rate limits

### Hierarchical Summarization
- Split large transcripts into chunks (default: 6000 tokens)
- Process chunks in parallel for speed
- Create intermediate group summaries
- Combine into final cohesive summary
- Handle failed chunks with retry logic

## Version Control

- Branch naming: `feature/`, `bugfix/`, `hotfix/`
- Commit messages: Use conventional commits format
- PR descriptions: Include context, changes, and testing notes
- Keep commits focused and atomic
