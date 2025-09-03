# ops/logs_to_issues.py
from __future__ import annotations
import os, sys, re, datetime as dt
import requests

RENDER_API = "https://api.render.com/v1"
API_KEY = os.getenv("RENDER_API_KEY")
SERVICE_ID = os.getenv("BACKEND_SERVICE_ID")
REPO = os.getenv("GITHUB_REPO")
GH_TOKEN = os.getenv("GH_TOKEN")

if not (API_KEY and SERVICE_ID and REPO and GH_TOKEN):
    print("Missing env vars for monitor", file=sys.stderr)
    sys.exit(0)

ERROR_PATTERNS = {
    r"ModuleNotFoundError: No module named '(.+)'": "Python import error",
    r"sqlalchemy\.exc\.(OperationalError|InterfaceError).*": "DB connection error",
    r"alembic\.util\.CommandError": "Alembic migration error",
    r"psycopg.*(UndefinedTable|relation .* does not exist)": "DB schema mismatch (run migrations)",
    r"AssertionError: app\.main.*'app'": "FastAPI app not exposed",
    r"uvicorn\.error.*address already in use": "Port binding error",
    r"Traceback \(most recent call last\)": "Python exception",
}

def list_logs(service_id: str, start: str, end: str, limit=1000):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"startTime": start, "endTime": end, "serviceIds": service_id, "limit": str(limit), "order": "desc"}
    r = requests.get(f"{RENDER_API}/logs", headers=headers, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    return js.get("logs", js if isinstance(js, list) else [])

def ensure_issue(title: str, body: str):
    url = "https://api.github.com/repos/{}/issues".format(REPO)
    headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}
    # ищем открытый ишью с похожим заголовком
    q = f'repo:{REPO} state:open in:title "{title}"'
    sr = requests.get("https://api.github.com/search/issues", headers=headers, params={"q": q}, timeout=30)
    sr.raise_for_status()
    items = sr.json().get("items", [])
    if items:
        requests.post(items[0]["comments_url"], headers=headers, json={"body": body}, timeout=30)
        return items[0]["html_url"]
    cr = requests.post(url, headers=headers, json={"title": title, "body": body, "labels": ["autobot"]}, timeout=30)
    cr.raise_for_status()
    return cr.json()["html_url"]

def main():
    now = dt.datetime.utcnow()
    start = (now - dt.timedelta(minutes=15)).isoformat() + "Z"
    end = now.isoformat() + "Z"

    entries = list_logs(SERVICE_ID, start, end)
    hits: dict[str, list[str]] = {}
    for e in entries:
        msg = e.get("message") or e.get("log") or ""
        for pat, kind in ERROR_PATTERNS.items():
            if re.search(pat, msg):
                hits.setdefault(kind, []).append(msg[:1000])

    if not hits:
        print("No errors last 15m.")
        return

    for kind, msgs in hits.items():
        title = f"[Auto] {kind} detected in Render logs"
        body = (
            f"Окно: {start} → {end} (UTC)\n"
            f"Сервис: `{SERVICE_ID}`\n\n"
            "Примеры:\n" + "\n\n".join(f"```\n{m}\n```" for m in msgs[:5])
        )
        url = ensure_issue(title, body)
        print("Issue:", url)

if __name__ == "__main__":
    main()
