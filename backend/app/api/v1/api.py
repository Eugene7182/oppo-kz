from fastapi import APIRouter
from .routes.health import router as health_router
from .routes.version import router as version_router
from .routes.auth import router as auth_router
from .routes.invites import router as invites_router
from .routes.sales_v2 import router as sales_router
from .routes.periods import router as periods_router
from .routes.plans import router as plans_router
from .insights import router as insights_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(invites_router)
api_router.include_router(sales_router)
api_router.include_router(periods_router)
api_router.include_router(plans_router)
api_router.include_router(insights_router, prefix="/insights", tags=["insights"])
