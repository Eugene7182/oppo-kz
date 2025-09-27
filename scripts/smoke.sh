#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"
PROMO_USER="${PROMO_USER:-pavlov}"
PROMO_ROLE="${PROMO_ROLE:-promoter}"
PROMO_NAME="${PROMO_NAME:-Иван Павлов}"
PROMO_PASS="${PROMO_PASS:-StrongPass123}"
echo "=== Smoke: BASE_URL=${BASE_URL}"
py() { python3 - "$@"; }
_status() { local s="$1" m="$2"; if [ "$s" -eq 0 ]; then echo "[OK] $m"; else echo "[FAIL] $m"; fi; }
curl -sS "${BASE_URL}/api/v1/health" | py -c "import sys,json;print(json.load(sys.stdin).get('status','?'))" >/dev/null; _status $? "health"
curl -sS "${BASE_URL}/api/v1/version" | py -c "import sys,json;print(json.load(sys.stdin).get('version','?'))" >/dev/null; _status $? "version"
ADMIN_TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))"); [ -n "$ADMIN_TOKEN" ] || { echo "Admin login failed"; exit 1; }; echo "[OK] login admin"
AUTHZ="Authorization: Bearer ${ADMIN_TOKEN}"
INV_JSON=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/invites" -H "Content-Type: application/json" -H "$AUTHZ" -d "{"username":"${PROMO_USER}","role":"${PROMO_ROLE}","full_name":"${PROMO_NAME}","expires_hours":72}")
CODE=$(echo "$INV_JSON" | py -c "import sys,json;print(json.load(sys.stdin).get('code',''))"); [ -n "$CODE" ] || { echo "Invite create failed: $INV_JSON"; exit 1; }; echo "[OK] invite created: ${CODE}"
curl -sS "${BASE_URL}/api/v1/auth/invites/${CODE}" | py -c "import sys,json;print(json.load(sys.stdin).get('valid',False))" >/dev/null; _status $? "invite check"
REG_OK=0
REG_JSON=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/invites/register" -H "Content-Type: application/json" -d "{"code":"${CODE}","password":"${PROMO_PASS}"}") || REG_OK=$?
if [ $REG_OK -ne 0 ] || [ -z "$REG_JSON" ]; then
  REG_JSON=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/register" -H "Content-Type: application/json" -d "{"code":"${CODE}","password":"${PROMO_PASS}"}")
fi
PROMO_TOKEN=$(echo "$REG_JSON" | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))"); [ -n "$PROMO_TOKEN" ] || { echo "Registration failed: $REG_JSON"; exit 1; }; echo "[OK] register by invite"
REFRESH_JSON=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/refresh" -H "$AUTHZ")
NEW_TOKEN=$(echo "$REFRESH_JSON" | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))"); [ -n "$NEW_TOKEN" ] || { echo "Refresh failed: $REFRESH_JSON"; exit 1; }; echo "[OK] refresh"
STORE_ID=$(curl -sS "${BASE_URL}/api/v1/stores" -H "$AUTHZ" | py -c "import sys,json;d=json.load(sys.stdin);print((d[0]['id']) if isinstance(d,list) and d else '')" 2>/dev/null || true)
if [ -n "$STORE_ID" ]; then
  SC_JSON=$(curl -sS -X POST "${BASE_URL}/api/v1/store-coefficients" -H "Content-Type: application/json" -H "$AUTHZ" -d "{"store_id":${STORE_ID},"code":"A","value":1.15}")
  echo "$SC_JSON" | py -c "import sys,json;print(json.load(sys.stdin).get('id',''))" >/dev/null && echo "[OK] store coeff created" || echo "[WARN] store coeff skipped"
else
  echo "[WARN] no stores found, skip store-coefficients"
fi
echo "=== Smoke test: DONE"
