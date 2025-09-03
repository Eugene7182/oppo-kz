# backend/app/main.py
from __future__ import annotations
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from alembic import command
from alembic.config import Config as AlembicConfig

from app.core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    CORS_ORIGINS,
    RUN_MIGRATIONS_ON_STARTUP,
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
)
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.db.models.user import User
from app.api.v1.api import api_router

# Доп: метаданные для фолбэка create_all
from app.db.base_class import Base

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION)

# CORS
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

# Все наши v1-роуты
app.include_router(api_router, prefix="/api/v1")


def _run_migrations() -> None:
    """Прямая попытка применить Alembic-миграции."""
    cfg = AlembicConfig("alembic.ini")
    logger.info("Running Alembic upgrade head...")
    command.upgrade(cfg, "head")
    logger.info("Alembic migrations applied")


def _stamp_head() -> None:
    """Проставить версию Alembic в head (после ручного create_all)."""
    cfg = AlembicConfig("alembic.ini")
    logger.warning("Stamping Alembic head after create_all fallback...")
    command.stamp(cfg, "head")


def _migrate_with_fallback() -> None:
    """
    Безопасная миграция:
    1) пытаемся alembic upgrade head;
    2) если падает — логируем стек, делаем Base.metadata.create_all(engine),
       затем проставляем stamp head, чтобы Alembic знал текущее состояние схемы.
    """
    try:
        _run_migrations()
    except Exception as exc:
        logger.exception("Alembic upgrade failed; applying fallback create_all. Error: %s", exc)
        # Фолбэк: создаём таблицы из моделей (users, invites и т.д.)
        Base.metadata.create_all(bind=engine)
        _stamp_head()
        logger.warning("Fallback create_all completed")


def seed_admin(db: Session) -> None:
    """Сид админа из ENV, если его ещё нет."""
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
    # Важно: выполняем "безопасную" миграцию с фолбэком
    if RUN_MIGRATIONS_ON_STARTUP:
        _migrate_with_fallback()

    # Затем сидим админа
    with SessionLocal() as db:
        seed_admin(db)

    logger.info("Startup completed")
