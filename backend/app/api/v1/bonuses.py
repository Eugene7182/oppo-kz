"""Demo bonuses routes.

Маршруты доступны только при включённом флаге ENABLE_BONUSES.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.feature_flags.deps import check_feature


router = APIRouter(prefix="/bonuses", tags=["bonuses"])


@router.get("/ping", dependencies=[Depends(check_feature("ENABLE_BONUSES"))])
async def bonuses_ping() -> dict[str, object]:
    """Simple flag-protected endpoint."""
    return {"ok": True, "feature": "bonuses"}


__all__ = ["router"]

