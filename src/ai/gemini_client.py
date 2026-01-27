"""Google Gemini AI client."""

import logging
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from src.ai.base import AIClient
from src.ai.rate_limiter import get_gemini_rate_limiter

logger = logging.getLogger(__name__)


class GeminiClient(AIClient):
    """Client for Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash-8b"):
        """Initialize Gemini client."""
        self.api_key = api_key
        self.model_name = model
        self._model = None
        self._available = None
        self.rate_limiter = get_gemini_rate_limiter()

        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(model)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text using Gemini with rate limiting."""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("google-generativeai package not installed")

        if not self._model:
            raise RuntimeError("Gemini model not initialized. Check API key.")

        def _generate():
            generation_config = {}
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            response = self._model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text

        try:
            # Use rate limiter with exponential backoff
            return self.rate_limiter.execute_with_backoff(_generate)

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise RuntimeError(f"Failed to generate with Gemini: {e}")

    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        if not GEMINI_AVAILABLE:
            return False

        if self._available is not None:
            return self._available

        if not self.api_key or not self._model:
            self._available = False
            return False

        try:
            # Try a simple generation to test
            _ = self._model.generate_content("Test")
            self._available = True
            return True
        except Exception as e:
            logger.warning(f"Gemini not available: {e}")
            self._available = False
            return False
