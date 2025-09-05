from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User


def require_roles(*roles: str):
    def _dependency(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
        user_role = getattr(current_user.role, "value", current_user.role)
        if str(user_role) not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user

    return _dependency
