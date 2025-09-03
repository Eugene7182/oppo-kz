from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from app.db.models.user import User

def require_roles(*roles: str):
    def _checker(current: User = Depends(get_current_user)) -> User:
        if current.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current
    return _checker
