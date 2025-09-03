# backend/app/main.py
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone
from typing import List
# import logging  # ← раскомментируй, если захочешь приглушить passlib-лог

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.api.v1.routes import version as version_router
app.include_router(version_router.router, prefix="/api/v1")
from .db import engine, SessionLocal
from .models import Base, User
from .core.security import hash_password

# Если надо заглушить красный лог про bcrypt от passlib:
# logging.getLogger("passlib").setLevel(logging.CRITICAL)

# Важно: импортируем модели ДО create_all(), чтобы таблицы создались
try:
    from .models.user_invite import UserInvite  # noqa: F401
except Exception:
    pass
try:
    from .models.city import City  # noqa: F401
except Exception:
    pass


# --- Sentry (optional) ---
import os
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FastApiIntegration()])
        print("[sentry] enabled")
    except Exception as e:
        print("[sentry] not enabled:", e)

app = FastAPI(title="OPPO KZ API", version="0.1.0")

# -----------------------------
# CORS
# -----------------------------
def _read_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "" or raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]

CORS_ORIGINS = _read_cors_origins()
allow_credentials = not (len(CORS_ORIGINS) == 1 and CORS_ORIGINS[0] == "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Метрики Prometheus
# -----------------------------
REQS = Counter("http_requests_total", "Total HTTP requests", ["path", "method", "code"])
LAT = Histogram("http_request_duration_seconds", "Latency", ["path", "method"])

@app.middleware("http")
async def add_request_id_and_metrics(request: Request, call_next):
    request.state.req_id = str(uuid.uuid4())
    start = time.time()
    resp = await call_next(request)
    dur = time.time() - start
    REQS.labels(request.url.path, request.method, str(resp.status_code)).inc()
    LAT.labels(request.url.path, request.method).observe(dur)
    resp.headers["X-Request-Id"] = request.state.req_id
    return resp

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# -----------------------------
# Старт: таблицы + первый супер
# -----------------------------
def _seed_first_super() -> None:
    """
    Создаёт первого супер-пользователя из ENV.
    ADMIN_EMAIL/ADMIN_USERNAME, ADMIN_PASSWORD (обязателен), ADMIN_NAME.
    """
    admin_username = os.getenv("ADMIN_EMAIL") or os.getenv("ADMIN_USERNAME") or "admin@oppo.kz"
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    if not admin_password:
        return

    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == admin_username).first()
        if not exists:
            u = User(
                username=admin_username,
                full_name=admin_name,
                role="super",
                password_hash=hash_password(admin_password),
                is_active=True,
            )
            db.add(u)
            db.commit()
    finally:
        db.close()

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    _seed_first_super()

# -----------------------------
# System endpoints (+ fallback)
# -----------------------------
@app.get("/", tags=["system"])
def root():
    return {"ok": True, "service": app.title, "version": app.version}

@app.get("/api/v1/health", tags=["system"], summary="Health check")
def api_health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

@app.get("/api/v1/version", tags=["system"], summary="API version")
def api_version():
    return {"name": "oppo-kz-api", "version": app.version}

@app.get("/health", include_in_schema=False)
def health_fallback():
    return {"status": "ok"}

# HEAD на корень — для мониторинга Render
@app.head("/", include_in_schema=False)
def head_root():
    return Response(status_code=200)

# -----------------------------
# Бизнес-роутеры v1
# -----------------------------
app.include_router(api_router, prefix="/api/v1")
