# Реэкспорт схем (from app.schemas import ...)

from .auth import (
    TokenOut,
    LoginInput,
    RefreshInput,
    InviteCreateIn,
    InviteOut,
    InviteCreateOut,
    InviteCheckOut,
)

# Если есть файл backend/app/schemas/user.py с UserOut — импортируем.
# Если его нет, оставляем мягкую заглушку, чтобы импорты не падали.
try:
    from .user import UserOut
except Exception:
    class UserOut:  # заглушка — лучше заменить на реальную модель
        pass

__all__ = [
    "TokenOut",
    "LoginInput",
    "RefreshInput",
    "InviteCreateIn",
    "InviteOut",
    "InviteCreateOut",
    "InviteCheckOut",
    "UserOut",
]
