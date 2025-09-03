"""
AutoDoctor: читает логи Render и автоматически правит/создаёт файлы проекта.
Фокус на типовых блокерах:
  1) /api/v1/health и /api/v1/version — гарантируем наличие и подключение маршрутов.
  2) frontend/src/shared/api/http.ts — добавляем fallback VITE_API_URL.
  3) Добавляем ops/smoke_http.py, если отсутствует.
  4) Добавляем .github/workflows/deploy_and_smoke.yml, если отсутствует.

ENV (передаёт workflow):
  - RENDER_API_KEY
  - RENDER_BACKEND_SERVICE_ID
  - APP_BASE_URL (не обязательно; используем только для инфо)
Режим коммита настраивается в YAML (push в main или PR).

⚠️ Скрипт ИДЕМПОТЕНТЕН: повторный прогон не плодит дублей.
"""

from __future__ import annotations
import os, re, sys, textwrap, json
from pathlib import Path

# ===== Настройки окружения =====
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
SERVICE_ID = os.getenv("RENDER_BACKEND_SERVICE_ID")
RENDER_API = "https://api.render.com/v1"

# ===== Утилиты =====
def log(msg: str):
    print(f"[autodoctor] {msg}")

def read_file(p: Path) -> str | None:
    return p.read_text(encoding="utf-8") if p.exists() else None

