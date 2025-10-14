"""Prompt management for the Call2Action pipeline."""

from pathlib import Path
from typing import Dict

import yaml


class PromptManager:
    """Manages and loads prompts from YAML configuration file."""

    def __init__(self, prompts_file: Path):
        """
        Initialize the prompt manager.

        Args:
            prompts_file: Path to the YAML file containing prompts
        """
        self.prompts_file = prompts_file
        self._prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompts from the YAML file."""
        if not self.prompts_file.exists():
            raise FileNotFoundError(
                f"Prompts file not found: {self.prompts_file}\n"
                f"Please ensure prompts.yaml exists in the project root."
            )

        with open(self.prompts_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Extract template strings from the YAML structure
        for key, value in data.items():
            if isinstance(value, dict) and "template" in value:
                self._prompts[key] = value["template"]
            else:
                self._prompts[key] = value

        print(f"✅ Loaded {len(self._prompts)} prompts from {self.prompts_file}")

    def get_prompt(self, prompt_name: str) -> str:
        """
        Get a prompt template by name.

        Args:
            prompt_name: Name of the prompt to retrieve

        Returns:
            The prompt template string

        Raises:
            KeyError: If the prompt name is not found
        """
        if prompt_name not in self._prompts:
            raise KeyError(
                f"Prompt '{prompt_name}' not found. "
                f"Available prompts: {list(self._prompts.keys())}"
            )
        return self._prompts[prompt_name]

    @property
    def chunk_summary(self) -> str:
        """Get the chunk summary prompt."""
        return self.get_prompt("chunk_summary")

    @property
    def group_summary(self) -> str:
        """Get the group summary prompt."""
        return self.get_prompt("group_summary")

    @property
    def final_summary(self) -> str:
        """Get the final summary prompt."""
        return self.get_prompt("final_summary")

    @property
    def action_items(self) -> str:
        """Get the action items prompt."""
        return self.get_prompt("action_items")
