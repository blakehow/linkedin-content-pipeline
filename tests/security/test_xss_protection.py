"""Security tests for XSS protection."""

import pytest
from src.security.input_sanitizer import validate_ai_output


class TestXSSProtection:
    """Test protection against XSS attacks."""

    def test_removes_script_tags(self):
        """Test removal of script tags."""
        attacks = [
            "<script>alert('XSS')</script>",
            "<SCRIPT>alert('XSS')</SCRIPT>",
            "<script src='evil.js'></script>",
            "Hello<script>alert(1)</script>World",
        ]

        for attack in attacks:
            result = validate_ai_output(attack)
            assert "<script" not in result.lower()
            assert "</script>" not in result.lower()

    def test_removes_javascript_urls(self):
        """Test removal of javascript: URLs."""
        attacks = [
            "<a href='javascript:alert(1)'>Click</a>",
            "<img src='x' onerror='javascript:alert(1)'>",
            "Visit javascript:void(0)",
        ]

        for attack in attacks:
            result = validate_ai_output(attack)
            assert "javascript:" not in result.lower()

    def test_removes_event_handlers(self):
        """Test removal of event handler attributes."""
        attacks = [
            "<div onclick='alert(1)'>Click</div>",
            "<img onerror='alert(1)' src='x'>",
            "<body onload='steal()'>",
            "<input onfocus='evil()'>",
        ]

        for attack in attacks:
            result = validate_ai_output(attack)
            # Check that event handlers are removed
            assert "onclick" not in result.lower()
            assert "onerror" not in result.lower()
            assert "onload" not in result.lower()
            assert "onfocus" not in result.lower()

    def test_allows_safe_html(self):
        """Test that safe HTML/markdown is preserved."""
        safe_content = [
            "<b>Bold text</b>",
            "Visit https://example.com",
            "Email: user@example.com",
            "## Heading\n- List item",
        ]

        for content in safe_content:
            result = validate_ai_output(content)
            # Should not be empty or dramatically changed
            assert len(result) > 0

    def test_removes_multiple_script_tags(self):
        """Test removal of multiple script tags."""
        attack = """
        <script>alert(1)</script>
        Normal content here
        <script>alert(2)</script>
        """

        result = validate_ai_output(attack)
        assert "<script" not in result.lower()
        assert "Normal content here" in result

    def test_removes_inline_scripts(self):
        """Test removal of inline scripts in various positions."""
        attacks = [
            "Start<script>bad()</script>End",
            "<p>Text<script>bad()</script>More</p>",
            "<script>first()</script>Middle<script>second()</script>",
        ]

        for attack in attacks:
            result = validate_ai_output(attack)
            assert "bad()" not in result
            assert "first()" not in result
            assert "second()" not in result

    def test_truncates_excessive_output(self):
        """Test truncation of excessively long output."""
        # Create very long output (potential DoS)
        long_output = "A" * 100000

        result = validate_ai_output(long_output)

        # Should be truncated
        assert len(result) < len(long_output)
        assert "[truncated]" in result
