"""API v1 root router."""

from fastapi import APIRouter

from .auth import router as auth_router
from .system import router as system_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(auth_router)

__all__ = ["api_router"]
