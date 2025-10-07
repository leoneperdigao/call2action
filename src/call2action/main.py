"""Command-line interface for the Call2Action pipeline."""

import sys
from pathlib import Path

from call2action.pipeline import TranscriptPipeline


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print("Usage: python -m call2action.main <audio_file> [--force-rerun]")
        print("\nOptions:")
        print("  --force-rerun    Re-run all steps even if cached results exist")
        print("\nExample:")
        print("  python -m call2action.main path/to/video.mp4")
        print("  python -m call2action.main path/to/video.mp4 --force-rerun")
        sys.exit(1)

    audio_file = Path(sys.argv[1])
    force_rerun = "--force-rerun" in sys.argv

    if not audio_file.exists():
        print(f"❌ Error: File not found: {audio_file}")
        sys.exit(1)

    try:
        pipeline = TranscriptPipeline()
        result = pipeline.process(audio_file, force_rerun=force_rerun)
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        print(f"\n📄 Transcript ({len(result.transcript)} characters):")
        print("-" * 60)
        print(result.transcript[:500] + "..." if len(result.transcript) > 500 else result.transcript)
        print()
        
        print("📝 Summary:")
        print("-" * 60)
        print(result.summary)
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
