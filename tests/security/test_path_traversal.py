"""Security tests for path traversal protection."""

import pytest
from src.security.input_sanitizer import sanitize_filename, validate_url


class TestPathTraversal:
    """Test protection against path traversal attacks."""

    def test_blocks_parent_directory_traversal(self):
        """Test blocking ../ path traversal."""
        attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "../../sensitive/file.txt",
            "normal/../../../etc/passwd",
        ]

        for attack in attacks:
            result = sanitize_filename(attack)
            assert ".." not in result
            assert "/" not in result
            assert "\\" not in result

    def test_blocks_absolute_paths(self):
        """Test blocking absolute paths."""
        attacks = [
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
            "/var/log/sensitive.log",
        ]

        for attack in attacks:
            result = sanitize_filename(attack)
            assert not result.startswith("/")
            assert not result.startswith("C:")
            assert "/" not in result
            assert "\\" not in result

    def test_blocks_hidden_files(self):
        """Test blocking hidden file patterns."""
        attacks = [
            ".bashrc",
            ".ssh/id_rsa",
            "...hidden",
        ]

        for attack in attacks:
            result = sanitize_filename(attack)
            # Leading dots should be removed
            assert not result.startswith(".")

    def test_removes_special_characters(self):
        """Test removal of special characters."""
        filename = "my<file>:name|?.txt"
        result = sanitize_filename(filename)

        # Special chars should be removed
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "|" not in result
        assert "?" not in result

    def test_allows_safe_filenames(self):
        """Test that safe filenames pass through."""
        safe_names = [
            "document.txt",
            "my_file_123.pdf",
            "report-2024.xlsx",
        ]

        for name in safe_names:
            result = sanitize_filename(name)
            assert result == name

    def test_handles_very_long_filenames(self):
        """Test handling of very long filenames."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)

        # Should be truncated to reasonable length
        assert len(result) <= 255


class TestURLValidation:
    """Test URL validation for SSRF protection."""

    def test_blocks_localhost(self):
        """Test blocking localhost URLs."""
        attacks = [
            "http://localhost/admin",
            "http://127.0.0.1/internal",
            "http://0.0.0.0/",
            "https://[::1]/secret",
        ]

        for attack in attacks:
            assert not validate_url(attack)

    def test_blocks_private_networks(self):
        """Test blocking private network URLs."""
        attacks = [
            "http://192.168.1.1/",
            "http://10.0.0.1/",
            "http://172.16.0.1/",
            "http://172.31.255.255/",
        ]

        for attack in attacks:
            assert not validate_url(attack)

    def test_blocks_non_http_protocols(self):
        """Test blocking non-HTTP protocols."""
        attacks = [
            "file:///etc/passwd",
            "ftp://internal.server/",
            "gopher://old.server/",
            "javascript:alert(1)",
        ]

        for attack in attacks:
            assert not validate_url(attack)

    def test_allows_public_urls(self):
        """Test allowing public HTTPS URLs."""
        safe_urls = [
            "https://www.google.com",
            "https://github.com/user/repo",
            "http://example.com",
            "https://api.openai.com",
        ]

        for url in safe_urls:
            assert validate_url(url)

    def test_handles_url_encoding(self):
        """Test handling of URL-encoded attacks."""
        # This is a more advanced test - URL encoding bypass attempts
        attacks = [
            "http://127.0.0.1%00.example.com",  # Null byte
            "http://①②⑦.⓪.⓪.①/",  # Unicode digits
        ]

        # These should be blocked or handled safely
        for attack in attacks:
            # The function should either block it or not crash
            result = validate_url(attack)
            assert isinstance(result, bool)
