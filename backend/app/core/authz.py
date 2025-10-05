from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User, UserRole, UserStatus


def require_roles(roles: Iterable[UserRole | str]):
    """Dependency factory ensuring the current user has one of the roles."""

    allowed = {UserRole(r) if isinstance(r, str) else r for r in roles}

    def _checker(current: User = Depends(get_current_user)) -> User:
        if current.status != UserStatus.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        if UserRole(current.role) not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current

    return _checker
