"""Orchestrate the complete project handover documentation pipeline."""

import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

from call2action.config import Settings
from call2action.diagram_generator import DiagramGenerator
from call2action.handover_analyzer import HandoverAnalyzer
from call2action.html_generator import HtmlGenerator
from call2action.models import HandoverReport, ProjectContext, VideoSummary
from call2action.pipeline import TranscriptPipeline


def _process_single_video(video_file: Path, settings: Settings, force_rerun: bool) -> VideoSummary:
    """
    Process a single video file (designed to be called in parallel).
    
    Checks for existing summary first to avoid re-processing.
    
    Args:
        video_file: Path to video file
        settings: Application settings
        force_rerun: Whether to force re-processing
        
    Returns:
        VideoSummary object
    """
    try:
        # Extract date from filename
        date = _extract_date_from_filename(video_file.name)
        
        # Check if summary already exists (unless force_rerun)
        if not force_rerun:
            from call2action.models import TranscriptResult
            
            # Try to load existing transcript and summary
            cached_transcript = TranscriptResult.load_transcript(video_file, settings.output_dir)
            cached_summary = TranscriptResult.load_summary(video_file, settings.output_dir)
            
            if cached_transcript and cached_summary:
                transcript, segments = cached_transcript
                summary, call_to_action = cached_summary
                
                # Verify summary is not empty
                if not summary or not summary.strip():
                    # Fall through to reprocess
                    pass
                else:
                    # Create VideoSummary from cached data
                    video_summary = VideoSummary(
                        video_file=video_file,
                        date=date,
                        transcript=transcript,
                        summary=summary,
                        key_themes=[],
                        duration_seconds=None,
                        error=None,
                    )
                    
                    print(f"📦 Loaded from cache: {video_file.name}")
                    return video_summary
        
        # No cache or force_rerun - process through pipeline
        pipeline = TranscriptPipeline(settings=settings)
        
        # Process video
        result = pipeline.process(
            video_file, save_output=True, force_rerun=force_rerun
        )
        
        # Create VideoSummary
        video_summary = VideoSummary(
            video_file=video_file,
            date=date,
            transcript=result.transcript,
            summary=result.summary,
            key_themes=[],
            duration_seconds=None,
            error=None,
        )
        
        return video_summary
        
    except Exception as e:
        print(f"❌ Error processing {video_file.name}: {e}")
        
        # Create error video summary
        video_summary = VideoSummary(
            video_file=video_file,
            date=_extract_date_from_filename(video_file.name),
            transcript="",
            summary="",
            error=str(e),
        )
        return video_summary


