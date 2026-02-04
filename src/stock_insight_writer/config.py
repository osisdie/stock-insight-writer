"""Configuration management using Pydantic Settings."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Language(StrEnum):
    """Supported output languages."""

    EN = "en"
    ZH_TW = "zh-TW"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter API (OpenAI-compatible)
    openrouter_api_key: SecretStr
    openrouter_model: str = "anthropic/claude-sonnet-4"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Language setting
    language: Language = Language.EN

    # Slack notification
    slack_webhook_url: SecretStr | None = None

    # Output configuration
    output_dir: Path = Path("output/stock-posts")

    # Stock screening settings
    min_price_change_pct: float = 10.0
    max_candidates: int = 6


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
