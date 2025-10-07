"""Speech-to-text transcription using Faster Whisper."""

from pathlib import Path
from typing import List

from faster_whisper import WhisperModel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from call2action.config import Settings
from call2action.models import TranscriptSegment


class Transcriber:
    """Transcribes audio/video files using Faster Whisper."""

    def __init__(self, settings: Settings):
        """Initialize the transcriber with configuration."""
        self.settings = settings
        print(f"Loading Whisper model: {settings.whisper_model_size}...")
        self.model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        print("✅ Whisper model loaded successfully")

    def transcribe(self, audio_file: Path) -> tuple[str, List[TranscriptSegment]]:
        """
        Transcribe an audio/video file.

        Args:
            audio_file: Path to the audio/video file

        Returns:
            Tuple of (full transcript text, list of transcript segments)
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        print(f"🎤 Transcribing {audio_file.name}...")
        
        segments, info = self.model.transcribe(
            str(audio_file),
            beam_size=5,
            language=None,  # Auto-detect language
        )

        print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")

        transcript_segments = []
        full_text_parts = []

        # Process segments with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Processing audio segments..."),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("", total=None)
            
            for segment in segments:
                transcript_segment = TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                )
                transcript_segments.append(transcript_segment)
                full_text_parts.append(segment.text.strip())

        full_transcript = " ".join(full_text_parts)
        
        print(f"✅ Transcription complete: {len(transcript_segments)} segments")
        return full_transcript, transcript_segments
