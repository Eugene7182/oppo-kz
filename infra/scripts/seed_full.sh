#!/usr/bin/env bash
set -euo pipefail
# Full seed of demo data for OPPO KZ (robust: tries multiple endpoints, logs status, skips gracefully)
# Requires: bash, curl, python3
#
# Usage:
#   BASE_URL=http://localhost:8000 ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123 ./infra/scripts/seed_full.sh

BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"

py() { python3 - "$@"; }
http_code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }
jpost() { curl -sS -H "Content-Type: application/json" -H "$AUTHZ" -X POST "$@"; }
jput()  { curl -sS -H "Content-Type: application/json" -H "$AUTHZ" -X PUT  "$@"; }
jget()  { curl -sS -H "$AUTHZ" -X GET "$@"; }

echo "=== SEED FULL @ ${BASE_URL} ==="

# 0) Auth as admin
TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" \
  | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") || true
[ -n "$TOKEN" ] || { echo "[FAIL] admin login"; exit 1; }
AUTHZ="Authorization: Bearer ${TOKEN}"
echo "[OK] admin login"

# ---------- helpers ----------
probe() { # $1=METHOD $2=PATH
  local m="$1" p="$2" code
  if [ "$m" = "GET" ]; then
    code=$(http_code -H "$AUTHZ" "${BASE_URL}${p}")
  else
    code=$(http_code -H "Content-Type: application/json" -H "$AUTHZ" -X "$m" "${BASE_URL}${p}")
  fi
  echo "$code"
}

try_first() { # tries list of candidate paths for GET and returns first with 200
  local -n arr=$1
  for p in "${arr[@]}"; do
    local code; code=$(probe GET "$p")
    if [ "$code" = "200" ]; then echo "$p"; return 0; fi
  done
  echo ""
  return 1
}

post_any() { # $1=payload-json, then candidate POST endpoints...
  local payload="$1"; shift
  for p in "$@"; do
    local code
    code=$(http_code -H "Content-Type: application/json" -H "$AUTHZ" -X POST "${BASE_URL}${p}" -d "$payload")
    echo "POST $p -> [$code]"
    if [ "$code" = "200" ] || [ "$code" = "201" ]; then
      jpost "${BASE_URL}${p}" -d "$payload" | py -c "import sys,json;d=json.load(sys.stdin);print(d if isinstance(d,dict) else 'OK')" >/dev/null 2>&1 || true
      return 0
    fi
  done
  return 1
}

# ---------- 1) Stores ----------
stores_candidates_get=( "/api/v1/stores" "/api/v1/dict/stores" "/api/v1/reference/stores" )
stores_candidates_post=( "/api/v1/stores" "/api/v1/dict/stores" "/api/v1/reference/stores" )
stores_payloads=(
'{"code":"WH1","name":"Central Warehouse","region":"KZ","city":"Almaty"}'
'{"code":"A01","name":"Almaty Dostyk","region":"KZ","city":"Almaty"}'
'{"code":"A02","name":"Almaty Mega","region":"KZ","city":"Almaty"}'
'{"code":"N01","name":"Astana KhanShatyr","region":"KZ","city":"Astana"}'
)
stores_path=$(try_first stores_candidates_get) || true
if [ -z "$stores_path" ]; then stores_path="/api/v1/stores"; fi
echo "[INFO] stores GET path: $stores_path"
for pl in "${stores_payloads[@]}"; do
  post_any "$pl" "${stores_candidates_post[@]}" || echo "[WARN] store insert failed (skipped)"
done

# fetch store ids
STORE_IDS=$(jget "${BASE_URL}${stores_path}" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(str(x.get('id')) for x in d if isinstance(d,list)))" 2>/dev/null || true)
echo "[INFO] store ids: ${STORE_IDS}"

# ---------- 2) SKUs ----------
skus_candidates_get=( "/api/v1/skus" "/api/v1/sku" "/api/v1/products" "/api/v1/items" )
skus_candidates_post=( "/api/v1/skus" "/api/v1/sku" "/api/v1/products" "/api/v1/items" )
skus_payloads=(
'{"code":"OPPO-A1K","name":"OPPO A1K","category":"phone","uom":"pcs"}'
'{"code":"OPPO-RENO10","name":"OPPO Reno 10","category":"phone","uom":"pcs"}'
'{"code":"OPPO-ENCOBUDS2","name":"OPPO Enco Buds 2","category":"accessory","uom":"pcs"}'
)
skus_path=$(try_first skus_candidates_get) || true
[ -z "$skus_path" ] && skus_path="/api/v1/skus"
echo "[INFO] skus GET path: $skus_path"
for pl in "${skus_payloads[@]}"; do
  post_any "$pl" "${skus_candidates_post[@]}" || echo "[WARN] sku insert failed (skipped)"
done

