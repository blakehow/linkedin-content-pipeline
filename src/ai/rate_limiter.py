"""Rate limiting for AI API calls."""

import time
import logging
from collections import deque
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter with exponential backoff."""

    def __init__(
        self,
        max_requests_per_minute: int = 60,
        max_requests_per_hour: int = 1000,
        max_retries: int = 3,
        initial_backoff: float = 1.0
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests per minute
            max_requests_per_hour: Maximum requests per hour
            max_retries: Maximum number of retries on rate limit errors
            initial_backoff: Initial backoff time in seconds
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

        # Track requests in sliding windows
        self.minute_requests = deque()
        self.hour_requests = deque()

    def _clean_old_requests(self):
        """Remove requests older than the time windows."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        # Clean minute window
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()

        # Clean hour window
        while self.hour_requests and self.hour_requests[0] < hour_ago:
            self.hour_requests.popleft()

    def can_make_request(self) -> tuple[bool, Optional[float]]:
        """
        Check if a request can be made.

        Returns:
            Tuple of (can_make_request, wait_time_seconds)
        """
        self._clean_old_requests()

        # Check minute limit
        if len(self.minute_requests) >= self.max_requests_per_minute:
            oldest = self.minute_requests[0]
            wait_time = 60 - (datetime.now() - oldest).total_seconds()
            return False, max(0, wait_time)

        # Check hour limit
        if len(self.hour_requests) >= self.max_requests_per_hour:
            oldest = self.hour_requests[0]
            wait_time = 3600 - (datetime.now() - oldest).total_seconds()
            return False, max(0, wait_time)

        return True, None

    def record_request(self):
        """Record a successful request."""
        now = datetime.now()
        self.minute_requests.append(now)
        self.hour_requests.append(now)

    def wait_if_needed(self) -> bool:
        """
        Wait if rate limit is reached.

        Returns:
            True if waited, False if no wait was needed
        """
        can_request, wait_time = self.can_make_request()

        if not can_request and wait_time:
            logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time + 0.1)  # Add small buffer
            return True

        return False

    def execute_with_backoff(self, func, *args, **kwargs):
        """
        Execute a function with exponential backoff on rate limit errors.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If all retries are exhausted
        """
        backoff = self.initial_backoff

        for attempt in range(self.max_retries + 1):
            # Wait if rate limited
            self.wait_if_needed()

            try:
                # Record request before making it
                self.record_request()

                # Execute function
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                error_str = str(e).lower()

                # Check if it's a retryable error
                is_retryable = any([
                    "rate limit" in error_str,
                    "quota" in error_str,
                    "429" in error_str,
                    "timeout" in error_str,
                    "timed out" in error_str,
                    "connection" in error_str,
                    "network" in error_str,
                    "503" in error_str,  # Service unavailable
                    "502" in error_str,  # Bad gateway
                    "500" in error_str,  # Internal server error
                    "temporarily unavailable" in error_str,
                ])

                if is_retryable:
                    if attempt < self.max_retries:
                        logger.warning(
                            f"Retryable error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                            f"Backing off for {backoff:.1f} seconds..."
                        )
                        time.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Max retries exceeded after {self.max_retries + 1} attempts: {e}")
                        raise

                # Not a retryable error, raise immediately
                logger.error(f"Non-retryable error: {e}")
                raise

        raise RuntimeError("Max retries exceeded")


# Global rate limiter instances
_gemini_limiter: Optional[RateLimiter] = None
_ollama_limiter: Optional[RateLimiter] = None


def get_gemini_rate_limiter() -> RateLimiter:
    """Get the global Gemini rate limiter."""
    global _gemini_limiter
    if _gemini_limiter is None:
        # Gemini free tier: 60 requests per minute
        _gemini_limiter = RateLimiter(
            max_requests_per_minute=60,
            max_requests_per_hour=1500,
            max_retries=3,
            initial_backoff=2.0
        )
    return _gemini_limiter


def get_ollama_rate_limiter() -> RateLimiter:
    """Get the global Ollama rate limiter."""
    global _ollama_limiter
    if _ollama_limiter is None:
        # Ollama local: More generous limits
        _ollama_limiter = RateLimiter(
            max_requests_per_minute=120,
            max_requests_per_hour=5000,
            max_retries=2,
            initial_backoff=1.0
        )
    return _ollama_limiter
