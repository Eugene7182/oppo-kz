# backend/app/db/session.py
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Берём URL из settings или из переменной окружения
try:
    from app.core.config import settings  # type: ignore
    db_url = getattr(settings, "DATABASE_URL", None) or os.environ["DATABASE_URL"]
except Exception:
    db_url = os.environ["DATABASE_URL"]

# Форсим драйвер psycopg3 (SQLAlchemy 2.x)
if "+psycopg" not in db_url:
    db_url = db_url.replace("postgres://", "postgresql+psycopg://") \
                   .replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(db_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# алиас под старые импорты:
get_db = get_session
