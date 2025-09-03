# backend/app/main.py
from __future__ import annotations
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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

# ВАЖНО: импортируем модели, чтобы Base.metadata "видел" таблицы
from app.db.models.user import User
from app.db.models.invite import Invite  # noqa: F401  (используется для регистрации метаданных)

from app.api.v1.api import api_router

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

# Подключаем v1-роуты
app.include_router(api_router, prefix="/api/v1")

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
    # Полностью отключаем Alembic на старте: просто создаём таблицы из моделей
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("create_all completed")
    except Exception as exc:
        logger.exception("create_all failed: %s", exc)

    # Сид-админ
    with SessionLocal() as db:
        seed_admin(db)

    logger.info("Startup completed")
