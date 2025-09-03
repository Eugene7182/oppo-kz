#!/usr/bin/env bash
set -euo pipefail

echo "=== Python & pip versions ==="
python -V || true
pip -V || true

echo "=== Install requirements ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Sanity check: compile sources ==="
python - <<'PY'
import compileall, sys, pathlib
root = pathlib.Path("app")
ok = compileall.compile_dir(str(root), force=True, quiet=1)
print("COMPILEALL:", "OK" if ok else "FAIL")
if not ok:
    sys.exit(1)
PY

echo "=== List schemas dir ==="
ls -la app/schemas || true
echo "=== Import check: app.main ==="
python - <<'PY'
import importlib, sys, pathlib
print("CWD:", pathlib.Path().resolve())
m = importlib.import_module("app.main")
app = getattr(m, "app", None)
assert app is not None, "FastAPI app not found as 'app' in app.main"
print("IMPORT_OK: app.main.app =", getattr(app, "title", "<no title>"))
PY

echo "=== Build script finished successfully ==="
