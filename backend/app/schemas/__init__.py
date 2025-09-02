# Реэкспорт схем (from app.schemas import ...)

from .auth import (
    TokenOut,
    LoginInput,
    RefreshInput,
    InviteCreateIn,
    InviteOut,
    InviteCreateOut,
)

# Если у тебя есть файл backend/app/schemas/user.py с UserOut — оставляем импорт:
try:
    from .user import UserOut
except Exception:  # на случай отсутствия user.py в ранней стадии
    class UserOut:  # заглушка, чтобы импорты не падали (лучше заменить на реальную модель)
        pass

__all__ = [
    "TokenOut",
    "LoginInput",
    "RefreshInput",
    "InviteCreateIn",
    "InviteOut",
    "InviteCreateOut",
    "UserOut",
]
