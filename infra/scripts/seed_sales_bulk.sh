#!/usr/bin/env bash
set -euo pipefail
# Generate large volume of sales for charts/load testing.
# Tries /api/v1/sales/bulk first, falls back to per-item POST to /api/v1/sales (or variants).
#
# Vars:
#   DAYS=30        - how many days back
#   PER_DAY=50     - sales per day
#   STORES="A01,A02" (fallback, will try fetch from API)
#   SKUS="OPPO-A1K,OPPO-RENO10,OPPO-ENCOBUDS2" (fallback, will try fetch from API)
#   PROMOTER=pavlov
#
BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"
DAYS="${DAYS:-30}"
PER_DAY="${PER_DAY:-50}"
STORES="${STORES:-A01,A02}"
SKUS="${SKUS:-OPPO-A1K,OPPO-RENO10,OPPO-ENCOBUDS2}"
PROMOTER="${PROMOTER:-pavlov}"

py() { python3 - "$@"; }
http_code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "=== SEED SALES BULK @ ${BASE_URL} (days=${DAYS} per_day=${PER_DAY}) ==="

# Login
TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" \
  | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") || true
[ -n "$TOKEN" ] || { echo "[FAIL] admin login"; exit 1; }
AUTHZ="Authorization: Bearer ${TOKEN}"

# Discover store codes from API (optional)
stores_code=$(http_code -H "$AUTHZ" "${BASE_URL}/api/v1/stores")
if [ "$stores_code" = "200" ]; then
  STORES=$(curl -sS -H "$AUTHZ" "${BASE_URL}/api/v1/stores" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(sorted({(x.get('code') or x.get('store_code')) for x in d if isinstance(d,list) and (x.get('code') or x.get('store_code'))})))" 2>/dev/null || echo "$STORES")
fi
IFS=',' read -r -a store_arr <<< "$STORES"
IFS=',' read -r -a sku_arr <<< "$SKUS"

# Generate JSON array for bulk
payload=$(py - <<PY
import os, json, random, datetime
days=int(os.environ.get("DAYS","30"))
per_day=int(os.environ.get("PER_DAY","50"))
stores=os.environ.get("STORES","A01,A02").split(",")
skus=os.environ.get("SKUS","OPPO-A1K,OPPO-RENO10,OPPO-ENCOBUDS2").split(",")
promoter=os.environ.get("PROMOTER","pavlov")
today=datetime.date.today()
out=[]
for d in range(days):
    day=(today - datetime.timedelta(days=d)).isoformat()
    for i in range(per_day):
        out.append({
            "store_code": random.choice(stores),
            "sku_code": random.choice(skus),
            "qty": random.randint(1,3),
            "sold_at": day,
            "promoter": promoter
        })
print(json.dumps(out))
PY
)

# Try bulk endpoint
bulk_code=$(http_code -H "Content-Type: application/json" -H "$AUTHZ" -X POST "${BASE_URL}/api/v1/sales/bulk" -d "$payload")
echo "POST /api/v1/sales/bulk -> [$bulk_code]"
if [ "$bulk_code" = "200" ] || [ "$bulk_code" = "201" ]; then
  echo "[OK] bulk inserted"
  exit 0
fi

# Fallback: per-item post to variants
targets=( "/api/v1/sales" "/api/v1/sales/promoter" "/api/v1/sales/network" )
count=0
for item in $(echo "$payload" | py -c "import sys,json;d=json.load(sys.stdin);import base64; print('\n'.join(base64.b64encode(json.dumps(x).encode()).decode() for x in d))"); do
  json_item=$(python3 - <<'PY' "$item"
import sys, json, base64
print(base64.b64decode(sys.argv[1]).decode())
PY
)
  posted=0
  for t in "${targets[@]}"; do
    code=$(http_code -H "Content-Type: application/json" -H "$AUTHZ" -X POST "${BASE_URL}${t}" -d "$json_item")
    if [ "$code" = "200" ] || [ "$code" = "201" ]; then
      posted=1; break
    fi
  done
  if [ "$posted" -eq 1 ]; then
    count=$((count+1))
  fi
done
echo "[OK] inserted $count sales (fallback mode)"
