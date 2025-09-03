#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USER:-admin@oppo.kz}"
ADMIN_PASS="${ADMIN_PASS:-StrongPass123}"

echo "Health..."
curl -fsSL "$BASE_URL/api/v1/health" | jq .

echo "Version..."
curl -fsSL "$BASE_URL/api/v1/version" | jq .

echo "Login (admin)..."
TOK=$(curl -fsSL -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\"}" | jq -r '.access_token // .token // .access')
test -n "$TOK"
echo "Token ok: ${#TOK} chars"

echo "Invites list..."
curl -fsSL -H "Authorization: Bearer $TOK" "$BASE_URL/api/v1/invites?only_active=true" | jq .
echo "OK"
