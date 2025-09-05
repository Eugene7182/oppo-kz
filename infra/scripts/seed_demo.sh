#!/usr/bin/env bash
set -euo pipefail
# Seed demo data via API where это возможно.
# Требуется: bash, curl, python3. Укажи BASE_URL и креды админа.

BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"

PROMO_USER="${PROMO_USER:-pavlov}"
PROMO_NAME="${PROMO_NAME:-Иван Павлов}"
PROMO_PASS="${PROMO_PASS:-StrongPass123}"

py() { python3 - "$@"; }
http_code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "=== Seed: BASE_URL=${BASE_URL}"

# 1) Login as admin
ADMIN_TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" \
  | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") || true
if [ -z "$ADMIN_TOKEN" ]; then echo "[FAIL] admin login"; exit 1; fi
AUTHZ="Authorization: Bearer ${ADMIN_TOKEN}"
echo "[OK] admin login"

# 2) Ensure at least one user (promoter) via invite/register
INV=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/invites" \
  -H "Content-Type: application/json" -H "$AUTHZ" \
  -d "{\"username\":\"${PROMO_USER}\",\"role\":\"promoter\",\"full_name\":\"${PROMO_NAME}\",\"expires_hours\":72}") || true
CODE=$(echo "$INV" | py -c "import sys,json;print(json.load(sys.stdin).get('code',''))") || true
if [ -n "$CODE" ]; then
  curl -sS -X POST "${BASE_URL}/api/v1/auth/invites/register" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"${CODE}\",\"password\":\"${PROMO_PASS}\"}" >/dev/null || true
  echo "[OK] promoter seeded (invite/register)"
else
  echo "[WARN] invite create failed (maybe already exists)"
fi

# 3) Try to create store coefficient for the first store (if stores API exists)
stores_code=$(http_code -H "$AUTHZ" "${BASE_URL}/api/v1/stores")
if [ "$stores_code" = "200" ]; then
  STORE_ID=$(curl -sS -H "$AUTHZ" "${BASE_URL}/api/v1/stores" | py -c "import sys,json;d=json.load(sys.stdin);print((d[0]['id']) if isinstance(d,list) and d else '')" 2>/dev/null || true)
  if [ -n "$STORE_ID" ]; then
    curl -sS -X POST "${BASE_URL}/api/v1/store-coefficients" \
      -H "Content-Type: application/json" -H "$AUTHZ" \
      -d "{\"store_id\":${STORE_ID},\"code\":\"A\",\"value\":1.10}" >/dev/null || true
    echo "[OK] store coefficient created for store ${STORE_ID}"
  else
    echo "[WARN] no stores found; skip coefficients"
  fi
else
  echo "[WARN] /api/v1/stores not available; skip coefficients"
fi

# 4) Optional: feature flags default (if endpoint exists)
ff_code=$(http_code -H "$AUTHZ" "${BASE_URL}/api/v1/feature-flags")
if [ "$ff_code" = "200" ]; then
  echo "[OK] feature-flags endpoint alive"
else
  echo "[INFO] feature-flags not present (skip)"
fi

echo "=== Seed: DONE"
