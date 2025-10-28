"""Data models for the Call2Action pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


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
    def load_transcript(audio_file: Path, output_dir: Path) -> Optional[Tuple[str, List['TranscriptSegment']]]:
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
    def load_summary(audio_file: Path, output_dir: Path) -> Optional[Tuple[str, List[str]]]:
        """Load existing summary from file.
        
        Args:
            audio_file: Original audio file path
            output_dir: Directory containing saved summaries
            
        Returns:
            Tuple of (summary text, empty list) or None if not found
        """
        summary_file = output_dir / f"{audio_file.stem}_summary.txt"
        
        if not summary_file.exists():
            return None
        
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            if not content:
                return None
            
            # Current format: just the summary text (no call-to-action section)
            # Return summary with empty actions list
            return content, []
            
        except Exception:
            return None


@dataclass
class VideoSummary:
    """Summary information for a single processed video."""
    
    video_file: Path
    date: Optional[datetime]
    transcript: str
    summary: str
    key_themes: List[str] = field(default_factory=list)
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


@dataclass
class PersonRole:
    """Information about a person and their role in the project."""
    
    name: str
    roles: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    mentions: int = 0


@dataclass
class ProjectComponent:
    """A technical component or system in the project."""
    
    name: str
    description: str
    related_people: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class TimelineEvent:
    """A significant event or decision in the project timeline."""
    
    date: Optional[datetime]
    title: str
    description: str
    event_type: str  # milestone, decision, discussion, issue
    related_videos: List[str] = field(default_factory=list)


@dataclass
class ProjectContext:
    """Aggregated analysis of project context from multiple videos."""
    
    project_overview: str
    key_themes: List[str] = field(default_factory=list)
    people: List[PersonRole] = field(default_factory=list)
    components: List[ProjectComponent] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    technical_stack: List[str] = field(default_factory=list)


@dataclass
class HandoverReport:
    """Complete handover documentation report."""
    
    project_context: ProjectContext
    executive_summary: str
    technical_summary: str
    video_summaries: List[VideoSummary]
    diagrams: Dict[str, str] = field(default_factory=dict)  # diagram_name -> mermaid_code
    generation_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, any] = field(default_factory=dict)
