from fastapi import APIRouter, FastAPI
router = APIRouter(prefix="/_audit", tags=["_internal"])

@router.get("/routes")
def list_routes(app: FastAPI):
    # Вернёт все зарегистрированные маршруты — быстро понять, что реально поднято
    return [{"path": r.path, "name": r.name, "methods": sorted(list(r.methods))} for r in app.routes]
