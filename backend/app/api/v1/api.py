"""API v1 root router."""

from fastapi import APIRouter

from .system import router as system_router

api_router = APIRouter()
api_router.include_router(system_router)

__all__ = ["api_router"]

