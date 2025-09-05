#!/usr/bin/env bash
set -euo pipefail
# E2E-пробежка по AI / Stock / Reports эндпойнтам.
# Гибко проверяет существование и печатает статус-коды.

BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"

py() { python3 - "$@"; }
http_code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "=== E2E AI/STOCK/REPORTS: BASE_URL=${BASE_URL}"

# Login
TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" \
  | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") || true
[ -n "$TOKEN" ] || { echo "[FAIL] admin login"; exit 1; }
AUTHZ="Authorization: Bearer ${TOKEN}"
echo "[OK] admin login"

probe() {
  local method="$1"; shift
  local path="$1"; shift
  local code
  if [ "$method" = "GET" ]; then
    code=$(http_code -H "$AUTHZ" "${BASE_URL}${path}")
  else
    code=$(http_code -H "$AUTHZ" -H "Content-Type: application/json" -X "$method" "${BASE_URL}${path}" "$@")
  fi
  echo "[$code] $method $path"
}

# AI
for p in "/api/v1/ai" "/api/v1/ai/alerts" "/api/v1/ai/recommendations" "/api/v1/ai/suggest_transfer"; do
  probe GET "$p"
done

# STOCK
for p in "/api/v1/stock" "/api/v1/stock/requests" "/api/v1/stock/in-transit" "/api/v1/stock/shipments"; do
  probe GET "$p"
done

# REPORTS
for p in "/api/v1/reports" "/api/v1/reports/sales" "/api/v1/reports/promoters" "/api/v1/reports/sku"; do
  probe GET "$p"
done

echo "=== E2E AI/STOCK/REPORTS: DONE"
