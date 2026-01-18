"""Configuration settings for the application."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_env: str = "development"
    debug_mode: bool = True
    log_level: str = "INFO"

    # Data Storage
    data_storage_type: str = "mock"  # mock or google_sheets

    # Google Sheets
    google_sheets_creds_file: Optional[str] = None
    google_sheet_id: Optional[str] = None

    # AI Service
    ai_service_primary: str = "ollama"  # mock, ollama, gemini
    ai_service_fallback: str = "gemini"

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Google Gemini
    google_gemini_api_key: Optional[str] = None

    # Twitter API
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None

    # LinkedIn API
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None

    # Demo Mode
    demo_mode: bool = True
    load_sample_data: bool = True

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_demo_mode(self) -> bool:
        """Check if demo mode is enabled."""
        return self.demo_mode

    @property
    def has_ollama_config(self) -> bool:
        """Check if Ollama is configured."""
        return bool(self.ollama_host and self.ollama_model)

    @property
    def has_gemini_config(self) -> bool:
        """Check if Gemini API is configured."""
        return bool(self.google_gemini_api_key)

    @property
    def has_google_sheets_config(self) -> bool:
        """Check if Google Sheets is configured."""
        return bool(self.google_sheets_creds_file and self.google_sheet_id)

    @property
    def has_twitter_config(self) -> bool:
        """Check if Twitter API is configured."""
        return all([
            self.twitter_api_key,
            self.twitter_api_secret,
            self.twitter_access_token,
            self.twitter_access_token_secret
        ])


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings."""
    return settings


# Data directory for mock storage
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Prompts directory
PROMPTS_DIR = PROJECT_ROOT / "prompts"
PROMPTS_DIR.mkdir(exist_ok=True)
