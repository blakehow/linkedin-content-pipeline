"""AI client factory with fallback support."""

import logging
from typing import Optional

from src.ai.base import AIClient
from src.ai.mock_client import MockAIClient
from src.ai.ollama_client import OllamaClient
from src.ai.gemini_client import GeminiClient
from src.security import validate_ai_output
from config.settings import get_settings

logger = logging.getLogger(__name__)


class AIClientWithFallback:
    """AI client that supports fallback to secondary service."""

    def __init__(
        self,
        primary_client: AIClient,
        fallback_client: Optional[AIClient] = None,
        primary_name: str = "Primary",
        fallback_name: str = "Fallback"
    ):
        """Initialize with primary and optional fallback client."""
        self.primary_client = primary_client
        self.fallback_client = fallback_client
        self.primary_name = primary_name
        self.fallback_name = fallback_name
        self._primary_failed = False
        self._last_error_message = None

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text, falling back if primary fails."""

        response = None
        primary_error = None
        fallback_error = None

        # Try primary first
        if not self._primary_failed:
            try:
                if self.primary_client.is_available():
                    logger.info(f"Using {self.primary_name} AI client")
                    response = self.primary_client.generate(prompt, max_tokens)
                else:
                    logger.warning(f"{self.primary_name} AI client not available")
                    self._primary_failed = True
                    primary_error = f"{self.primary_name} service is not available"
            except Exception as e:
                error_str = str(e).lower()
                logger.error(f"{self.primary_name} AI client failed: {e}")
                self._primary_failed = True
                primary_error = str(e)

                # Check if it's a quota/rate limit error
                if any(x in error_str for x in ["quota", "rate limit", "429"]):
                    primary_error = f"{self.primary_name} quota exceeded. Trying {self.fallback_name}..."

        # Fall back to secondary
        if response is None and self.fallback_client:
            try:
                if self.fallback_client.is_available():
                    logger.info(f"Using {self.fallback_name} AI client")
                    response = self.fallback_client.generate(prompt, max_tokens)
                else:
                    fallback_error = f"{self.fallback_name} service is not available"
                    logger.error(fallback_error)
            except Exception as e:
                fallback_error = str(e)
                logger.error(f"{self.fallback_name} AI client failed: {e}")

        if response is None:
            # Build helpful error message
            error_parts = []
            if primary_error:
                error_parts.append(f"{self.primary_name} failed: {primary_error}")
            if fallback_error:
                error_parts.append(f"{self.fallback_name} failed: {fallback_error}")
            elif not self.fallback_client:
                error_parts.append("No fallback service configured")

            details = ". ".join(error_parts)
            full_error = f"All AI services failed. {details}"
            self._last_error_message = full_error
            raise RuntimeError(full_error)

        # Validate AI output for security
        return validate_ai_output(response)

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self._last_error_message

    def is_available(self) -> bool:
        """Check if any client is available."""
        return (
            self.primary_client.is_available() or
            (self.fallback_client and self.fallback_client.is_available())
        )


def create_ai_client() -> AIClientWithFallback:
    """Create AI client based on configuration."""
    from src.data.storage import get_storage

    settings = get_settings()
    storage = get_storage()
    user_settings = storage.get_settings()

    # Use user settings if available, otherwise fall back to env settings
    if user_settings and hasattr(user_settings, 'ai_provider_primary'):
        primary_service = user_settings.ai_provider_primary
        fallback_service = user_settings.ai_provider_fallback if hasattr(user_settings, 'ai_provider_fallback') else None
    else:
        primary_service = settings.ai_service_primary
        fallback_service = settings.ai_service_fallback

    # Create primary client
    primary_client = _create_client(primary_service, settings)

    # Create fallback client if different from primary
    fallback_client = None
    fallback_name = None
    if (fallback_service and
        fallback_service != primary_service and
        fallback_service.lower() not in ["none", "null", ""]):
        fallback_client = _create_client(fallback_service, settings)
        fallback_name = fallback_service.capitalize()

    return AIClientWithFallback(
        primary_client,
        fallback_client,
        primary_name=primary_service.capitalize(),
        fallback_name=fallback_name or "None"
    )


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
