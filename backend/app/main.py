# backend/app/main.py
from __future__ import annotations
import logging
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from alembic import command
from alembic.config import Config as AlembicConfig

from app.core.config import PROJECT_NAME, PROJECT_VERSION, CORS_ORIGINS, RUN_MIGRATIONS_ON_STARTUP, ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.db.models.user import User
from app.api.v1.api import api_router

logger = logging.getLogger(__name__)
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

def run_migrations() -> None:
    cfg = AlembicConfig("alembic.ini")
    command.upgrade(cfg, "head")
    logger.info("Alembic migrations applied")

def seed_admin(db: Session) -> None:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin:
        return
    admin = User(email=ADMIN_EMAIL, full_name="Administrator", role="admin", password_hash=get_password_hash(ADMIN_PASSWORD), is_active=True)
    db.add(admin)
    db.commit()
    logger.info("Seeded admin user %s", ADMIN_EMAIL)

@app.on_event("startup")
def on_startup():
    if RUN_MIGRATIONS_ON_STARTUP:
        run_migrations()
    with SessionLocal() as db:
        seed_admin(db)
    logger.info("Startup completed")
