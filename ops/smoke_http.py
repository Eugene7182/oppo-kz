# ops/smoke_http.py
"""
Смоук прод-стенда:
- /api/v1/health → 200
- /api/v1/version → 200 (или /version фоллбек)
- /api/v1/auth/login → токен
- /api/v1/invites?only_active=true → 200
- (опц.) /api/v1/feature-flags, /api/v1/sales/*
- (опц.) проверка фронта по FRONT_URL

ENV:
  APP_BASE_URL (обязательно)   — https://<backend>.onrender.com
  ADMIN_USER / ADMIN_PASS      — учётка админа для логина
  FRONT_URL (опц.)             — https://<frontend>.onrender.com
"""
from __future__ import annotations
import os, sys, requests

BASE = os.getenv("APP_BASE_URL", "").rstrip("/")
FRONT = os.getenv("FRONT_URL", "").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASS = os.getenv("ADMIN_PASS", "")

def must(ok: bool, msg: str):
    if not ok:
        print(f"❌ {msg}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ {msg}")

def jget(url: str, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=30)
        ct = r.headers.get("content-type","")
        return r.status_code, (r.json() if ct.startswith("application/json") else r.text)
    except Exception as e:
        return 0, f"EXC: {e}"

def jpost(url: str, data: dict, headers=None):
    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        ct = r.headers.get("content-type","")
        return r.status_code, (r.json() if ct.startswith("application/json") else r.text)
    except Exception as e:
        return 0, f"EXC: {e}"

def main():
    must(bool(BASE), "APP_BASE_URL задан")
    print("BASE:", BASE)

    code, js = jget(f"{BASE}/api/v1/health")
    must(code == 200 and isinstance(js, dict) and js.get("status") == "ok", "/api/v1/health OK")

    ok = False
    for path in ("/api/v1/version", "/version"):
        code, _ = jget(f"{BASE}{path}")
        if code == 200:
            ok = True; print(f"ℹ️ {path} OK")
            break
    must(ok, "version endpoint OK")

    token = None
    if ADMIN_USER and ADMIN_PASS:
        code, js = jpost(f"{BASE}/api/v1/auth/login", {"username": ADMIN_USER, "password": ADMIN_PASS})
        must(code == 200, "логин 200")
        if isinstance(js, dict):
            token = js.get("access_token") or js.get("token") or js.get("access")
        must(bool(token), "токен получен")
        hdr = {"Authorization": f"Bearer {token}"}

        code, _ = jget(f"{BASE}/api/v1/invites?only_active=true", headers=hdr)
        must(code == 200, "/api/v1/invites 200")

        code, _ = jget(f"{BASE}/api/v1/feature-flags", headers=hdr)
        if code == 200: print("ℹ️ feature-flags OK")

        for path in ("/api/v1/sales/networks", "/api/v1/sales/promoters", "/api/v1/final-sales"):
            code, _ = jget(f"{BASE}{path}", headers=hdr)
            if code == 200: print(f"ℹ️ {path} OK")
            elif code in (401,403): must(False, f"{path} требует доступ")
            else: print(f"⚠️ {path} → {code}")

    if FRONT:
        try:
            r = requests.get(FRONT, timeout=30)
            must(r.status_code in (200,304), "фронт доступен")
        except Exception as e:
            must(False, f"фронт недоступен: {e}")

    print("🎉 Smoke passed")

if __name__ == "__main__":
    main()
