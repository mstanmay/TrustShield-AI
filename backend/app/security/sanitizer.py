"""
Input Sanitizer — defends against XSS, SQL Injection, and Command Injection attacks.
"""

from __future__ import annotations

import html
import re
from typing import Any


class InputSanitizer:
    """Sanitizes user input strings, URLs, and JSON payloads against XSS and injection attacks."""

    # SQL Injection patterns
    SQLI_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|EXEC|UNION)\b)",
        r"(--|/\*|\*/|;\s*SELECT|;\s*DROP|;\s*DELETE)",
        r"(' OR '1'='1'|' OR 1=1|' OR 'a'='a')",
    ]

    # Command Injection patterns
    CMD_PATTERNS = [
        r"(;|\|\||&&|`|\$\(|\${)",
        r"(\b(nc|bash|sh|cmd|powershell|curl|wget)\b\s+)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"eval\(",
    ]

    @classmethod
    def sanitize_string(cls, input_str: str) -> str:
        """Sanitize a raw string against HTML/XSS injection."""
        if not input_str:
            return input_str

        # Escape HTML tags
        clean = html.escape(input_str.strip())
        return clean

    @classmethod
    def check_sqli(cls, input_str: str) -> bool:
        """Check if input contains potential SQL injection signatures."""
        for pattern in cls.SQLI_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_cmd_injection(cls, input_str: str) -> bool:
        """Check if input contains command injection signatures."""
        for pattern in cls.CMD_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_xss(cls, input_str: str) -> bool:
        """Check if input contains XSS attack signatures."""
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False

    @classmethod
    def is_safe_input(cls, input_str: str) -> bool:
        """Verify input string is free of SQLi, Command Injection, and XSS attacks."""
        if not input_str:
            return True
        return not (cls.check_sqli(input_str) or cls.check_cmd_injection(input_str) or cls.check_xss(input_str))
