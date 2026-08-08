"""
Role-Based Access Control (RBAC) — permission enforcement dependencies for ADMIN, ANALYST, AUDITOR, INVESTOR.
"""

from __future__ import annotations

import enum
import logging
from typing import Callable
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    AUDITOR = "AUDITOR"
    INVESTOR = "INVESTOR"


# Role Hierarchy Permissions
ROLE_HIERARCHY = {
    UserRole.ADMIN: {UserRole.ADMIN, UserRole.ANALYST, UserRole.AUDITOR, UserRole.INVESTOR},
    UserRole.ANALYST: {UserRole.ANALYST, UserRole.INVESTOR},
    UserRole.AUDITOR: {UserRole.AUDITOR, UserRole.INVESTOR},
    UserRole.INVESTOR: {UserRole.INVESTOR},
}


class RBACPermissionChecker:
    """Dependency checker verifying required user roles."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def has_permission(self, user_role_str: str) -> bool:
        """Verify if current user role possesses required permission level."""
        try:
            current_role = UserRole(user_role_str.upper())
        except ValueError:
            return False

        permitted_set = ROLE_HIERARCHY.get(current_role, set())
        return any(role in permitted_set for role in self.allowed_roles)

    def enforce(self, user_role_str: str) -> None:
        """Enforce role permissions or raise HTTP 403 Forbidden."""
        if not self.has_permission(user_role_str):
            logger.warning("Access denied for user with role '%s' (Required: %s)", user_role_str, self.allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role level: {[r.value for r in self.allowed_roles]}",
            )


def require_roles(allowed_roles: list[UserRole]) -> RBACPermissionChecker:
    return RBACPermissionChecker(allowed_roles)
