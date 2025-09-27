from fastapi import APIRouter
from .routes.health import router as health_router
from .routes.version import router as version_router
from .routes.auth import router as auth_router
from .routes.invites import router as invites_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(version_router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(invites_router)
