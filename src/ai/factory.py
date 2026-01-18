"""AI client factory with fallback support."""

import logging
from typing import Optional

from src.ai.base import AIClient
from src.ai.mock_client import MockAIClient
from src.ai.ollama_client import OllamaClient
from src.ai.gemini_client import GeminiClient
from config.settings import get_settings

logger = logging.getLogger(__name__)


class AIClientWithFallback:
    """AI client that supports fallback to secondary service."""

    def __init__(
        self,
        primary_client: AIClient,
        fallback_client: Optional[AIClient] = None
    ):
        """Initialize with primary and optional fallback client."""
        self.primary_client = primary_client
        self.fallback_client = fallback_client
        self._primary_failed = False

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text, falling back if primary fails."""

        # Try primary first
        if not self._primary_failed:
            try:
                if self.primary_client.is_available():
                    logger.info("Using primary AI client")
                    return self.primary_client.generate(prompt, max_tokens)
                else:
                    logger.warning("Primary AI client not available")
                    self._primary_failed = True
            except Exception as e:
                logger.error(f"Primary AI client failed: {e}")
                self._primary_failed = True

        # Fall back to secondary
        if self.fallback_client:
            try:
                if self.fallback_client.is_available():
                    logger.info("Using fallback AI client")
                    return self.fallback_client.generate(prompt, max_tokens)
                else:
                    logger.error("Fallback AI client not available")
            except Exception as e:
                logger.error(f"Fallback AI client failed: {e}")

        raise RuntimeError("All AI services failed")

    def is_available(self) -> bool:
        """Check if any client is available."""
        return (
            self.primary_client.is_available() or
            (self.fallback_client and self.fallback_client.is_available())
        )


def create_ai_client() -> AIClientWithFallback:
    """Create AI client based on configuration."""
    settings = get_settings()

    # Create primary client
    primary_client = _create_client(
        settings.ai_service_primary,
        settings
    )

    # Create fallback client if different from primary
    fallback_client = None
    if settings.ai_service_fallback and settings.ai_service_fallback != settings.ai_service_primary:
        fallback_client = _create_client(
            settings.ai_service_fallback,
            settings
        )

    return AIClientWithFallback(primary_client, fallback_client)


def _create_client(service_type: str, settings) -> AIClient:
    """Create a specific AI client."""

    if service_type == "mock":
        logger.info("Creating mock AI client")
        return MockAIClient()

    elif service_type == "ollama":
        logger.info(f"Creating Ollama client: {settings.ollama_host} / {settings.ollama_model}")
        return OllamaClient(
            host=settings.ollama_host,
            model=settings.ollama_model
        )

    elif service_type == "gemini":
        if not settings.google_gemini_api_key:
            logger.warning("Gemini API key not configured, falling back to mock")
            return MockAIClient()

        logger.info("Creating Gemini client")
        return GeminiClient(
            api_key=settings.google_gemini_api_key
        )

    else:
        logger.warning(f"Unknown AI service: {service_type}, using mock")
        return MockAIClient()


# Global AI client instance
_ai_client: Optional[AIClientWithFallback] = None


def get_ai_client() -> AIClientWithFallback:
    """Get the global AI client instance."""
    global _ai_client
    if _ai_client is None:
        _ai_client = create_ai_client()
    return _ai_client
