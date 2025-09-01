from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.v1.deps import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/profile")
def me_profile(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Try DB lookup (if users table exists); fallback to auth payload.
    username = getattr(user, "username", None)
    role = getattr(user, "role", None)
    city_code = getattr(user, "city_code", None)
    try:
        r = db.execute(text("select to_regclass('users')")).scalar()
        if r and username:
            row = db.execute(text("select username, role, city_code, full_name from users where username=:u"), {"u": username}).mappings().first()
            if row:
                role = row.get("role", role)
                city_code = row.get("city_code", city_code)
                full_name = row.get("full_name", getattr(user, "full_name", None))
                return {"username": username, "role": role, "city_code": city_code, "full_name": full_name}
    except Exception:
        pass
    return {"username": username, "role": role, "city_code": city_code, "full_name": getattr(user, "full_name", None)}
