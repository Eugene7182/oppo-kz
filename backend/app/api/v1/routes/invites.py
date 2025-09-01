# backend/app/api/v1/routes/invites.py
from fastapi import APIRouter, HTTPException, status

# Важно: префикс относительный. Глобальный "/api/v1" задаётся в main.py
router = APIRouter(prefix="/invites", tags=["invites"])

@router.get("/_health", summary="Invites router is loaded")
def invites_health():
    return {"status": "ok", "module": "invites"}

# Временные заглушки, чтобы не падать. Рабочую реализацию добавим далее.
@router.post("", summary="Create invite (stub)")
def create_invite_stub():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="Invites: implement create")

@router.get("/{code}", summary="Check invite (stub)")
def check_invite_stub(code: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="Invites: implement check")

@router.post("/register", summary="Register by invite (stub)")
def register_by_invite_stub():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                        detail="Invites: implement register")
