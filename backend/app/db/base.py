"""Import SQLAlchemy models for Alembic."""

from app.db.base_class import Base  # noqa: F401
from app.db.models.user import User  # noqa: F401

__all__ = ["Base", "User"]

