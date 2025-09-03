# backend/app/main.py
from __future__ import annotations
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# --- конфиг / БД ---
from app.core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    CORS_ORIGINS,
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
)
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.db.base_class import Base

# Важно: импорт моделей, чтобы Base.metadata видел таблицы
from app.db.models.user import User
from app.db.models.invite import Invite  # noqa: F401

# --- логгер ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# >>> ГЛОБАЛЬНОЕ ПРИЛОЖЕНИЕ (это то, что ищет Uvicorn) <<<
app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION)

# --- CORS ---
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- простые ручки для проверки ---
@app.get("/health", include_in_schema=False)
def health_root():
    return {"status": "ok"}

@app.head("/", include_in_schema=False)
def head_root():
    return Response(status_code=200)

# --- v1 роуты ---
from app.api.v1.api import api_router  # импорт после создания app
app.include_router(api_router, prefix="/api/v1")


def _ensure_users_table_schema() -> None:
    """
    Авто-ремонт таблицы users:
    - добавляет недостающие колонки (full_name, password_hash, is_active, role),
    - переименовывает hashed_password -> password_hash,
    - конвертирует id из integer/bigint в VARCHAR(36), если нужно,
    - гарантирует уникальный индекс на email.
    """
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users'
            """)
        ).mappings().all()

        cols = {r["column_name"]: r for r in rows}
        if not cols:
            logger.info("users table not found in public schema (will be created by create_all)")
            return

        # id: integer -> varchar(36)
        id_info = cols.get("id")
        if id_info and id_info["data_type"] in ("integer", "bigint"):
            logger.warning("users.id is %s — converting to VARCHAR(36)", id_info["data_type"])
            if id_info["column_default"]:
                conn.execute(text("ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT"))
            conn.execute(text("ALTER TABLE public.users ALTER COLUMN id TYPE VARCHAR(36) USING id::varchar"))

        # full_name
        if "full_name" not in cols:
            logger.warning("users.full_name is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN full_name VARCHAR(255) NULL"))

        # password_hash
        if "password_hash" not in cols and "hashed_password" in cols:
            logger.warning("users.hashed_password found — renaming to password_hash")
            conn.execute(text('ALTER TABLE public.users RENAME COLUMN "hashed_password" TO "password_hash"'))
            cols["password_hash"] = {"column_name": "password_hash", "data_type": "character varying", "column_default": None}
        if "password_hash" not in cols and "hashed_password" not in cols:
            logger.warning("users.password_hash is missing — adding")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))

        # is_active
        if "is_active" not in cols:
            logger.warning("users.is_active is missing — adding with default true")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true"))

        # role
        if "role" not in cols:
            logger.warning("users.role is missing — adding with default 'admin'")
            conn.execute(text("ALTER TABLE public.users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'"))

        # уникальный индекс на email (если вдруг нет)
        conn.execute(
            text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE schemaname = 'public' AND indexname = 'ix_users_email'
                    ) THEN
                        CREATE UNIQUE INDEX ix_users_email ON public.users (email);
                    END IF;
                END$$;
            """)
        )


def seed_admin(db: Session) -> None:
    """Сид админа из ENV, если ещё нет."""
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


# --- запусковые хуки ---
@app.on_event("startup")
def on_startup():
    # Создаём отсутствующие таблицы (существующие не трогаем)
    Base.metadata.create_all(bind=engine)
    logger.info("create_all completed")

    # Чиним схему users, если она старого формата
    try:
        _ensure_users_table_schema()
        logger.info("users table schema ensured")
    except Exception as exc:
        logger.exception("users table schema ensure failed: %s", exc)

    # Сидим админа
    with SessionLocal() as db:
        seed_admin(db)

    logger.info("Startup completed")
