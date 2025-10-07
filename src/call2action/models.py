"""Data models for the Call2Action pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class TranscriptSegment:
    """A single segment of transcribed text."""

    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    """Complete result from the transcript pipeline."""

    audio_file: Path
    transcript: str
    segments: List[TranscriptSegment]
    summary: str
    call_to_action: List[str]
    metadata: Optional[dict] = None

    def save(self, output_dir: Path) -> None:
        """Save the transcript result to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save transcript
        transcript_file = output_dir / f"{self.audio_file.stem}_transcript.txt"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(self.transcript)
        
        # Save summary (no longer including call-to-action)
        summary_file = output_dir / f"{self.audio_file.stem}_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(self.summary)
        
        # Save detailed segments
        segments_file = output_dir / f"{self.audio_file.stem}_segments.txt"
        with open(segments_file, "w", encoding="utf-8") as f:
            for segment in self.segments:
                f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")
        
        print(f"✅ Results saved to {output_dir}/")

    @staticmethod
    def load_transcript(audio_file: Path, output_dir: Path) -> tuple[str, List['TranscriptSegment']] | None:
        """Load existing transcript and segments from files.
        
        Args:
            audio_file: Original audio file path
            output_dir: Directory containing saved transcripts
            
        Returns:
            Tuple of (transcript text, segments list) or None if not found
        """
        transcript_file = output_dir / f"{audio_file.stem}_transcript.txt"
        segments_file = output_dir / f"{audio_file.stem}_segments.txt"
        
        if not transcript_file.exists() or not segments_file.exists():
            return None
        
        # Load transcript
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
        
        # Load segments
        segments = []
        with open(segments_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Parse format: [0.00s -> 5.20s] text
                try:
                    time_part, text = line.split("] ", 1)
                    times = time_part.strip("[").split(" -> ")
                    start = float(times[0].rstrip("s"))
                    end = float(times[1].rstrip("s"))
                    segments.append(TranscriptSegment(start=start, end=end, text=text))
                except (ValueError, IndexError):
                    continue
        
        return transcript, segments

    @staticmethod
    def save_transcript_only(audio_file: Path, transcript: str, segments: List['TranscriptSegment'], output_dir: Path) -> None:
        """Save only the transcript and segments to files.
        
        Args:
            audio_file: Original audio file path
            transcript: Full transcript text
            segments: List of transcript segments
            output_dir: Directory to save files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save transcript
        transcript_file = output_dir / f"{audio_file.stem}_transcript.txt"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # Save detailed segments
        segments_file = output_dir / f"{audio_file.stem}_segments.txt"
        with open(segments_file, "w", encoding="utf-8") as f:
            for segment in segments:
                f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")
        
        print(f"💾 Transcript saved to {output_dir}/")

    @staticmethod
    def load_summary(audio_file: Path, output_dir: Path) -> tuple[str, List[str]] | None:
        """Load existing summary and call-to-action from file.
        
        Args:
            audio_file: Original audio file path
            output_dir: Directory containing saved summaries
            
        Returns:
            Tuple of (summary text, list of actions) or None if not found
        """
        summary_file = output_dir / f"{audio_file.stem}_summary.txt"
        
        if not summary_file.exists():
            return None
        
        with open(summary_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse the summary file
        try:
            parts = content.split("=== CALL TO ACTION ===")
            if len(parts) != 2:
                return None
            
            summary_part = parts[0].replace("=== SUMMARY ===", "").strip()
            actions_part = parts[1].strip()
            
            # Parse actions
            actions = []
            for line in actions_part.split("\n"):
                line = line.strip()
                if line and not line.startswith("==="):
                    # Remove numbering (e.g., "1. ", "2. ")
                    action = line.split(". ", 1)[-1] if ". " in line else line
                    actions.append(action)
            
            return summary_part, actions
        except Exception:
            return None
