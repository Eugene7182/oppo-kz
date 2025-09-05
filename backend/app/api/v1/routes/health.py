from pathlib import Path

from fastapi import APIRouter

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from app.db.session import engine

router = APIRouter()


@router.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@router.get("/db_status", tags=["system"])
def db_status():
    cfg = Config(str(Path(__file__).resolve().parents[4] / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    head = script.get_current_head()
    with engine.connect() as conn:
        context = MigrationContext.configure(conn)
        current = context.get_current_revision()
    ok = current == head
    return {"ok": ok, "alembic_head": head, "alembic_current": current}
