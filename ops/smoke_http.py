"""
Простой, но полный смоук-тест прод-стенда:
- проверяет /health и /version
- логинится админом (если заданы ADMIN_USER / ADMIN_PASS)
- дергает invites и несколько ключевых модулей
- печатает понятные ошибки и падает с ненулевым кодом при проблемах

Запускается из GitHub Actions (см. workflow ниже).
"""
from __future__ import annotations
import os, sys, json, time
import urllib.parse as up
import requests

BASE = os.getenv("APP_BASE_URL", "").rstrip("/")
FRONT = os.getenv("FRONT_URL", "").rstrip("/")
ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASS = os.getenv("ADMIN_PASS", "")

def must(cond: bool, msg: str):
    if not cond:
        print(f"❌ {msg}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ {msg}")

def get_json(url: str, headers: dict | None = None, method: str = "GET", data: dict | None = None):
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        else:
            r = requests.post(url, headers=headers, json=data, timeout=30)
        return r.status_code, (r.json() if r.headers.get("content-type","").startswith("application/json") else r.text)
    except Exception as e:
        return 0, f"EXC: {e}"

def main():
    must(bool(BASE), "APP_BASE_URL задан")
    print(f"BASE = {BASE}")
    if FRONT:
        print(f"FRONT = {FRONT}")

    # 1) health
    sc, js = get_json(f"{BASE}/api/v1/health")
    must(sc == 200 and isinstance(js, dict) and js.get("status") == "ok", "/api/v1/health отвечает OK")

    # 2) version (допускаем /version в корне как фоллбек)
    for path in ("/api/v1/version", "/version"):
        sc, js = get_json(f"{BASE}{path}")
        if sc == 200:
            must(True, f"{path} отвечает 200")
            break
    else:
        must(False, "нет валидного ответa от /api/v1/version")

    token = None
    if ADMIN_USER and ADMIN_PASS:
        # 3) login
        sc, js = get_json(f"{BASE}/api/v1/auth/login", method="POST",
                          data={"username": ADMIN_USER, "password": ADMIN_PASS})
        must(sc == 200, "логин админа 200")
        if isinstance(js, dict):
            token = js.get("access_token") or js.get("token") or js.get("access")
        must(bool(token), "получили токен")
        headers = {"Authorization": f"Bearer {token}"}

        # 4) invites доступен и отвечает
        sc, js = get_json(f"{BASE}/api/v1/invites?only_active=true", headers=headers)
        must(sc == 200, "/api/v1/invites отвечает 200")

        # 5) feature flags (если есть)
        sc, js = get_json(f"{BASE}/api/v1/feature-flags", headers=headers)
        if sc == 200:
            print("ℹ️ feature-flags OK")

        # 6) продажи (сети/промоутеры) — опционально, не валим деплой если 404
        for path in ("/api/v1/sales/networks", "/api/v1/sales/promoters", "/api/v1/final-sales"):
            sc, _ = get_json(f"{BASE}{path}", headers=headers)
            if sc == 200:
                print(f"ℹ️ {path} OK")
            elif sc in (401, 403):
                must(False, f"{path} недоступен по авторизации")
            else:
                print(f"⚠️ {path} вернул {sc} — пропускаем")

    # 7) фронт живой (если задан FRONT_URL)
    if FRONT:
        try:
            r = requests.get(FRONT, timeout=30)
            must(r.status_code in (200, 304), "фронт доступен")
        except Exception as e:
            must(False, f"фронт недоступен: {e}")

    print("🎉 Smoke passed")

if __name__ == "__main__":
    main()
