from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
# from app.api.v1.invites import router as invites_router  # подключи, если уже есть
from app.api.v1._audit import router as audit_router

app = FastAPI(title="OPPO KZ Data Platform", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.include_router(auth_router, prefix="/api/v1")
# app.include_router(invites_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