def write_file(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    log(f"wrote: {p}")

def patch_frontend_http_ts():
    target = Path("frontend/src/shared/api/http.ts")
    text = read_file(target)
    if text is None:
        log("skip frontend http.ts: not found")
        return False
    if "VITE_API_URL" in text:
        log("frontend http.ts: VITE_API_URL already present")
        return False
    # минимально инвазивная правка
    if "const BASE = " in text:
        new = text.replace("const BASE = ", "const BASE = import.meta.env.VITE_API_URL || ", 1)
    else:
        new = 'const BASE = import.meta.env.VITE_API_URL || "";\n' + text
    write_file(target, new)
    return True

def ensure_version_routes():
    target = Path("backend/app/api/v1/routes/version.py")
    need_write = False
    content = read_file(target)
    expected = textwrap.dedent("""\
        from datetime import datetime, timezone
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/health", tags=["system"], summary="Health check")
        def health():
            return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}

        @router.get("/version", tags=["system"], summary="API version")
        def version():
            return {"name": "oppo-kz-api", "version": "0.1.0"}
    """)
    if content is None or "def health" not in content or "def version" not in content:
        write_file(target, expected)
        need_write = True

    # подключение роутера в main.py
    main_py = Path("backend/app/main.py")
    mtext = read_file(main_py) or ""
    import_line = "from app.api.v1.routes import version as version_router"
    include_line = "app.include_router(version_router.router, prefix=\"/api/v1\")"

    changed = False
    if import_line not in mtext:
        mtext = import_line + "\n" + mtext
        changed = True
    if include_line not in mtext:
        # добавим include к концу файла (без дублирования)
        mtext = mtext.rstrip() + "\n" + include_line + "\n"
        changed = True
    if changed:
        write_file(main_py, mtext)
        need_write = True

    return need_write

def ensure_smoke_script():
    target = Path("ops/smoke_http.py")
    if target.exists():
        return False
    content = textwrap.dedent("""\
        from __future__ import annotations
        import os, sys, requests

        BASE = os.getenv("APP_BASE_URL","").rstrip("/")
        FRONT = os.getenv("FRONT_URL","").rstrip("/")
        ADMIN_USER = os.getenv("ADMIN_USER","")
        ADMIN_PASS = os.getenv("ADMIN_PASS","")

        def must(ok: bool, msg: str):
            if not ok:
                print("❌ " + msg, file=sys.stderr); sys.exit(1)
            print("✅ " + msg)

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
            code, js = jget(f"{BASE}/api/v1/health")
            must(code == 200 and isinstance(js, dict) and js.get("status") == "ok", "/api/v1/health OK")

            ok = False
            for path in ("/api/v1/version", "/version"):
                code, _ = jget(f"{BASE}{path}")
                if code == 200: ok=True; break
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

            if FRONT:
                try:
                    r = requests.get(FRONT, timeout=30)
                    must(r.status_code in (200,304), "фронт доступен")
                except Exception as e:
                    must(False, f"фронт недоступен: {e}")

            print("🎉 Smoke passed")

        if __name__ == "__main__":
            main()
    """)
    write_file(target, content)
    return True

def ensure_deploy_and_smoke_workflow():
    target = Path(".github/workflows/deploy_and_smoke.yml")
    if target.exists():
        return False
    content = textwrap.dedent("""\
        name: Deploy and Smoke (single env)

        on:
          push: { branches: [ "main" ] }
          workflow_dispatch: {}

        permissions: { contents: read }

        jobs:
          deploy:
            runs-on: ubuntu-latest
            env:
              RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
              SERVICE_ID: ${{ secrets.RENDER_BACKEND_SERVICE_ID || secrets.RENDER_STAGING_SERVICE_ID }}
              APP_BASE_URL: ${{ secrets.APP_BASE_URL || secrets.STAGING_APP_BASE_URL }}
            steps:
              - uses: actions/checkout@v4
              - run: sudo apt-get update && sudo apt-get install -y jq
              - name: Trigger deploy
                id: kick
                run: |
                  set -e
                  DEPLOY_ID=$(curl -sS -X POST "https://api.render.com/v1/services/${SERVICE_ID}/deploys" \\
                    -H "Authorization: Bearer ${RENDER_API_KEY}" -H "Content-Type: application/json" --data '{}' | jq -r '.id')
                  echo "deploy_id=${DEPLOY_ID}" >> $GITHUB_OUTPUT
              - name: Wait until live
                env: { DEPLOY_ID: ${{ steps.kick.outputs.deploy_id }} }
                run: |
                  set -e
                  for i in $(seq 1 120); do
                    STATUS=$(curl -sS "https://api.render.com/v1/services/${SERVICE_ID}/deploys/${DEPLOY_ID}" \\
                      -H "Authorization: Bearer ${RENDER_API_KEY}" | jq -r '.status')
                    echo "status: $STATUS"
                    if [ "$STATUS" = "live" ]; then exit 0; fi
                    if [ "$STATUS" = "failed" ] || [ "$STATUS" = "canceled" ]; then exit 1; fi
                    sleep 10
                  done
                  echo "Timeout"; exit 1

          smoke:
            runs-on: ubuntu-latest
            needs: deploy
            env:
              APP_BASE_URL: ${{ secrets.APP_BASE_URL || secrets.STAGING_APP_BASE_URL }}
              FRONT_URL: ${{ secrets.FRONT_URL || secrets.STAGING_FRONT_URL }}
              ADMIN_USER: ${{ secrets.ADMIN_USER }}
              ADMIN_PASS: ${{ secrets.ADMIN_PASS }}
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with: { python-version: "3.11" }
              - run: pip install requests
              - run: python ops/smoke_http.py
    """)
    write_file(target, content)
    return True

def get_render_logs() -> list[str]:
    """ Берём последние логи (без фанатизма — дальше используем только сигнатуры). """
    if not (RENDER_API_KEY and SERVICE_ID):
        log("No Render creds; skip reading logs")
        return []
    import requests, datetime as dt
    headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(minutes=30)
    params = {
        "startTime": start.isoformat() + "Z",
        "endTime": end.isoformat() + "Z",
        "serviceIds": SERVICE_ID,
        "limit": "1000",
        "order": "desc",
    }
    try:
        r = requests.get(f"{RENDER_API}/logs", headers=headers, params=params, timeout=30)
        r.raise_for_status()
        js = r.json()
        items = js.get("logs", js if isinstance(js, list) else [])
        return [ (it.get("message") or it.get("log") or "") for it in items ]
    except Exception as e:
        log(f"Render logs error: {e}")
        return []

def main():
    logs = get_render_logs()
    text_all = "\n".join(logs)

    changed = False

    # 1) Если видим проблемы с /health|/version или импортами — гарантируем маршруты
    if re.search(r"(404|No route).*(/api/v1/health|/api/v1/version)", text_all, re.I) or \
       re.search(r"AssertionError: app\.main.*'app'", text_all) or \
       re.search(r"ModuleNotFoundError: .*routes\.version", text_all) or \
       True:  # полезно держать эндпоинты всегда
        if ensure_version_routes():
            changed = True

    # 2) front BASE fallback
    if re.search(r"(CORS|TypeError|failed to fetch|NetworkError)", text_all, re.I) or True:
        if patch_frontend_http_ts():
            changed = True

    # 3) smoke
    if ensure_smoke_script():
        changed = True

    # 4) deploy+smoke workflow
    if ensure_deploy_and_smoke_workflow():
        changed = True

    if not changed:
        log("no changes")
    else:
        log("files changed")

if __name__ == "__main__":
    main()
