"""Unit tests for rate limiter."""

import pytest
import time
from src.ai.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_allows_requests_under_limit(self):
        """Test that requests under limit are allowed."""
        limiter = RateLimiter(max_requests_per_minute=10)

        for i in range(5):
            can_request, wait_time = limiter.can_make_request()
            assert can_request
            assert wait_time is None
            limiter.record_request()

    def test_blocks_requests_over_minute_limit(self):
        """Test that requests over minute limit are blocked."""
        limiter = RateLimiter(max_requests_per_minute=5)

        # Make 5 requests (at limit)
        for i in range(5):
            limiter.record_request()

        # 6th request should be blocked
        can_request, wait_time = limiter.can_make_request()
        assert not can_request
        assert wait_time is not None
        assert wait_time > 0

    def test_blocks_requests_over_hour_limit(self):
        """Test that requests over hour limit are blocked."""
        limiter = RateLimiter(
            max_requests_per_minute=100,
            max_requests_per_hour=10
        )

        # Make 10 requests (at hour limit)
        for i in range(10):
            limiter.record_request()

        # 11th request should be blocked
        can_request, wait_time = limiter.can_make_request()
        assert not can_request
        assert wait_time is not None

    def test_execute_with_backoff_success(self):
        """Test successful execution with backoff."""
        limiter = RateLimiter(max_requests_per_minute=100)

        def dummy_func():
            return "success"

        result = limiter.execute_with_backoff(dummy_func)
        assert result == "success"

    def test_execute_with_backoff_retries(self):
        """Test retry logic with backoff."""
        limiter = RateLimiter(max_requests_per_minute=100, max_retries=2)

        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Rate limit exceeded")
            return "success"

        result = limiter.execute_with_backoff(failing_func)
        assert result == "success"
        assert call_count == 2

    def test_execute_with_backoff_max_retries(self):
        """Test max retries are respected."""
        limiter = RateLimiter(max_requests_per_minute=100, max_retries=2)

        def always_fails():
            raise Exception("Rate limit exceeded")

        with pytest.raises(Exception):
            limiter.execute_with_backoff(always_fails)

    def test_non_rate_limit_error_raises_immediately(self):
        """Test that non-rate-limit errors are raised immediately."""
        limiter = RateLimiter(max_requests_per_minute=100, max_retries=3)

        call_count = 0

        def other_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Different error")

        with pytest.raises(ValueError):
            limiter.execute_with_backoff(other_error)

        # Should only be called once (no retries for non-rate-limit errors)
        assert call_count == 1
