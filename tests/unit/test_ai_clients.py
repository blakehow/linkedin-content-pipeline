"""Unit tests for AI clients."""

import pytest
from src.ai.mock_client import MockAIClient
from src.ai.factory import AIClientWithFallback


class TestMockAIClient:
    """Test mock AI client."""

    def test_is_available(self):
        """Test that mock client is always available."""
        client = MockAIClient()
        assert client.is_available()

    def test_generate_topic_curation(self):
        """Test topic curation response."""
        client = MockAIClient()
        response = client.generate("curate topics from these ideas")

        assert "Topic 1" in response
        assert "Core Insight" in response

    def test_generate_content_development(self):
        """Test content development response."""
        client = MockAIClient()
        response = client.generate("develop content for bridge audience")

        assert "Title" in response
        assert len(response) > 100

    def test_generate_linkedin_optimization(self):
        """Test LinkedIn optimization response."""
        client = MockAIClient()
        response = client.generate("optimize for linkedin")

        assert len(response) > 50
        assert "#" in response  # Should have hashtags

    def test_generate_twitter_optimization(self):
        """Test Twitter optimization response."""
        client = MockAIClient()
        response = client.generate("create twitter thread")

        assert "THREAD" in response
        assert "1/" in response or "2/" in response


class TestAIClientWithFallback:
    """Test AI client with fallback."""

    def test_uses_primary_when_available(self):
        """Test that primary client is used when available."""
        primary = MockAIClient()
        fallback = MockAIClient()

        client = AIClientWithFallback(primary, fallback)
        response = client.generate("test")

        assert response is not None
        assert len(response) > 0

    def test_falls_back_when_primary_unavailable(self):
        """Test fallback when primary is unavailable."""

        class UnavailableClient(MockAIClient):
            def is_available(self):
                return False

        primary = UnavailableClient()
        fallback = MockAIClient()

        client = AIClientWithFallback(primary, fallback)
        response = client.generate("test")

        assert response is not None

    def test_raises_when_all_fail(self):
        """Test error when all clients fail."""

        class FailingClient(MockAIClient):
            def is_available(self):
                return False

        primary = FailingClient()
        fallback = FailingClient()

        client = AIClientWithFallback(primary, fallback)

        with pytest.raises(RuntimeError, match="All AI services failed"):
            client.generate("test")

    def test_is_available_true_when_any_available(self):
        """Test is_available when any client is available."""
        primary = MockAIClient()
        fallback = MockAIClient()

        client = AIClientWithFallback(primary, fallback)
        assert client.is_available()

    def test_is_available_false_when_none_available(self):
        """Test is_available when no client is available."""

        class UnavailableClient(MockAIClient):
            def is_available(self):
                return False

        primary = UnavailableClient()
        fallback = UnavailableClient()

        client = AIClientWithFallback(primary, fallback)
        assert not client.is_available()