# ---------- 3) Price List (valid_from/today, valid_to/+90d) ----------
today=$(date +%F)
valid_to=$(date -d "+90 days" +%F 2>/dev/null || date -v+90d +%F)
pricelist_candidates_post=( "/api/v1/price-list" "/api/v1/pricelist" "/api/v1/sku/price-list" )
prices_payloads=(
"{\"sku_code\":\"OPPO-A1K\",\"price\":79990,\"valid_from\":\"$today\",\"valid_to\":\"$valid_to\"}"
"{\"sku_code\":\"OPPO-RENO10\",\"price\":199990,\"valid_from\":\"$today\",\"valid_to\":\"$valid_to\"}"
"{\"sku_code\":\"OPPO-ENCOBUDS2\",\"price\":19990,\"valid_from\":\"$today\",\"valid_to\":\"$valid_to\"}"
)
for pl in "${prices_payloads[@]}"; do
  post_any "$pl" "${pricelist_candidates_post[@]}" || echo "[WARN] price-list insert failed (skipped)"
done

# ---------- 4) Initial Stock / Balances ----------
stock_candidates_post=( "/api/v1/stock" "/api/v1/stock/put" "/api/v1/stock/balance" "/api/v1/stock/balances" )
if [ -n "$STORE_IDS" ]; then
  FIRST_STORE=$(echo "$STORE_IDS" | cut -d',' -f1)
  stock_payloads=(
  "{\"store_id\":${FIRST_STORE},\"sku_code\":\"OPPO-A1K\",\"qty\":50}"
  "{\"store_id\":${FIRST_STORE},\"sku_code\":\"OPPO-RENO10\",\"qty\":20}"
  "{\"store_id\":${FIRST_STORE},\"sku_code\":\"OPPO-ENCOBUDS2\",\"qty\":100}"
  )
  for pl in "${stock_payloads[@]}"; do
    post_any "$pl" "${stock_candidates_post[@]}" || echo "[WARN] stock insert failed (skipped)"
  done
fi

# ---------- 5) Sales (promoter/network) ----------
sales_candidates_post=( "/api/v1/sales" "/api/v1/sales/promoter" "/api/v1/sales/network" )
sales_payloads=(
"{\"store_code\":\"A01\",\"sku_code\":\"OPPO-A1K\",\"qty\":2,\"sold_at\":\"$today\",\"promoter\":\"pavlov\"}"
"{\"store_code\":\"A01\",\"sku_code\":\"OPPO-RENO10\",\"qty\":1,\"sold_at\":\"$today\",\"promoter\":\"pavlov\"}"
"{\"store_code\":\"A02\",\"sku_code\":\"OPPO-ENCOBUDS2\",\"qty\":5,\"sold_at\":\"$today\",\"promoter\":\"pavlov\"}"
)
for pl in "${sales_payloads[@]}"; do
  post_any "$pl" "${sales_candidates_post[@]}" || echo "[WARN] sale insert failed (skipped)"
done

# ---------- 6) Shipments / In-Transit ----------
ship_candidates_post=( "/api/v1/stock/shipments" "/api/v1/shipments" )
ship_payload="{\"from_code\":\"WH1\",\"to_code\":\"A01\",\"sku_code\":\"OPPO-A1K\",\"qty\":10,\"shipped_at\":\"$today\"}"
post_any "$ship_payload" "${ship_candidates_post[@]}" || echo "[WARN] shipments insert failed (skipped)"

intransit_candidates_post=( "/api/v1/stock/in-transit" "/api/v1/in-transit" )
intransit_payload="{\"from_code\":\"WH1\",\"to_code\":\"A02\",\"sku_code\":\"OPPO-RENO10\",\"qty\":3,\"depart_at\":\"$today\"}"
post_any "$intransit_payload" "${intransit_candidates_post[@]}" || echo "[WARN] in-transit insert failed (skipped)"

# ---------- 7) Bonus Grid (simple) ----------
bonus_candidates_post=( "/api/v1/bonus-grid" "/api/v1/bonus" "/api/v1/payouts" )
bonus_payloads=(
"{\"role\":\"promoter\",\"sku_code\":\"OPPO-A1K\",\"type\":\"percent\",\"value\":3.0}"
"{\"role\":\"promoter\",\"sku_code\":\"OPPO-RENO10\",\"type\":\"percent\",\"value\":4.0}"
"{\"role\":\"promoter\",\"sku_code\":\"OPPO-ENCOBUDS2\",\"type\":\"fixed\",\"value\":500}"
)
for pl in "${bonus_payloads[@]}"; do
  post_any "$pl" "${bonus_candidates_post[@]}" || echo "[WARN] bonus-grid insert failed (skipped)"
done

# ---------- 8) Store Coefficients ----------
coeff_path_candidates=( "/api/v1/store-coefficients" )
coeff_payloads=(
"{\"store_id\":1,\"code\":\"A\",\"value\":1.10}"
"{\"store_id\":2,\"code\":\"B\",\"value\":0.95}"
)
for pl in "${coeff_payloads[@]}"; do
  post_any "$pl" "${coeff_path_candidates[@]}" || echo "[WARN] coeff insert failed (skipped)"
done

# ---------- 9) AI / Recommendations warm-up (optional GETs) ----------
ai_warm=( "/api/v1/ai" "/api/v1/ai/recommendations" "/api/v1/ai/alerts" "/api/v1/ai/suggest_transfer" )
for p in "${ai_warm[@]}"; do
  code=$(probe GET "$p")
  echo "[AI] GET $p -> [$code]"
done

echo "=== SEED FULL: DONE ==="
