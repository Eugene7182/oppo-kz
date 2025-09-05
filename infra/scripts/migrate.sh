#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
alembic upgrade head
echo "[OK] Alembic upgraded to head"
