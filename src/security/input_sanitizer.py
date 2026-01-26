"""Input sanitization and validation for security."""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Dangerous patterns that might indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+previous",
    r"disregard\s+previous",
    r"forget\s+previous",
    r"new\s+instructions:",
    r"system\s+prompt:",
    r"</?\s*system\s*>",
    r"<\s*assistant\s*>",
    r"\[SYSTEM\]",
    r"\[INST\]",
    r"###\s*Instruction",
]

# Maximum lengths to prevent abuse
MAX_IDEA_LENGTH = 5000
MAX_PROFILE_NAME_LENGTH = 100
MAX_PROFILE_DESCRIPTION_LENGTH = 2000
MAX_AI_OUTPUT_LENGTH = 50000


def sanitize_user_input(text: str, input_type: str = "general") -> str:
    """
    Sanitize user input to prevent prompt injection and other attacks.

    Args:
        text: The user input to sanitize
        input_type: Type of input (idea, profile_name, profile_description, general)

    Returns:
        Sanitized text

    Raises:
        ValueError: If input is suspicious or exceeds limits
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Check length limits based on input type
    max_length = {
        "idea": MAX_IDEA_LENGTH,
        "profile_name": MAX_PROFILE_NAME_LENGTH,
        "profile_description": MAX_PROFILE_DESCRIPTION_LENGTH,
        "general": MAX_IDEA_LENGTH
    }.get(input_type, MAX_IDEA_LENGTH)

    if len(text) > max_length:
        logger.warning(f"Input exceeds max length: {len(text)} > {max_length}")
        raise ValueError(f"Input too long. Maximum {max_length} characters allowed.")

    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(f"Potential prompt injection detected: {pattern}")
            raise ValueError(
                "Input contains suspicious content. "
                "Please rephrase your input without special instructions."
            )

    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def validate_ai_output(text: str) -> str:
    """
    Validate AI output to ensure it's safe to display.

    Args:
        text: The AI-generated text to validate

    Returns:
        Validated text

    Raises:
        ValueError: If output is suspicious
    """
    if not text:
        return ""

    # Check length
    if len(text) > MAX_AI_OUTPUT_LENGTH:
        logger.warning(f"AI output exceeds max length: {len(text)}")
        text = text[:MAX_AI_OUTPUT_LENGTH] + "... [truncated]"

    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Basic XSS prevention - remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)

    return text


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: The filename to sanitize

    Returns:
        Safe filename
    """
    # Remove path separators
    filename = re.sub(r'[/\\]+', '_', filename)

    # Remove consecutive dots to prevent .. but keep single dots for extensions
    filename = re.sub(r'\.\.+', '_', filename)

    # Remove special characters but keep dots, underscores, hyphens
    filename = re.sub(r'[^\w\s\-\.]', '', filename)

    # Remove leading dots and spaces
    filename = filename.lstrip('. ')

    # Remove trailing spaces (but keep trailing dots for extensions)
    filename = filename.rstrip(' ')

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename or "untitled"


def validate_url(url: str) -> bool:
    """
    Validate URL to prevent SSRF and other attacks.

    Args:
        url: URL to validate

    Returns:
        True if URL is safe, False otherwise
    """
    if not url:
        return False

    # Basic URL validation
    url_lower = url.lower()

    # Must be HTTP or HTTPS
    if not (url_lower.startswith('http://') or url_lower.startswith('https://')):
        return False

    # Block localhost and private IPs
    blocked_patterns = [
        r'localhost',
        r'127\.0\.0\.1',
        r'0\.0\.0\.0',
        r'192\.168\.',
        r'10\.',
        r'172\.(1[6-9]|2[0-9]|3[01])\.',
        r'\[::1\]',
        r'\[::ffff:127\.0\.0\.1\]',
    ]

    for pattern in blocked_patterns:
        if re.search(pattern, url_lower):
            logger.warning(f"Blocked private/local URL: {url}")
            return False

    return True
