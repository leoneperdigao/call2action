"""
Example script demonstrating how to use the Call2Action pipeline.
"""

from pathlib import Path
from call2action.pipeline import TranscriptPipeline
from call2action.config import Settings

def main():
    # Example 1: Basic usage with default settings
    print("=== Example 1: Basic Usage ===\n")
    
    pipeline = TranscriptPipeline()
    
    # Process a video file (replace with your actual file)
    # result = pipeline.process("path/to/your/video.mp4")
    # print(f"Summary: {result.summary}")
    # print(f"Actions: {result.call_to_action}")
    
    print("To use this example, uncomment the lines above and provide a video file path.\n")
    
    # Example 2: Custom configuration
    print("=== Example 2: Custom Configuration ===\n")
    
    custom_settings = Settings(
        openai_api_key="your-api-key-here",
        openai_model="gpt-4o",  # Use a more powerful model
        whisper_model_size="medium",  # Use a larger Whisper model for better accuracy
        whisper_device="cpu",  # Change to "cuda" if you have a GPU
    )
    
    custom_pipeline = TranscriptPipeline(settings=custom_settings)
    # result = custom_pipeline.process("path/to/your/video.mp4")
    
    print("This example shows how to customize the pipeline settings.\n")
    
    # Example 3: Process without saving to disk
    print("=== Example 3: Process Without Saving ===\n")
    
    pipeline = TranscriptPipeline()
    # result = pipeline.process("path/to/your/video.mp4", save_output=False)
    # print(result.transcript)
    
    print("Set save_output=False to process without saving results to disk.\n")
    
    # Example 4: Access individual components
    print("=== Example 4: Using Individual Components ===\n")
    
    from call2action.transcriber import Transcriber
    from call2action.summarizer import Summarizer
    
    settings = Settings()
    
    # Use transcriber separately
    transcriber = Transcriber(settings)
    # transcript, segments = transcriber.transcribe("path/to/audio.mp4")
    
    # Use summarizer separately
    summarizer = Summarizer(settings)
    # summary = summarizer.generate_summary(transcript)
    # actions = summarizer.generate_call_to_action(transcript, summary)
    
    print("You can use individual components separately for more control.\n")
    
    # Example 5: Generate Handover Documentation
    print("=== Example 5: Project Handover Documentation ===\n")
    
    from call2action.handover_pipeline import HandoverPipeline
    
    handover_pipeline = HandoverPipeline()
    
    # Generate handover from all videos in a directory
    # report = handover_pipeline.generate_handover("path/to/videos/")
    # print(f"Generated report with {len(report.video_summaries)} videos")
    # print(f"Project overview: {report.project_context.project_overview[:200]}...")
    
    print("This generates comprehensive handover documentation from multiple videos.")
    print("Outputs: HTML report with executive/technical views and diagrams.\n")
    
    # Example 6: Custom Handover Configuration
    print("=== Example 6: Custom Handover Output ===\n")
    
    custom_settings = Settings(
        output_dir=Path("custom_output"),
        handover_output_file="team_handover.html",
        include_individual_summaries=True,
        openai_model="gpt-4o",  # Use more powerful model for better analysis
    )
    
    handover_pipeline = HandoverPipeline(settings=custom_settings)
    # report = handover_pipeline.generate_handover("path/to/videos/")
    
    print("You can customize output directory and filename for handover reports.\n")
    
    # Example 7: Parallel Processing Configuration
    print("=== Example 7: Parallel Processing for Many Videos ===\n")
    
    # For large video collections, increase parallel workers
    parallel_settings = Settings(
        max_parallel_videos=8,  # Process 8 videos at once (requires 8+ cores)
        whisper_model_size="base",  # Use faster model
        whisper_device="cuda",  # Use GPU for even faster processing
    )
    
    fast_pipeline = HandoverPipeline(settings=parallel_settings)
    # report = fast_pipeline.generate_handover("path/to/40-videos/")
    
    print("Process many videos in parallel for dramatic speed improvements.")
    print("Example: 40 videos in ~1.5 hours instead of ~10 hours!\n")
    print("\nPerformance tips:")
    print("- Use max_parallel_videos = number of CPU cores")
    print("- Enable CUDA if you have an NVIDIA GPU")
    print("- Use smaller Whisper models (base/small) for speed")
    print("- Cached videos are automatically skipped for instant regeneration\n")
    
    # Example 8: Smart Caching Behavior
    print("=== Example 8: Smart Caching for Fast Regeneration ===\n")
    
    print("The handover pipeline intelligently uses cached results:")
    print("\nFirst run (40 videos):")
    print("  - Transcribes and summarizes all 40 videos")
    print("  - Takes ~2.5 hours (4 workers) or ~1.5 hours (8 workers)")
    print("  - Saves transcript and summary for each video")
    print("\nSubsequent runs (without --force-rerun):")
    print("  - Loads existing summaries from cache (instant)")
    print("  - Only regenerates the final handover report")
    print("  - Takes ~2 minutes total!")
    print("\nTo reprocess everything:")
    print("  python -m call2action.main handover path/to/videos/ --force-rerun")
    print("\nThis means you can:")
    print("  - Tweak prompts and regenerate reports quickly")
    print("  - Add new videos without reprocessing old ones")
    print("  - Experiment with different report formats efficiently\n")

if __name__ == "__main__":
    main()
