# backend/app/db/__init__.py
from __future__ import annotations

import os
from typing import Dict, Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

# Поддержка и DATABASE_URL, и DB_DSN
raw_dsn = os.getenv("DATABASE_URL") or os.getenv("DB_DSN") or "sqlite:///./dev.db"
DATABASE_URL = _normalize_db_url(raw_dsn)

connect_args: Dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = ["engine", "SessionLocal", "DATABASE_URL", "get_db"]


def to_float(value: Any) -> float: 
        """Convert a value to float, returning 0.0 on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

__all__.append("to_float")

