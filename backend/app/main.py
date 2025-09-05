"""FastAPI application entry point."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.api.v1.bonuses import router as bonuses_router
from app.api.v1.regions import router as regions_router
from app.api.v1.networks import router as networks_router
from app.api.v1.stores import router as stores_router
from app.api.v1.sku import router as sku_router
from app.api.v1.prices import router as prices_router
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.feature_flags.deps import FeatureDisabled


setup_logging()

app = FastAPI(title="OPPO KZ API", debug=settings.debug, version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request and response data in JSON format."""
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    user_id = getattr(request.state, "user_id", None)
    logging.getLogger("app.request").info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": user_id,
            "trace_id": trace_id,
        },
    )
    return response


app.include_router(api_router, prefix="/api/v1")
app.include_router(bonuses_router, prefix="/api/v1")
app.include_router(regions_router, prefix="/api/v1")
app.include_router(networks_router, prefix="/api/v1")
app.include_router(stores_router, prefix="/api/v1")
app.include_router(sku_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")


@app.exception_handler(FeatureDisabled)
async def _feature_disabled_handler(_: Request, __: FeatureDisabled):
    """Return uniform response when a feature is disabled."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Feature disabled", "code": "feature_disabled"},
    )


__all__ = ["app"]

