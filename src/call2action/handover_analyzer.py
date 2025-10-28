"""Analyze multiple video summaries to extract project context for handover documentation."""

import json
from typing import List

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from call2action.config import Settings
from call2action.models import (
    PersonRole,
    ProjectComponent,
    ProjectContext,
    TimelineEvent,
    VideoSummary,
)
from call2action.prompts import PromptManager


class HandoverAnalyzer:
    """Analyzes multiple video summaries to extract comprehensive project context."""

    def __init__(self, settings: Settings):
        """
        Initialize the handover analyzer.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.prompt_manager = PromptManager(settings.prompts_file)

        # Initialize LLM with higher token limit for analysis
        llm_params = {
            "model": settings.openai_model,
            "api_key": settings.openai_api_key,
            "max_tokens": 8192,
        }

        if settings.openai_temperature != 1.0:
            llm_params["temperature"] = settings.openai_temperature

        self.llm = ChatOpenAI(**llm_params)

        print(f"✅ HandoverAnalyzer initialized")

    def analyze_project_context(
        self, video_summaries: List[VideoSummary]
    ) -> ProjectContext:
        """
        Analyze all video summaries to extract comprehensive project context.

        Args:
            video_summaries: List of processed video summaries

        Returns:
            ProjectContext with aggregated information
        """
        print("\n" + "=" * 60)
        print("🔍 Analyzing Project Context")
        print("=" * 60)

        # Prepare summaries text
        summaries_text = self._prepare_summaries_text(video_summaries)

        # Extract project analysis
        print("📊 Extracting project overview and themes...")
        project_data = self._extract_project_analysis(summaries_text)

        # Extract components
        print("🏗️  Extracting technical components...")
        components = self._extract_components(summaries_text)

        # Extract people and roles
        print("👥 Extracting people and roles...")
        people = self._extract_people_roles(summaries_text)

        # Extract timeline events
        print("📅 Extracting timeline events...")
        timeline = self._extract_timeline(video_summaries, summaries_text)

        # Build ProjectContext
        context = ProjectContext(
            project_overview=project_data.get("project_overview", ""),
            key_themes=project_data.get("key_themes", []),
            people=people,
            components=components,
            timeline=timeline,
            decisions=project_data.get("decisions", []),
            risks=project_data.get("risks", []),
            open_questions=project_data.get("open_questions", []),
            technical_stack=project_data.get("technical_stack", []),
        )

        print(f"✅ Project context analyzed:")
        print(f"   - {len(context.key_themes)} themes identified")
        print(f"   - {len(context.people)} people identified")
        print(f"   - {len(context.components)} components identified")
        print(f"   - {len(context.timeline)} timeline events")
        print(f"   - {len(context.decisions)} key decisions")

        return context

    def generate_executive_summary(self, project_context: ProjectContext) -> str:
        """
        Generate executive-focused handover summary.

        Args:
            project_context: Aggregated project context

        Returns:
            Executive summary text
        """
        print("\n📝 Generating executive summary...")

        # Prepare context text
        context_text = self._format_project_context(project_context)

        # Load prompt
        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("executive_summary")
        )

        chain = prompt_template | self.llm
        response = chain.invoke({"project_context": context_text})

        summary = response.content.strip()
        print(f"✅ Executive summary generated ({len(summary)} chars)")

        return summary

    def generate_technical_summary(self, project_context: ProjectContext) -> str:
        """
        Generate technical-focused handover summary.

        Args:
            project_context: Aggregated project context

        Returns:
            Technical summary text
        """
        print("\n📝 Generating technical summary...")

        # Prepare context text
        context_text = self._format_project_context(project_context, technical=True)

        # Load prompt
        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("technical_summary")
        )

        chain = prompt_template | self.llm
        response = chain.invoke({"project_context": context_text})

        summary = response.content.strip()
        print(f"✅ Technical summary generated ({len(summary)} chars)")

        return summary

    def _prepare_summaries_text(self, video_summaries: List[VideoSummary]) -> str:
        """Prepare concatenated summaries text for analysis."""
        summaries = []

        for i, video in enumerate(video_summaries, 1):
            date_str = video.date.strftime("%Y-%m-%d") if video.date else "Unknown date"
            summaries.append(
                f"--- Video {i}: {video.video_file.stem} ({date_str}) ---\n{video.summary}\n"
            )

        return "\n\n".join(summaries)

    def _extract_project_analysis(self, summaries_text: str) -> dict:
        """Extract high-level project analysis using LLM."""
        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("project_analysis")
        )

        chain = prompt_template | self.llm

        try:
            response = chain.invoke({"summaries": summaries_text})
            result_text = response.content.strip()

            # Try to parse JSON
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            return data

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse JSON response: {e}")
            print(f"   Using fallback values")
            return {
                "project_overview": "Unable to extract project overview automatically.",
                "key_themes": [],
                "decisions": [],
                "risks": [],
                "open_questions": [],
                "technical_stack": [],
            }
        except Exception as e:
            print(f"   ⚠️  Error extracting project analysis: {e}")
            return {
                "project_overview": "Error during analysis.",
                "key_themes": [],
                "decisions": [],
                "risks": [],
                "open_questions": [],
                "technical_stack": [],
            }

    def _extract_components(self, summaries_text: str) -> List[ProjectComponent]:
        """Extract technical components using LLM."""
        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("component_extraction")
        )

        chain = prompt_template | self.llm

        try:
            response = chain.invoke({"summaries": summaries_text})
            result_text = response.content.strip()

            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            components = []

            for comp_data in data.get("components", []):
                component = ProjectComponent(
                    name=comp_data.get("name", "Unknown"),
                    description=comp_data.get("description", ""),
                    technologies=comp_data.get("technologies", []),
                    relationships=comp_data.get("relationships", []),
                )
                components.append(component)

            return components

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse components JSON: {e}")
            return []
        except Exception as e:
            print(f"   ⚠️  Error extracting components: {e}")
            return []

    def _extract_people_roles(self, summaries_text: str) -> List[PersonRole]:
        """Extract people and their roles using LLM."""
        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("people_roles_extraction")
        )

        chain = prompt_template | self.llm

        try:
            response = chain.invoke({"summaries": summaries_text})
            result_text = response.content.strip()

            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            people = []

            for person_data in data.get("people", []):
                person = PersonRole(
                    name=person_data.get("name", "Unknown"),
                    roles=person_data.get("roles", []),
                    components=person_data.get("components", []),
                )
                people.append(person)

            return people

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse people JSON: {e}")
            return []
        except Exception as e:
            print(f"   ⚠️  Error extracting people: {e}")
            return []

    def _extract_timeline(
        self, video_summaries: List[VideoSummary], summaries_text: str
    ) -> List[TimelineEvent]:
        """Extract timeline events using LLM."""
        # Prepare summaries with dates
        summaries_with_dates = []
        for video in video_summaries:
            date_str = video.date.strftime("%Y-%m-%d") if video.date else "null"
            summaries_with_dates.append(
                f"Date: {date_str}\nVideo: {video.video_file.stem}\nSummary: {video.summary}\n"
            )

        summaries_text_dated = "\n---\n".join(summaries_with_dates)

        prompt_template = ChatPromptTemplate.from_template(
            self.prompt_manager.get_prompt("timeline_extraction")
        )

        chain = prompt_template | self.llm

        try:
            response = chain.invoke({"summaries_with_dates": summaries_text_dated})
            result_text = response.content.strip()

            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            data = json.loads(result_text)
            events = []

            for event_data in data.get("events", []):
                # Parse date
                date = None
                video_date = event_data.get("video_date")
                if video_date and video_date != "null":
                    try:
                        from datetime import datetime
                        date = datetime.strptime(video_date, "%Y-%m-%d")
                    except ValueError:
                        pass

                event = TimelineEvent(
                    date=date,
                    title=event_data.get("title", "Event"),
                    description=event_data.get("description", ""),
                    event_type=event_data.get("type", "discussion"),
                )
                events.append(event)

            # Sort by date (None dates at the end)
            events.sort(key=lambda e: e.date if e.date else datetime.max)

            return events

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse timeline JSON: {e}")
            return []
        except Exception as e:
            print(f"   ⚠️  Error extracting timeline: {e}")
            return []

    def _format_project_context(
        self, context: ProjectContext, technical: bool = False
    ) -> str:
        """Format project context as text for LLM consumption."""
        lines = []

        lines.append("PROJECT OVERVIEW:")
        lines.append(context.project_overview)
        lines.append("")

        lines.append("KEY THEMES:")
        for theme in context.key_themes:
            lines.append(f"  - {theme}")
        lines.append("")

        if technical and context.technical_stack:
            lines.append("TECHNICAL STACK:")
            for tech in context.technical_stack:
                lines.append(f"  - {tech}")
            lines.append("")

        if technical and context.components:
            lines.append("COMPONENTS:")
            for comp in context.components:
                lines.append(f"  • {comp.name}: {comp.description}")
                if comp.technologies:
                    lines.append(f"    Technologies: {', '.join(comp.technologies)}")
            lines.append("")

        if context.people:
            lines.append("PEOPLE & ROLES:")
            for person in context.people:
                roles = ", ".join(person.roles) if person.roles else "Team member"
                lines.append(f"  • {person.name} - {roles}")
                if person.components:
                    lines.append(f"    Works on: {', '.join(person.components)}")
            lines.append("")

        if context.decisions:
            lines.append("KEY DECISIONS:")
            for decision in context.decisions:
                lines.append(f"  - {decision}")
            lines.append("")

        if context.risks:
            lines.append("RISKS & CONCERNS:")
            for risk in context.risks:
                lines.append(f"  - {risk}")
            lines.append("")

        if context.open_questions:
            lines.append("OPEN QUESTIONS:")
            for question in context.open_questions:
                lines.append(f"  - {question}")
            lines.append("")

        if context.timeline:
            lines.append("TIMELINE HIGHLIGHTS:")
            for event in context.timeline[:10]:  # Top 10 events
                date_str = event.date.strftime("%Y-%m-%d") if event.date else "TBD"
                lines.append(f"  • [{date_str}] {event.title}: {event.description}")
            lines.append("")

        return "\n".join(lines)

