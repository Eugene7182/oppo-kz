"""FastAPI application entry point."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.logging_config import setup_logging
from app.core.settings import settings


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
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    user_id = getattr(request.state, "user_id", None)
    logging.getLogger("app.request").info(
        "request",
        extra={
            "extra": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "user_id": user_id,
                "trace_id": trace_id,
            }
        },
    )
    return response


app.include_router(api_router, prefix="/api/v1")


__all__ = ["app"]

