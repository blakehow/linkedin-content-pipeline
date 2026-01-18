"""Base AI client interface."""

from abc import ABC, abstractmethod
from typing import Optional


class AIClient(ABC):
    """Base class for AI clients."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text from a prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI service is available."""
        pass
