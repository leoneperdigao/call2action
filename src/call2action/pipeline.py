"""Main pipeline orchestration for the Call2Action system."""

from pathlib import Path

from call2action.config import Settings
from call2action.models import TranscriptResult
from call2action.transcriber import Transcriber
from call2action.summarizer import Summarizer


class TranscriptPipeline:
    """Orchestrates the complete transcript-to-summary-to-action pipeline."""

    def __init__(self, settings: Settings = None, silent: bool = False):
        """
        Initialize the pipeline with all components.

        Args:
            settings: Optional Settings object. If not provided, loads from environment.
            silent: If True, suppress verbose logging (useful for parallel processing)
        """
        self.settings = settings or Settings()
        self.transcriber = Transcriber(self.settings)
        self.summarizer = Summarizer(self.settings)
        self.silent = silent

    def process(self, audio_file: str | Path, save_output: bool = True, force_rerun: bool = False) -> TranscriptResult:
        """
        Process an audio/video file through the complete pipeline.

        Args:
            audio_file: Path to the audio/video file to process
            save_output: Whether to save the results to disk
            force_rerun: If True, re-run all steps even if cached results exist

        Returns:
            TranscriptResult containing all processed information
        """
        audio_path = Path(audio_file)
        
        if not self.silent:
            print(f"\n{'='*60}")
            print(f"🚀 Starting pipeline for: {audio_path.name}")
            print(f"{'='*60}\n")

        # Step 1: Transcribe audio (or load from cache)
        if not self.silent:
            print("📍 Step 1: Transcription")
        
        # Try to load existing transcript if not forcing re-run
        transcript = None
        segments = None
        if not force_rerun:
            cached = TranscriptResult.load_transcript(audio_path, self.settings.output_dir)
            if cached:
                transcript, segments = cached
                if not self.silent:
                    print(f"✅ Found existing transcription (skipping Whisper)")
                    print(f"   - {len(segments)} segments loaded from cache")
                    print(f"Transcript preview: {transcript[:200]}...\n")
        
        # If no cache or force_rerun, transcribe
        if transcript is None:
            transcript, segments = self.transcriber.transcribe(audio_path)
            if not self.silent:
                print(f"Transcript preview: {transcript[:200]}...\n")
            
            # Save transcript immediately to avoid losing progress
            if save_output:
                TranscriptResult.save_transcript_only(audio_path, transcript, segments, self.settings.output_dir)
                if not self.silent:
                    print()

        # Step 2: Generate summary (or load from cache)
        if not self.silent:
            print("📍 Step 2: Summarization")
        
        summary = None
        call_to_action = []  # Empty list - no longer generating call-to-action
        
        # Try to load existing summary if not forcing re-run
        if not force_rerun:
            cached_summary = TranscriptResult.load_summary(audio_path, self.settings.output_dir)
            if cached_summary:
                summary, call_to_action = cached_summary
                if not self.silent:
                    print(f"✅ Found existing summary (skipping OpenAI)")
                    print(f"Summary preview: {summary[:200]}...\n")
        
        # If no cached summary, generate it
        if summary is None:
            summary = self.summarizer.generate_summary(transcript)
            if not self.silent:
                print(f"Summary preview: {summary[:200]}...\n")

        # Create result object
        result = TranscriptResult(
            audio_file=audio_path,
            transcript=transcript,
            segments=segments,
            summary=summary,
            call_to_action=call_to_action,
            metadata={
                "whisper_model": self.settings.whisper_model_size,
                "openai_model": self.settings.openai_model,
            },
        )

        # Save results if requested
        if save_output:
            # Save the complete result (including summary and actions)
            result.save(self.settings.output_dir)
            if not self.silent:
                print()

        if not self.silent:
            print(f"{'='*60}")
            print("✅ Pipeline completed successfully!")
            print(f"{'='*60}\n")

        return result
