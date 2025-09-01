from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.stores import router as stores_router
from .routes.sku import router as sku_router
from .routes.price_list import router as price_router
from .routes.sales import router as sales_router
from .routes.reconciliation import router as recon_router
from .routes.final_sales import router as final_router
from .routes.invites import router as invites_router
from .routes.bonus_grids import router as bonus_router  # <-- добавили
from app.api.v1.endpoints import supervisors as supervisors_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(stores_router)
api_router.include_router(sku_router)
api_router.include_router(price_router)
api_router.include_router(sales_router)
api_router.include_router(recon_router)
api_router.include_router(final_router)
api_router.include_router(invites_router)
api_router.include_router(bonus_router)  # <-- добавили
api_router.include_router(supervisors_router.router)

# >>> OPPO KZ added routers
from app.api.v1.endpoints import feature_flags, notifications, stock_requests, reports, push
api_router.include_router(feature_flags.router, prefix="/feature-flags", tags=["feature-flags"])
api_router.include_router(notifications.router,  prefix="/notifications",  tags=["notifications"])
api_router.include_router(stock_requests.router,  prefix="/stock",         tags=["stock"])
api_router.include_router(reports.router,        prefix="/reports",       tags=["reports"])
api_router.include_router(push.router,           prefix="/notifications/push", tags=["push"])
# <<< OPPO KZ added routers


from .routes import store_coefficients as store_coefficients_router
api_router.include_router(store_coefficients_router.router)

# === Added feature routers ===
from .routes import imports as imports_router
from .routes import exports as exports_router
from .routes import bonus_calc as bonus_router
from .routes import transfers as transfers_router
from .routes import ws as ws_router
from .routes import audit as audit_router
from .routes import campaigns as campaigns_router
api_router.include_router(imports_router.router)
api_router.include_router(exports_router.router)
api_router.include_router(bonus_router.router)
api_router.include_router(transfers_router.router)
api_router.include_router(ws_router.router)
api_router.include_router(audit_router.router)
api_router.include_router(campaigns_router.router)

from .routes import anomalies as anomalies_router
api_router.include_router(anomalies_router.router)

from .routes import forecast as forecast_router
api_router.include_router(forecast_router.router)
