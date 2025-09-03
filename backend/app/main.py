from __future__ import annotations
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import PROJECT_NAME, PROJECT_VERSION, CORS_ORIGINS, ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.invite import Invite  # noqa: F401
from app.api.v1.api import api_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health", include_in_schema=False)
def health_root():
    return {"status": "ok"}

@app.head("/", include_in_schema=False)
def head_root():
    return Response(status_code=200)

app.include_router(api_router, prefix="/api/v1")

def _ensure_users_table_schema() -> None:
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'users'
        """)).mappings().all()
        cols = {r["column_name"]: r for r in rows}
        if not cols:
            logger.info("users table not found; create_all will create it")
            return

        id_info = cols.get("id")
        if id_info and id_info["data_type"] in ("integer", "bigint"):
            # найти все FK на users(id), снять их, привести типы, затем конвертировать id
            fk_rows = conn.execute(text("""
                SELECT con.conname AS constraint_name, rel_t.relname AS table_name, att2.attname AS column_name
                FROM pg_constraint con
                JOIN pg_class rel_t ON rel_t.oid = con.conrelid
                JOIN LATERAL unnest(con.conkey) AS fk(attnum) ON TRUE
                JOIN pg_attribute att2 ON att2.attrelid = con.conrelid AND att2.attnum = fk.attnum
                WHERE con.contype='f' AND con.confrelid='public.users'::regclass
            """)).mappings().all()
            for r in fk_rows:
                conn.execute(text(f'ALTER TABLE public."{r["table_name"]}" DROP CONSTRAINT "{r["constraint_name"]}"'))
            for r in fk_rows:
                conn.execute(text(f'ALTER TABLE public."{r["table_name"]}" ALTER COLUMN "{r["column_name"]}" TYPE VARCHAR(36) USING "{r["column_name"]}"::varchar'))
            if id_info["column_default"]:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT"))
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar"))
            logger.info("users.id converted to VARCHAR(36)")

        if "full_name" not in cols:
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255) NULL"))
        if "password_hash" not in cols and "hashed_password" in cols:
            conn.execute(text('ALTER TABLE public.users RENAME COLUMN "hashed_password" TO "password_hash"'))
        if "password_hash" not in cols and "hashed_password" not in cols:
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))
        if "is_active" not in cols:
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true"))
        if "role" not in cols:
            conn.execute(text("ALTER TABLE public.users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'"))
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE schemaname='public' AND indexname='ix_users_email'
                ) THEN
                    CREATE UNIQUE INDEX ix_users_email ON public.users (email);
                END IF;
            END$$;
        """))

def seed_admin(db: Session) -> None:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin:
        return
    admin = User(
        email=ADMIN_EMAIL,
        full_name="Administrator",
        role="admin",
        password_hash=get_password_hash(ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Seeded admin user %s", ADMIN_EMAIL)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("create_all completed")
    try:
        _ensure_users_table_schema()
        logger.info("users table schema ensured")
    except Exception as exc:
        logger.exception("users table schema ensure failed: %s", exc)
    with SessionLocal() as db:
        seed_admin(db)
    logger.info("Startup completed")
