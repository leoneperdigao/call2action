"""Generate Mermaid diagrams for project handover documentation."""

from datetime import datetime
from typing import Dict, List

from call2action.models import (
    PersonRole,
    ProjectComponent,
    ProjectContext,
    TimelineEvent,
    VideoSummary,
)


class DiagramGenerator:
    """Generates Mermaid.js diagram syntax for various project visualizations."""

    def generate_all_diagrams(
        self, project_context: ProjectContext, video_summaries: List[VideoSummary]
    ) -> Dict[str, str]:
        """
        Generate all diagrams for the handover report.

        Args:
            project_context: Aggregated project context
            video_summaries: List of individual video summaries

        Returns:
            Dictionary mapping diagram names to Mermaid code
        """
        diagrams = {}

        # Generate timeline if we have events or videos with dates
        if project_context.timeline or any(v.date for v in video_summaries):
            diagrams["timeline"] = self.generate_timeline(
                project_context.timeline, video_summaries
            )

        # Generate architecture diagram if we have components
        if project_context.components:
            diagrams["architecture"] = self.generate_architecture_diagram(
                project_context.components
            )

        # Generate roles diagram if we have people
        if project_context.people:
            diagrams["roles"] = self.generate_roles_diagram(
                project_context.people, project_context.components
            )

        # Generate decision flow if we have significant decisions
        if project_context.decisions and len(project_context.decisions) >= 3:
            diagrams["decisions"] = self.generate_decision_flow(
                project_context.decisions, project_context.timeline
            )

        return diagrams

    def generate_timeline(
        self, events: List[TimelineEvent], video_summaries: List[VideoSummary]
    ) -> str:
        """
        Generate a Mermaid Gantt chart timeline.

        Args:
            events: List of timeline events
            video_summaries: List of video summaries with dates

        Returns:
            Mermaid Gantt chart syntax
        """
        mermaid = ["gantt", "    title Project Timeline", "    dateFormat YYYY-MM-DD", ""]

        # Collect all dates to determine range
        all_items = []

        # Add video meetings
        for video in video_summaries:
            if video.date:
                all_items.append((video.date, f"Meeting: {video.video_file.stem}", "meeting"))

        # Add timeline events
        for event in events:
            if event.date:
                all_items.append((event.date, event.title, event.event_type))

        # Sort by date
        all_items.sort(key=lambda x: x[0])

        if not all_items:
            # If no dates available, create a simple list
            mermaid = ["gantt", "    title Project Events", ""]
            for i, event in enumerate(events[:10], 1):
                mermaid.append(f"    Event {i}: {self._sanitize_mermaid(event.title)}")
            return "\n".join(mermaid)

        # Group by type - use defaultdict or create sections dynamically
        from collections import defaultdict
        sections = defaultdict(list)

        for date, title, event_type in all_items:
            # Normalize event type to avoid KeyError
            if not event_type:
                event_type = "other"
            sections[event_type].append((date, title))

        # Add sections with items
        for section_name, items in sections.items():
            if items:
                mermaid.append(f"    section {section_name.title()}s")
                for date, title in items:
                    sanitized_title = self._sanitize_mermaid(title[:50])
                    date_str = date.strftime("%Y-%m-%d")
                    mermaid.append(f"    {sanitized_title}: {date_str}, 1d")
                mermaid.append("")

        return "\n".join(mermaid)

    def generate_architecture_diagram(
        self, components: List[ProjectComponent]
    ) -> str:
        """
        Generate a Mermaid component/architecture diagram.

        Args:
            components: List of project components

        Returns:
            Mermaid graph syntax
        """
        mermaid = ["graph TB", ""]

        # Add component nodes with safe labels
        for i, component in enumerate(components):
            node_id = f"C{i}"
            label = self._sanitize_mermaid(component.name)
            if not label:
                label = f"Component {i+1}"
            # Use simple box notation
            mermaid.append(f"    {node_id}[{label}]")

        mermaid.append("")

        # Add relationships with simple arrows
        for i, component in enumerate(components):
            node_id = f"C{i}"

            # Parse relationships to find connections
            for relationship in component.relationships:
                # Try to find which component this relates to
                for j, other_component in enumerate(components):
                    if i != j and (
                        other_component.name.lower() in relationship.lower()
                    ):
                        target_id = f"C{j}"
                        # Use simple arrow without label to avoid syntax issues
                        mermaid.append(f"    {node_id} --> {target_id}")
                        break

        return "\n".join(mermaid)

    def generate_roles_diagram(
        self, people: List[PersonRole], components: List[ProjectComponent]
    ) -> str:
        """
        Generate a Mermaid diagram showing people, roles, and components.

        Args:
            people: List of people and their roles
            components: List of project components

        Returns:
            Mermaid graph syntax
        """
        mermaid = ["graph LR", ""]

        # Add people nodes
        for i, person in enumerate(people):
            person_id = f"P{i}"
            name = self._sanitize_mermaid(person.name)
            if not name:
                name = f"Person {i+1}"
            mermaid.append(f"    {person_id}[{name}]")

        mermaid.append("")

        # Add component nodes (if they work on components)
        component_ids = {}
        component_counter = 0
        for person in people:
            for comp_name in person.components:
                if comp_name not in component_ids:
                    comp_id = f"C{component_counter}"
                    component_ids[comp_name] = comp_id
                    sanitized = self._sanitize_mermaid(comp_name)
                    if not sanitized:
                        sanitized = f"Component {component_counter+1}"
                    mermaid.append(f"    {comp_id}[{sanitized}]")
                    component_counter += 1

        mermaid.append("")

        # Add connections between people and components (simple arrows)
        for i, person in enumerate(people):
            person_id = f"P{i}"
            for comp_name in person.components:
                if comp_name in component_ids:
                    comp_id = component_ids[comp_name]
                    # Use simple arrow without label to avoid syntax issues
                    mermaid.append(f"    {person_id} --> {comp_id}")

        return "\n".join(mermaid)

    def generate_decision_flow(
        self, decisions: List[str], timeline: List[TimelineEvent]
    ) -> str:
        """
        Generate a Mermaid flowchart of key decisions.

        Args:
            decisions: List of key decisions
            timeline: Timeline events for context

        Returns:
            Mermaid flowchart syntax
        """
        mermaid = ["flowchart TD", ""]

        # Filter decision events from timeline
        decision_events = [e for e in timeline if e.event_type == "decision"]

        # Use timeline decisions if available, otherwise use decisions list
        items_to_show = decision_events if decision_events else decisions[:8]

        if not items_to_show:
            mermaid.append("    Start[Project Started]")
            return "\n".join(mermaid)

        # Create flow of decisions
        mermaid.append("    Start([Project Start])")

        for i, item in enumerate(items_to_show):
            node_id = f"D{i}"

            if isinstance(item, TimelineEvent):
                title = self._sanitize_mermaid(item.title[:40])
                if not title:
                    title = f"Event {i+1}"
                # Use simple box notation for better compatibility
                mermaid.append(f"    {node_id}[{title}]")
            else:
                # Plain decision string
                text = self._sanitize_mermaid(item[:60])
                if not text:
                    text = f"Decision {i+1}"
                mermaid.append(f"    {node_id}[{text}]")

            # Connect to previous
            if i == 0:
                mermaid.append(f"    Start --> {node_id}")
            else:
                mermaid.append(f"    D{i-1} --> {node_id}")

        # Add end node
        last_id = f"D{len(items_to_show)-1}"
        mermaid.append(f"    {last_id} --> End([Current State])")

        return "\n".join(mermaid)

    def _sanitize_mermaid(self, text: str) -> str:
        """
        Sanitize text for use in Mermaid diagrams.

        Args:
            text: Raw text

        Returns:
            Sanitized text safe for Mermaid syntax
        """
        if not text:
            return ""
            
        # Replace characters that break Mermaid syntax
        replacements = {
            '"': "",  # Remove quotes entirely
            "'": "",  # Remove single quotes
            "`": "",  # Remove backticks
            "\n": " ",  # Replace newlines with spaces
            "\r": " ",  # Replace carriage returns
            "#": "",  # Remove hash
            ";": ",",  # Replace semicolons
            ":": "-",  # Replace colons
            "(": "",  # Remove parentheses
            ")": "",
            "[": "",  # Remove brackets
            "]": "",
            "{": "",  # Remove braces
            "}": "",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Trim and normalize whitespace
        text = " ".join(text.split())
        
        # Limit length to prevent overly long labels
        if len(text) > 60:
            text = text[:57] + "..."

        return text

