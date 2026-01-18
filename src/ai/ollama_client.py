"""Ollama AI client."""

import logging
from typing import Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from src.ai.base import AIClient

logger = logging.getLogger(__name__)


class OllamaClient(AIClient):
    """Client for local Ollama AI models."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """Initialize Ollama client."""
        self.host = host
        self.model = model
        self._available = None

    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text using Ollama."""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama package not installed. Install with: pip install ollama")

        if not self.is_available():
            raise RuntimeError(f"Ollama service not available at {self.host}")

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "num_predict": max_tokens if max_tokens else 2048,
                    "temperature": 0.7,
                }
            )

            return response['response']

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"Failed to generate with Ollama: {e}")

    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        if not OLLAMA_AVAILABLE:
            return False

        if self._available is not None:
            return self._available

        try:
            # Try to list models to check connection
            ollama.list()
            self._available = True
            return True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self._available = False
            return False
