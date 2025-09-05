#!/usr/bin/env bash
set -euo pipefail
# Wipes ONLY demo data created by seed scripts (safe by default).
# DRY_RUN=true by default; set CONFIRM=YES to actually delete or DRY_RUN=false.
#
# Usage:
#   BASE_URL=http://localhost:8000 ADMIN_USER=admin@oppo.kz ADMIN_PASS=StrongPass123 ./infra/scripts/wipe_demo.sh
#   CONFIRM=YES ./infra/scripts/wipe_demo.sh   # actually delete
#
BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"
DRY_RUN="${DRY_RUN:-true}"
CONFIRM="${CONFIRM:-NO}"

py() { python3 - "$@"; }
http_code() { curl -s -o /dev/null -w "%{http_code}" "$@"; }
jget()  { curl -sS -H "$AUTHZ" -X GET "$@"; }
jdel()  { curl -sS -H "$AUTHZ" -X DELETE "$@"; }

echo "=== WIPE DEMO @ ${BASE_URL} (DRY_RUN=${DRY_RUN} CONFIRM=${CONFIRM}) ==="

# Auth
TOKEN=$(curl -sS -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=${ADMIN_USER}&password=${ADMIN_PASS}" \
  | py -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") || true
[ -n "$TOKEN" ] || { echo "[FAIL] admin login"; exit 1; }
AUTHZ="Authorization: Bearer ${TOKEN}"
echo "[OK] admin login"

# Helpers
probe_get() { # returns first path with 200
  local -n arr=$1
  for p in "${arr[@]}"; do
    local code; code=$(http_code -H "$AUTHZ" "${BASE_URL}${p}")
    if [ "$code" = "200" ]; then echo "$p"; return 0; fi
  done
  echo ""
  return 1
}
confirm_or_echo() {
  if [ "$DRY_RUN" = "false" ] && [ "$CONFIRM" = "YES" ]; then
    eval "$@"
  else
    echo "[DRY] $*"
  fi
}

# 1) Sales (created by seeds) ------------------------------
sales_get_candidates=( "/api/v1/sales" "/api/v1/sales/promoter" "/api/v1/sales/network" )
sales_del_template="" # we will infer from GET path -> /{id}
sales_path=$(probe_get sales_get_candidates) || true
if [ -n "$sales_path" ]; then
  echo "[INFO] sales GET path: $sales_path"
  data=$(jget "${BASE_URL}${sales_path}")
  # filter OPPO-* SKUs and promoter pavlov
  ids=$(echo "$data" | py - <<'PY'
import sys, json
try:
    d = json.load(sys.stdin)
    out = []
    if isinstance(d, list):
        for x in d:
            sku = (x.get("sku") or x.get("sku_code") or "") or ""
            prom = (x.get("promoter") or x.get("promoter_username") or "") or ""
            if isinstance(sku, dict): sku = sku.get("code","")
            if str(sku).startswith("OPPO-") or prom=="pavlov":
                if "id" in x: out.append(str(x["id"]))
    print(",".join(out))
except Exception as e:
    print("")
PY
)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${sales_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  else
    echo "[INFO] no demo sales found"
  fi
else
  echo "[INFO] sales endpoint not found"
fi

# 2) Shipments / In-Transit --------------------------------
ship_get_candidates=( "/api/v1/stock/shipments" "/api/v1/shipments" )
ship_path=$(probe_get ship_get_candidates) || true
if [ -n "$ship_path" ]; then
  ids=$(jget "${BASE_URL}${ship_path}" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(str(x.get('id')) for x in d if isinstance(d,list)))" 2>/dev/null || true)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${ship_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi
intransit_get_candidates=( "/api/v1/stock/in-transit" "/api/v1/in-transit" )
in_path=$(probe_get intransit_get_candidates) || true
if [ -n "$in_path" ]; then
  ids=$(jget "${BASE_URL}${in_path}" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(str(x.get('id')) for x in d if isinstance(d,list)))" 2>/dev/null || true)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${in_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

# 3) Price List --------------------------------------------
pricelist_get_candidates=( "/api/v1/price-list" "/api/v1/pricelist" "/api/v1/sku/price-list" )
pl_path=$(probe_get pricelist_get_candidates) || true
if [ -n "$pl_path" ]; then
  ids=$(jget "${BASE_URL}${pl_path}" | py - <<'PY'
import sys, json
try:
    d = json.load(sys.stdin)
    out = []
    if isinstance(d, list):
        for x in d:
            sku = (x.get("sku_code") or x.get("sku") or "")
            if isinstance(sku, dict): sku = sku.get("code","")
            if str(sku).startswith("OPPO-"):
                if "id" in x: out.append(str(x["id"]))
    print(",".join(out))
except Exception:
    print("")
PY
)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${pl_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

# 4) Stock balances (skip; часто нет DELETE) ----------------

# 5) Bonus Grid ---------------------------------------------
bonus_get_candidates=( "/api/v1/bonus-grid" "/api/v1/bonus" "/api/v1/payouts" )
bonus_path=$(probe_get bonus_get_candidates) || true
if [ -n "$bonus_path" ]; then
  ids=$(jget "${BASE_URL}${bonus_path}" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(str(x.get('id')) for x in d if isinstance(d,list)))" 2>/dev/null || true)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${bonus_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

# 6) Store Coefficients -------------------------------------
coeff_path="/api/v1/store-coefficients"
if [ "$(http_code -H "$AUTHZ" "${BASE_URL}${coeff_path}")" = "200" ]; then
  ids=$(jget "${BASE_URL}${coeff_path}" | py -c "import sys,json;d=json.load(sys.stdin);print(','.join(str(x.get('id')) for x in d if isinstance(d,list)))")
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${coeff_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

# 7) SKUs (only OPPO-* demo) --------------------------------
skus_get_candidates=( "/api/v1/skus" "/api/v1/sku" "/api/v1/products" "/api/v1/items" )
skus_path=$(probe_get skus_get_candidates) || true
if [ -n "$skus_path" ]; then
  ids=$(jget "${BASE_URL}${skus_path}" | py - <<'PY'
import sys, json
try:
    d = json.load(sys.stdin)
    out = []
    if isinstance(d, list):
        for x in d:
            code = x.get("code") or x.get("sku_code") or ""
            if str(code).startswith("OPPO-") and "id" in x:
                out.append(str(x["id"]))
    print(",".join(out))
except Exception:
    print("")
PY
)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${skus_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

# 8) Stores (only demo codes) --------------------------------
store_codes=("WH1" "A01" "A02" "N01")
stores_get_candidates=( "/api/v1/stores" "/api/v1/dict/stores" "/api/v1/reference/stores" )
stores_path=$(probe_get stores_get_candidates) || true
if [ -n "$stores_path" ]; then
  data=$(jget "${BASE_URL}${stores_path}")
  ids=$(echo "$data" | py - <<'PY'
import sys, json, os
try:
    demo = set(os.environ.get("DEMO_STORES","WH1,A01,A02,N01").split(","))
    d = json.load(sys.stdin)
    out = []
    if isinstance(d, list):
        for x in d:
            code = x.get("code") or x.get("store_code") or ""
            if code in demo and "id" in x:
                out.append(str(x["id"]))
    print(",".join(out))
except Exception:
    print("")
PY
)
  if [ -n "$ids" ]; then
    IFS=',' read -r -a arr <<< "$ids"
    for id in "${arr[@]}"; do
      del_url="${BASE_URL}${stores_path}/${id}"
      echo "DELETE $del_url"
      confirm_or_echo jdel "$del_url" >/dev/null || true
    done
  fi
fi

echo "=== WIPE DEMO: DONE ==="
