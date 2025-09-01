    from fastapi import APIRouter, Depends, HTTPException, Query
    from datetime import datetime, timedelta, timezone
    import jwt  # PyJWT
    from typing import Optional, Dict, Any
    from app.core.settings_bi import BISettings
    from app.schemas.bi import BIEmbedOut

    router = APIRouter()

    def _make_signed_dashboard_url(site_url: str, secret: str, dashboard_id: int, params: Dict[str, Any], ttl_minutes: int = 10) -> str:
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": params or {},
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return f"{site_url}/embed/dashboard/{token}#bordered=false&titled=false"

    @router.get("/embed/dashboard", response_model=BIEmbedOut)
    async def embed_dashboard(
        dashboard_id: Optional[int] = Query(None, description="ID дашборда Metabase"),
        region_id: Optional[int] = Query(None, description="Опциональный фильтр региона"),
        store_id: Optional[int] = Query(None, description="Опциональный фильтр магазина"),
        user_id: Optional[int] = Query(None, description="Опционально: для персонализации"),
    ):
        settings = BISettings()
        if not settings.METABASE_EMBEDDING_SECRET or not settings.METABASE_SITE_URL:
            raise HTTPException(status_code=500, detail="Metabase embedding is not configured")

        dash_id = dashboard_id or settings.METABASE_DEFAULT_DASHBOARD_ID
        if not dash_id:
            raise HTTPException(status_code=400, detail="dashboard_id is required (or set METABASE_DEFAULT_DASHBOARD_ID)")

        params: Dict[str, Any] = {}
        if region_id is not None:
            params["region_id"] = region_id
        if store_id is not None:
            params["store_id"] = store_id
        if user_id is not None:
            params["user_id"] = user_id

        url = _make_signed_dashboard_url(settings.METABASE_SITE_URL, settings.METABASE_EMBEDDING_SECRET, dash_id, params)
        return BIEmbedOut(url=url)
    