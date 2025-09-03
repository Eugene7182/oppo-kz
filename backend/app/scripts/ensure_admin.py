# backend/app/scripts/ensure_admin.py
from __future__ import annotations
import os
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models import User, UserRole
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    admin_username = os.getenv("ADMIN_USERNAME", "admin@oppo.kz")
    admin_name = os.getenv("ADMIN_NAME", "Super Admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "StrongPass123")

    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.username == admin_username))
        if u:
            print("Admin exists")
            return
        user = User(
            username=admin_username,
            full_name=admin_name,
            role=UserRole.admin.value if hasattr(UserRole, "admin") else "admin",
            hashed_password=pwd.hash(admin_pass),
        )
        db.add(user)
        db.commit()
        print("Admin created:", admin_username)

if __name__ == "__main__":
    main()
