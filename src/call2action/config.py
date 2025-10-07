"""Configuration management for the Call2Action pipeline."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 1.0  # Default temperature (some models only support 1.0)
    openai_max_tokens: int = 1000

    # Whisper Configuration
    whisper_model_size: Literal["tiny", "base", "small", "medium", "large-v3"] = "base"
    whisper_device: Literal["cpu", "cuda"] = "cpu"
    whisper_compute_type: Literal["int8", "float16", "float32"] = "int8"

    # Pipeline Configuration
    output_dir: Path = Path("output")

    def __init__(self, **kwargs):
        """Initialize settings and create output directory."""
        super().__init__(**kwargs)
        self.output_dir.mkdir(parents=True, exist_ok=True)
