# Quick Start Guide

## Setup (One-Time)

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

2. **Configure your API key:**
   Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

## Usage

### Activate Virtual Environment
```bash
source .venv/bin/activate
```

### Process a Video/Audio File
```bash
python -m call2action.main path/to/your/video.mp4
```

### Using in Python Code
```python
from call2action.pipeline import TranscriptPipeline

pipeline = TranscriptPipeline()
result = pipeline.process("video.mp4")

print(result.summary)
print(result.call_to_action)
```

## Example Output Structure

After processing a file named `meeting.mp4`, you'll find in the `output/` directory:

- `meeting_transcript.txt` - Full transcript
- `meeting_summary.txt` - Summary and call-to-action items
- `meeting_segments.txt` - Timestamped segments

## Configuration Options

Edit `.env` to customize:

- `WHISPER_MODEL_SIZE` - Transcription accuracy (tiny, base, small, medium, large-v3)
- `OPENAI_MODEL` - GPT model to use (gpt-4o-mini, gpt-4o, gpt-4-turbo)
- `WHISPER_DEVICE` - Use GPU for faster processing (cpu or cuda)

## Troubleshooting

**Issue: "OpenAI API key not found"**
- Make sure you've added your API key to the `.env` file

**Issue: Slow transcription**
- Use a smaller Whisper model (tiny or base)
- Or use GPU by setting `WHISPER_DEVICE=cuda` (requires CUDA-compatible GPU)

**Issue: Out of memory**
- Use a smaller Whisper model
- Process shorter audio files
- Reduce `OPENAI_MAX_TOKENS` in `.env`
