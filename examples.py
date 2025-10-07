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

if __name__ == "__main__":
    main()
