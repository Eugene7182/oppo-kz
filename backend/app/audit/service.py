from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Any, Optional

def log_action(db: Session, *, username: Optional[str], action: str, payload: Any = None) -> None:
    try:
        db.execute(text("insert into audit_log (username, action, payload) values (:u,:a, to_jsonb(:p::text))"),
                   {"u": username, "a": action, "p": str(payload) if payload is not None else None})
        db.commit()
    except Exception:
        # Do not break business flow on audit errors
        db.rollback()
