# Call2Action - Video Transcript Pipeline

A Python project that transcribes video/audio files using Faster Whisper and generates AI-powered summaries using OpenAI's GPT models with advanced hierarchical summarization.

## Features

- 🎤 **Speech-to-Text**: Transcribe audio/video files using Faster Whisper
- 🤖 **AI Summarization**: Generate intelligent summaries using OpenAI GPT models with LangChain
- � **Hierarchical Summarization**: Automatically handles long transcripts by:
  - Splitting into manageable chunks
  - Processing chunks in parallel using LangChain's batch() method
  - Creating intermediate group summaries
  - Combining into a final cohesive summary
- ⚡ **Parallel Processing**: Efficient batch processing of transcript chunks
- �️ **Robust Error Handling**: Automatic retry logic for failed chunks and groups
- 💾 **Smart Caching**: Saves transcripts and summaries to avoid reprocessing
- 🌍 **Multi-language Support**: Automatically translates summaries to English
- 🐍 **Modern Python**: Uses `uv` for fast dependency management

## Prerequisites

- Python 3.10 or higher
- `uv` package manager ([installation guide](https://github.com/astral-sh/uv))
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd call2action
```

2. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

4. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Configuration

Edit the `.env` file with your settings:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE`: Temperature for generation (default: 0.7)
- `WHISPER_MODEL_SIZE`: Whisper model size (tiny, base, small, medium, large-v3)
- `WHISPER_DEVICE`: Device to use (cpu, cuda)
- `WHISPER_COMPUTE_TYPE`: Compute type (int8, float16, float32)
- `OUTPUT_DIR`: Directory for output files (default: output)
- `PROMPTS_FILE`: Path to prompts configuration file (default: prompts.yaml)

**Note**: For large transcripts, the summarizer automatically uses hierarchical processing with increased token limits (up to 8192 tokens for final summaries) to ensure complete summary generation.

### Customizing Prompts

All AI prompts are configured in `prompts.yaml`, making them easy to customize without modifying code. The prompts are designed to handle various meeting types (technical, business, planning, etc.) and generate structured summaries with:

- Meeting overview and context
- Identified participants
- Key discussion points
- Decisions made (or explicitly noting when none were made)
- Action items and next steps
- Open questions or concerns

For detailed information on customizing prompts, see [PROMPTS_README.md](PROMPTS_README.md).

## Usage

### Basic Usage

```python
from call2action.pipeline import TranscriptPipeline

# Initialize the pipeline
pipeline = TranscriptPipeline()

# Process a video/audio file
result = pipeline.process("path/to/your/video.mp4")

# Access results
print("Transcript:", result.transcript)
print("Summary:", result.summary)
# Note: call_to_action is no longer generated in the current version
```

### Command Line Interface

```bash
# Process a video file
python -m call2action.main path/to/your/video.mp4

# Force re-run even if cached results exist
python -m call2action.main path/to/your/video.mp4 --force-rerun
```

Output files are saved in the `output/` directory:
- `{filename}_transcript.txt` - Full transcript
- `{filename}_segments.txt` - Timestamped segments
- `{filename}_summary.txt` - AI-generated summary

### Advanced Usage

```python
from call2action.pipeline import TranscriptPipeline
from call2action.config import Settings

# Custom configuration
settings = Settings(
    whisper_model_size="medium",
    openai_model="gpt-4o",
    openai_temperature=0.5
)

pipeline = TranscriptPipeline(settings=settings)

# Process with options
result = pipeline.process(
    "video.mp4", 
    save_output=True,      # Save results to disk
    force_rerun=False      # Use cached results if available
)

# Access detailed results
print(f"Processed {len(result.segments)} segments")
print(f"Summary length: {len(result.summary)} characters")
```

## How It Works

### Hierarchical Summarization

For large transcripts (>10 chunks or >100K characters), the system uses a three-stage process:

1. **Chunk Processing**: 
   - Splits transcript into ~4000 character chunks with 200 character overlap
   - Processes all chunks in parallel using LangChain's batch() method
   - Each chunk gets a detailed summary (up to 4096 tokens)

2. **Group Summarization**:
   - Groups chunk summaries into batches of 6
   - Creates intermediate summaries for each group
   - Automatic retry logic for failed groups

3. **Final Combination**:
   - Combines all intermediate summaries into one cohesive summary
   - Uses increased token limit (8192) for comprehensive output
   - Ensures all content is in English regardless of source language

### Error Handling

The system includes robust error handling:
- Automatic retry for empty responses
- Fallback to concatenation if LLM calls fail
- Placeholder text for permanently failed chunks
- Graceful degradation to ensure you always get a result

## Project Structure

```
call2action/
├── src/
│   └── call2action/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       ├── models.py           # Data models
│       ├── prompts.py          # Prompt management from YAML
│       ├── transcriber.py      # Faster Whisper transcription
│       ├── summarizer.py       # OpenAI summarization
│       ├── pipeline.py         # Main pipeline orchestration
│       └── main.py            # CLI entry point
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py
├── prompts.yaml               # AI prompts configuration
├── pyproject.toml
├── .env.example
├── README.md
└── PROMPTS_README.md          # Prompts customization guide
```

## Development

Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
```

Lint code:
```bash
ruff check src/
```

## Performance Considerations

- **Whisper Models**: Larger models (medium, large-v3) are more accurate but slower
- **GPU Acceleration**: Use CUDA for faster transcription if available
- **Parallel Processing**: The summarizer automatically processes chunks in parallel
- **Caching**: Results are cached to avoid reprocessing (use `--force-rerun` to override)
- **Token Limits**: Summaries are configured with appropriate token limits:
  - Chunk summaries: 4096 tokens
  - Final summary: 8192 tokens

## Troubleshooting

### Empty Summaries
If you get empty summaries, check:
- Your OpenAI API key is valid
- The model supports the requested token limits
- Network connectivity to OpenAI's API

The system includes automatic retry logic, but persistent failures may indicate API issues.

### Slow Processing
- Try a smaller Whisper model (base instead of large-v3)
- Use GPU acceleration if available
- Check your internet connection for OpenAI API calls

## License

MIT License
