#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"
curl -sS -X POST "${BASE_URL}/api/v1/auth/login"   -H "Content-Type: application/x-www-form-urlencoded"   --data "username=${ADMIN_USER}&password=${ADMIN_PASS}"
