import os
import sys

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")


def request_json(path: str) -> dict:
    url = f"{API_URL}{path}"
    try:
        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"request to {url} failed: {exc}") from exc


def main() -> None:
    try:
        data = request_json("/api/v1/health")
        if data.get("status") != "ok":
            raise RuntimeError("/health returned unexpected response")

        data = request_json("/api/v1/version")
        if "version" not in data:
            raise RuntimeError("/version missing 'version' field")

        data = request_json("/api/v1/db_status")
        if not data.get("ok"):
            raise RuntimeError("/db_status reported not ok")
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE FAILED: {exc}")
        sys.exit(1)

    print("SMOKE OK")


if __name__ == "__main__":
    main()
