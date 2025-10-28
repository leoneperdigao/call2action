"""Generate interactive HTML reports for project handover documentation."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from jinja2 import Template
from markupsafe import Markup

from call2action.models import HandoverReport


class HtmlGenerator:
    """Generates HTML reports from handover data."""

    def __init__(self, template_path: Path = None):
        """
        Initialize the HTML generator.

        Args:
            template_path: Path to HTML template file
        """
        if template_path is None:
            # Default to template in package
            template_path = (
                Path(__file__).parent / "templates" / "handover_template.html"
            )

        self.template_path = template_path

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        with open(self.template_path, "r", encoding="utf-8") as f:
            self.template = f.read()

    def generate_html_report(
        self, handover_report: HandoverReport, output_path: Path
    ) -> None:
        """
        Generate complete HTML report.

        Args:
            handover_report: The handover report data
            output_path: Where to save the HTML file
        """
        print("\n🎨 Generating HTML report...")

        # Prepare template variables
        variables = self._prepare_variables(handover_report)

        # Render template
        html = self._render_template(variables)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ HTML report saved to: {output_path}")

    def _prepare_variables(self, report: HandoverReport) -> Dict:
        """Prepare all template variables from the handover report."""
        context = report.project_context

        # Format dates
        generation_date = report.generation_date.strftime("%B %d, %Y at %H:%M")

        # Format summaries (convert markdown-like formatting to HTML)
        # Mark as safe HTML for Jinja2
        executive_summary = Markup(self._format_content(report.executive_summary))
        technical_summary = Markup(self._format_content(report.technical_summary))
        project_overview = Markup(self._format_content(context.project_overview))

        # Prepare people data
        people = []
        for person in context.people:
            people.append(
                {
                    "name": person.name,
                    "roles": person.roles,
                    "components": person.components,
                }
            )

        # Prepare components data
        components = []
        for component in context.components:
            components.append(
                {
                    "name": component.name,
                    "description": component.description,
                    "technologies": component.technologies,
                    "relationships": component.relationships,
                }
            )

        # Prepare timeline events
        timeline_events = []
        for event in context.timeline:
            timeline_events.append(
                {
                    "date": event.date.strftime("%Y-%m-%d") if event.date else None,
                    "title": event.title,
                    "description": event.description,
                    "event_type": event.event_type,
                }
            )

        # Prepare video summaries
        video_summaries = []
        
        for video in report.video_summaries:
            video_name = video.video_file.stem
            has_summary = bool(video.summary and video.summary.strip())
            has_error = bool(video.error)
            
            if has_error:
                # Include error videos with error message
                video_summaries.append(
                    {
                        "title": video_name,
                        "date": video.date.strftime("%B %d, %Y") if video.date else "Unknown",
                        "summary": Markup(f"<p class='error'>Error processing this video: {video.error}</p>"),
                    }
                )
            elif has_summary:
                # Include videos with summaries
                video_summaries.append(
                    {
                        "title": video_name,
                        "date": video.date.strftime("%B %d, %Y") if video.date else None,
                        "summary": Markup(self._format_content(video.summary)),
                    }
                )
        
        print(f"✅ Prepared {len(video_summaries)} video summaries for HTML report")

        return {
            "generation_date": generation_date,
            "video_count": len(report.video_summaries),
            "executive_summary": executive_summary,
            "technical_summary": technical_summary,
            "project_overview": project_overview,
            "key_themes": context.key_themes,
            "technical_stack": context.technical_stack,
            "diagrams": report.diagrams,
            "people": people,
            "components": components,
            "timeline_events": timeline_events,
            "video_summaries": video_summaries,
        }

    def _render_template(self, variables: Dict) -> str:
        """
        Render the HTML template with variables using Jinja2.

        Args:
            variables: Dictionary of template variables

        Returns:
            Rendered HTML string
        """
        # Use Jinja2 to render the template
        template = Template(self.template)
        html = template.render(**variables)
        return html

    def _format_content(self, text: str) -> str:
        """
        Convert markdown-like formatting to HTML.

        Args:
            text: Raw text with markdown formatting

        Returns:
            HTML formatted text
        """
        if not text:
            return ""

        lines = text.split("\n")
        html_lines = []
        in_list = False

        for line in lines:
            stripped = line.strip()

            # Headers
            if stripped.startswith("###"):
                html_lines.append(f"<h4>{stripped[3:].strip()}</h4>")
            elif stripped.startswith("##"):
                html_lines.append(f"<h3>{stripped[2:].strip()}</h3>")
            elif stripped.startswith("#"):
                html_lines.append(f"<h3>{stripped[1:].strip()}</h3>")

            # Bold with **
            elif "**" in stripped:
                formatted = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", stripped)
                html_lines.append(f"<p>{formatted}</p>")

            # Lists
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{stripped[2:]}</li>")

            elif stripped.startswith(tuple(f"{i}." for i in range(1, 10))):
                if not in_list:
                    html_lines.append("<ol>")
                    in_list = True
                # Remove number prefix
                content = re.sub(r"^\d+\.\s*", "", stripped)
                html_lines.append(f"<li>{content}</li>")

            # Empty line
            elif not stripped:
                if in_list:
                    # Close list
                    html_lines.append("</ul>" if html_lines[-2].startswith("<li>") else "</ol>")
                    in_list = False
                html_lines.append("<br>")

            # Regular paragraph
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p>{stripped}</p>")

        # Close any open list
        if in_list:
            html_lines.append("</ul>")

        return "\n".join(html_lines)

    def export_markdown(
        self, handover_report: HandoverReport, output_dir: Path
    ) -> None:
        """
        Export handover report as separate markdown files.

        Args:
            handover_report: The handover report data
            output_dir: Directory to save markdown files
        """
        print("\n📝 Exporting markdown files...")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Executive summary
        exec_path = output_dir / "executive_summary.md"
        with open(exec_path, "w", encoding="utf-8") as f:
            f.write("# Executive Handover Summary\n\n")
            f.write(handover_report.executive_summary)

        # Technical summary
        tech_path = output_dir / "technical_summary.md"
        with open(tech_path, "w", encoding="utf-8") as f:
            f.write("# Technical Handover Summary\n\n")
            f.write(handover_report.technical_summary)

        print(f"✅ Markdown files saved to: {output_dir}")
        print(f"   - {exec_path.name}")
        print(f"   - {tech_path.name}")

