from fastapi import APIRouter
import logging
import importlib

api_router = APIRouter()

# --- Стабильные роуты из ./routes (их можно импортировать напрямую) ---
from .routes.auth import router as auth_router
from .routes.stores import router as stores_router
from .routes.sku import router as sku_router
from .routes.price_list import router as price_router
from .routes.sales import router as sales_router
from .routes.reconciliation import router as recon_router
from .routes.final_sales import router as final_router
from .routes.invites import router as invites_router
from .routes.bonus_grids import router as bonus_grids_router  # <-- Переименовали alias, чтобы не затирался
from .routes import store_coefficients as store_coefficients_router

# supervisors у тебя в endpoints
from app.api.v1.endpoints import supervisors as supervisors_router

# Подключение стабильных
api_router.include_router(auth_router)
api_router.include_router(stores_router)
api_router.include_router(sku_router)
api_router.include_router(price_router)
api_router.include_router(sales_router)
api_router.include_router(recon_router)
api_router.include_router(final_router)
api_router.include_router(invites_router)
api_router.include_router(bonus_grids_router)  # <-- корректный alias
api_router.include_router(supervisors_router.router)
api_router.include_router(store_coefficients_router.router)

# --- OPPO KZ endpoints (часть стабильные, часть "хрупкие") ---
# Эти три считаем стабильными
from app.api.v1.endpoints import feature_flags, stock_requests, reports

api_router.include_router(feature_flags.router, prefix="/feature-flags", tags=["feature-flags"])
api_router.include_router(stock_requests.router, prefix="/stock", tags=["stock"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Хрупкие модули (notifications/push) поднимаем мягко — чтобы падение одного модуля не роняло весь сервис
def try_include(module_path: str, prefix: str, tags: list[str]) -> None:
    try:
        mod = importlib.import_module(module_path)
        router = getattr(mod, "router")
        api_router.include_router(router, prefix=prefix, tags=tags)
    except Exception as e:
        logging.exception("Router %s disabled: %s", module_path, e)

# Если app.models.notification ещё не готов или опять перекроется пакет — просто отключится, сервис поднимется
try_include("app.api.v1.endpoints.notifications", "/notifications", ["notifications"])
try_include("app.api.v1.endpoints.push", "/notifications/push", ["push"])

# --- Доп. роуты из ./routes ---
from .routes import imports as imports_router
from .routes import exports as exports_router
from .routes import bonus_calc as bonus_calc_router   # <-- другой alias, не затирает bonus_grids_router
from .routes import transfers as transfers_router
from .routes import ws as ws_router
from .routes import audit as audit_router
from .routes import campaigns as campaigns_router
from .routes import anomalies as anomalies_router
from .routes import forecast as forecast_router

api_router.include_router(imports_router.router)
api_router.include_router(exports_router.router)
api_router.include_router(bonus_calc_router.router)
api_router.include_router(transfers_router.router)
api_router.include_router(ws_router.router)
api_router.include_router(audit_router.router)
api_router.include_router(campaigns_router.router)
api_router.include_router(anomalies_router.router)
api_router.include_router(forecast_router.router)
