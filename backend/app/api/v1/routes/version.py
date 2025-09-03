from fastapi import APIRouter
from app.core.config import PROJECT_VERSION

router = APIRouter()

@router.get("/version", tags=["system"])
def version():
    return {"version": PROJECT_VERSION}
