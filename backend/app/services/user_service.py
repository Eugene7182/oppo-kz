"""User service: CRUD helpers and admin seeding."""

from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.settings import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreateMinimal


def get_user(db: Session, user_id: str) -> User | None:
    """Return user by id."""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return user by email."""
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, user_in: UserCreateMinimal) -> User:
    """Create new user."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
        status=UserStatus.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_admin(db: Session | None = None) -> User | None:
    """Create admin user from ENV if absent."""
    email = settings.admin_email
    password = settings.admin_password
    if not email or not password:
        return None
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True
    try:
        user = get_user_by_email(db, email)
        if user:
            return user
        admin_in = UserCreateMinimal(email=email, password=password, role=UserRole.admin)
        return create_user(db, admin_in)
    finally:
        if owns_session:
            db.close()


def _cli() -> None:
    parser = argparse.ArgumentParser(description="User service utilities")
    parser.add_argument("--ensure-admin", action="store_true", help="Create admin user if missing")
    args = parser.parse_args()
    if args.ensure_admin:
        ensure_admin()


if __name__ == "__main__":
    _cli()