def _extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Try to extract a date from the filename.
    
    Supports formats like:
    - 2025-10-27
    - 2025_10_27
    - 20251027
    - 2025-10-27_10-30-00
    
    Args:
        filename: The filename to parse
        
    Returns:
        datetime object or None if no date found
    """
    # Common date patterns
    patterns = [
        # YYYY-MM-DD HH-MM-SS or YYYY-MM-DD_HH-MM-SS
        r"(\d{4})-(\d{2})-(\d{2})[\s_-](\d{2})-(\d{2})-(\d{2})",
        # YYYY-MM-DD
        r"(\d{4})-(\d{2})-(\d{2})",
        # YYYY_MM_DD
        r"(\d{4})_(\d{2})_(\d{2})",
        # YYYYMMDD
        r"(\d{4})(\d{2})(\d{2})",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 6:
                    # Date and time
                    year, month, day, hour, minute, second = map(int, groups)
                    return datetime(year, month, day, hour, minute, second)
                elif len(groups) == 3:
                    # Date only
                    year, month, day = map(int, groups)
                    return datetime(year, month, day)
            except ValueError:
                # Invalid date values
                continue
    
    return None


class HandoverPipeline:
    """Orchestrates the complete handover documentation generation pipeline."""

    # Supported video formats
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv"}

    def __init__(self, settings: Settings = None):
        """
        Initialize the handover pipeline.

        Args:
            settings: Optional Settings object. If not provided, loads from environment.
        """
        self.settings = settings or Settings()
        self.transcript_pipeline = TranscriptPipeline(self.settings)
        self.analyzer = HandoverAnalyzer(self.settings)
        self.diagram_generator = DiagramGenerator()
        self.html_generator = HtmlGenerator()

    def generate_handover(
        self, video_directory: Path, force_rerun: bool = False
    ) -> HandoverReport:
        """
        Generate complete handover documentation from a directory of videos.

        Args:
            video_directory: Path to directory containing video files
            force_rerun: If True, re-run all steps even if cached results exist

        Returns:
            HandoverReport with complete documentation
        """
        video_dir = Path(video_directory)

        if not video_dir.exists() or not video_dir.is_dir():
            raise ValueError(f"Invalid video directory: {video_dir}")

        print("\n" + "=" * 60)
        print(f"🚀 Starting Handover Pipeline")
        print(f"📁 Video Directory: {video_dir}")
        print("=" * 60)

        # Step 1: Discover video files
        video_files = self._discover_videos(video_dir)

        if not video_files:
            raise ValueError(f"No video files found in {video_dir}")

        print(f"\n📹 Found {len(video_files)} video file(s)")

        # Step 2: Process each video
        video_summaries = self._process_videos(video_files, force_rerun)

        # Check if we have cached handover analysis (unless force_rerun)
        import json
        import hashlib
        
        cache_file = self.settings.output_dir / ".handover_cache.json"
        cache_key = self._generate_cache_key(video_summaries)
        
        cached_data = None
        if not force_rerun and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                if cached.get("cache_key") == cache_key:
                    print("\n💡 Found cached handover analysis - loading...")
                    cached_data = cached
            except Exception as e:
                print(f"⚠️  Could not load cache: {e}")

        if cached_data:
            # Load from cache
            print("📦 Using cached project analysis")
            project_context = self._deserialize_project_context(cached_data["project_context"])
            executive_summary = cached_data["executive_summary"]
            technical_summary = cached_data["technical_summary"]
        else:
            # Generate fresh analysis
            # Step 3: Analyze project context
            print("\n" + "=" * 60)
            project_context = self.analyzer.analyze_project_context(video_summaries)

            # Step 4: Generate persona-specific summaries
            executive_summary = self.analyzer.generate_executive_summary(project_context)
            technical_summary = self.analyzer.generate_technical_summary(project_context)
            
            # Cache the results
            self._save_cache(cache_file, cache_key, project_context, executive_summary, technical_summary)

        # Step 5: Generate diagrams
        print("\n📊 Generating visual diagrams...")
        diagrams = self.diagram_generator.generate_all_diagrams(
            project_context, video_summaries
        )
        print(f"✅ Generated {len(diagrams)} diagram(s)")

        # Step 6: Create handover report
        handover_report = HandoverReport(
            project_context=project_context,
            executive_summary=executive_summary,
            technical_summary=technical_summary,
            video_summaries=video_summaries,
            diagrams=diagrams,
            generation_date=datetime.now(),
            metadata={
                "video_directory": str(video_dir),
                "video_count": len(video_summaries),
                "force_rerun": force_rerun,
            },
        )

        # Step 7: Generate HTML report
        output_path = self.settings.output_dir / self.settings.handover_output_file
        self.html_generator.generate_html_report(handover_report, output_path)

        # Step 8: Export markdown versions
        markdown_dir = self.settings.output_dir / "handover_markdown"
        self.html_generator.export_markdown(handover_report, markdown_dir)

        print("\n" + "=" * 60)
        print("✅ Handover Pipeline Completed Successfully!")
        print("=" * 60)
        print(f"\n📄 HTML Report: {output_path}")
        print(f"📝 Markdown Files: {markdown_dir}")
        print()

        return handover_report

    def _discover_videos(self, directory: Path) -> List[Path]:
        """
        Discover all video files in the directory.

        Args:
            directory: Directory to search

        Returns:
            List of video file paths, sorted by name
        """
        video_files = []

        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() in self.VIDEO_EXTENSIONS:
                video_files.append(file)

        # Sort by name (which often includes dates)
        video_files.sort(key=lambda f: f.name)

        return video_files

    def _process_videos(
        self, video_files: List[Path], force_rerun: bool
    ) -> List[VideoSummary]:
        """
        Process each video file through the transcript pipeline in parallel.

        Args:
            video_files: List of video files to process
            force_rerun: Whether to force re-processing

        Returns:
            List of VideoSummary objects
        """
        video_summaries = []
        total_videos = len(video_files)
        
        print(f"\n🚀 Processing {total_videos} videos in parallel (max {self.settings.max_parallel_videos} at a time)...")
        if not force_rerun:
            print(f"💡 Using cached results where available (use --force-rerun to reprocess all)")
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=self.settings.max_parallel_videos) as executor:
            # Submit all tasks
            future_to_video = {
                executor.submit(_process_single_video, video_file, self.settings, force_rerun): video_file
                for video_file in video_files
            }
            
            # Process completed tasks as they finish
            completed = 0
            cached_count = 0
            processed_count = 0
            
            for future in as_completed(future_to_video):
                video_file = future_to_video[future]
                completed += 1
                
                try:
                    video_summary = future.result()
                    video_summaries.append(video_summary)
                    
                    if video_summary.error:
                        print(f"❌ [{completed}/{total_videos}] Failed: {video_file.name}")
                    else:
                        # Note: we don't get info here if it was cached, but the function prints it
                        print(f"✅ [{completed}/{total_videos}] Done: {video_file.name}")
                        
                except Exception as e:
                    print(f"❌ [{completed}/{total_videos}] Error processing {video_file.name}: {e}")
                    
                    # Create error video summary
                    video_summary = VideoSummary(
                        video_file=video_file,
                        date=_extract_date_from_filename(video_file.name),
                        transcript="",
                        summary="",
                        error=str(e),
                    )
                    video_summaries.append(video_summary)

        # Filter out videos with errors for analysis
        successful = [v for v in video_summaries if not v.error]
        print(f"\n✅ Successfully loaded: {len(successful)}/{len(video_summaries)} videos")

        if len(successful) == 0:
            raise ValueError("No videos were successfully processed")

        return video_summaries

    def _generate_cache_key(self, video_summaries: List[VideoSummary]) -> str:
        """Generate a cache key based on video summaries."""
        import hashlib
        
        # Create a key from video files and their modification times
        key_parts = []
        for video in video_summaries:
            key_parts.append(f"{video.video_file.name}:{len(video.summary)}")
        
        key_string = "|".join(sorted(key_parts))
        return hashlib.md5(key_string.encode()).hexdigest()

    def _save_cache(
        self,
        cache_file: Path,
        cache_key: str,
        project_context: ProjectContext,
        executive_summary: str,
        technical_summary: str,
    ) -> None:
        """Save handover analysis to cache."""
        import json
        from datetime import datetime
        
        try:
            cache_data = {
                "cache_key": cache_key,
                "generated_at": datetime.now().isoformat(),
                "project_context": self._serialize_project_context(project_context),
                "executive_summary": executive_summary,
                "technical_summary": technical_summary,
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Saved handover analysis to cache")
        except Exception as e:
            print(f"⚠️  Could not save cache: {e}")

    def _serialize_project_context(self, context: ProjectContext) -> dict:
        """Serialize ProjectContext to dict."""
        return {
            "project_overview": context.project_overview,
            "key_themes": context.key_themes,
            "people": [
                {
                    "name": p.name,
                    "roles": p.roles,
                    "components": p.components,
                    "mentions": p.mentions,
                }
                for p in context.people
            ],
            "components": [
                {
                    "name": c.name,
                    "description": c.description,
                    "related_people": c.related_people,
                    "technologies": c.technologies,
                    "relationships": c.relationships,
                }
                for c in context.components
            ],
            "timeline": [
                {
                    "date": e.date.isoformat() if e.date else None,
                    "title": e.title,
                    "description": e.description,
                    "event_type": e.event_type,
                    "related_videos": e.related_videos,
                }
                for e in context.timeline
            ],
            "decisions": context.decisions,
            "risks": context.risks,
            "open_questions": context.open_questions,
            "technical_stack": context.technical_stack,
        }

    def _deserialize_project_context(self, data: dict) -> ProjectContext:
        """Deserialize dict to ProjectContext."""
        from call2action.models import PersonRole, ProjectComponent, TimelineEvent, ProjectContext
        from datetime import datetime
        
        return ProjectContext(
            project_overview=data["project_overview"],
            key_themes=data["key_themes"],
            people=[
                PersonRole(
                    name=p["name"],
                    roles=p["roles"],
                    components=p["components"],
                    mentions=p["mentions"],
                )
                for p in data["people"]
            ],
            components=[
                ProjectComponent(
                    name=c["name"],
                    description=c["description"],
                    related_people=c["related_people"],
                    technologies=c["technologies"],
                    relationships=c["relationships"],
                )
                for c in data["components"]
            ],
            timeline=[
                TimelineEvent(
                    date=datetime.fromisoformat(e["date"]) if e["date"] else None,
                    title=e["title"],
                    description=e["description"],
                    event_type=e["event_type"],
                    related_videos=e["related_videos"],
                )
                for e in data["timeline"]
            ],
            decisions=data["decisions"],
            risks=data["risks"],
            open_questions=data["open_questions"],
            technical_stack=data["technical_stack"],
        )

