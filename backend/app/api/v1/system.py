"""System endpoints: health and version."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.settings import settings
from app.db.session import engine

router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, object]:
    """Return service health and database status."""
    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    status = "ok" if db_ok else "fail"
    return {"status": status, "db": db_ok}


@router.get("/version", tags=["system"])
def version() -> dict[str, str | None]:
    """Return application version and git commit."""
    return {"version": settings.version, "commit": settings.git_commit}

