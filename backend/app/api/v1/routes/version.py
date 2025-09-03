# backend/app/api/v1/routes/version.py
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["system"], summary="Health check")
def health():
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

@router.get("/version", tags=["system"], summary="API version")
def version():
    # при желании подхватывай версию из env/файла
    return {"name": "oppo-kz-api", "version": "0.1.0"}
