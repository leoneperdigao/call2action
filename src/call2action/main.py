"""Command-line interface for the Call2Action pipeline."""

import sys
from pathlib import Path

from call2action.pipeline import TranscriptPipeline
from call2action.handover_pipeline import HandoverPipeline


def print_usage():
    """Print CLI usage information."""
    print("Call2Action - Video Transcript and Handover Documentation Pipeline")
    print("\nUsage:")
    print("  Single video mode:")
    print("    python -m call2action.main <video_file> [--force-rerun]")
    print("\n  Handover documentation mode:")
    print("    python -m call2action.main handover <video_directory> [--force-rerun]")
    print("\nOptions:")
    print("  --force-rerun    Re-run all steps even if cached results exist")
    print("\nExamples:")
    print("  # Process a single video")
    print("  python -m call2action.main path/to/video.mp4")
    print("\n  # Generate handover documentation from multiple videos")
    print("  python -m call2action.main handover path/to/videos/")
    print("\n  # Force re-processing")
    print("  python -m call2action.main handover path/to/videos/ --force-rerun")


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # Check for help flag
    if sys.argv[1] in ["-h", "--help", "help"]:
        print_usage()
        sys.exit(0)

    # Check if handover mode
    if sys.argv[1] == "handover":
        run_handover_mode()
    else:
        run_single_video_mode()


def run_single_video_mode():
    """Run the pipeline for a single video file."""
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_handover_mode():
    """Run the handover documentation pipeline for multiple videos."""
    if len(sys.argv) < 3:
        print("❌ Error: Please provide a video directory")
        print("\nUsage: python -m call2action.main handover <video_directory> [--force-rerun]")
        sys.exit(1)

    video_directory = Path(sys.argv[2])
    force_rerun = "--force-rerun" in sys.argv

    if not video_directory.exists():
        print(f"❌ Error: Directory not found: {video_directory}")
        sys.exit(1)

    if not video_directory.is_dir():
        print(f"❌ Error: Not a directory: {video_directory}")
        sys.exit(1)

    try:
        pipeline = HandoverPipeline()
        report = pipeline.generate_handover(video_directory, force_rerun=force_rerun)
        
        print("\n" + "="*60)
        print("HANDOVER DOCUMENTATION GENERATED")
        print("="*60)
        print(f"\n📊 Project Overview:")
        print("-" * 60)
        overview = report.project_context.project_overview
        print(overview[:500] + "..." if len(overview) > 500 else overview)
        print()
        
        print(f"📈 Statistics:")
        print(f"  - Videos processed: {len(report.video_summaries)}")
        print(f"  - People identified: {len(report.project_context.people)}")
        print(f"  - Components identified: {len(report.project_context.components)}")
        print(f"  - Timeline events: {len(report.project_context.timeline)}")
        print(f"  - Diagrams generated: {len(report.diagrams)}")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
