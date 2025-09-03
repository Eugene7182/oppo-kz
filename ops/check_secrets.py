# ops/check_secrets.py
import os, sys

# Check for required environment variables with fallbacks
api_key = os.getenv("RENDER_API_KEY")
# Service ID can come from backend, staging, or production
service_id = os.getenv("RENDER_BACKEND_SERVICE_ID") or os.getenv("RENDER_STAGING_SERVICE_ID") or os.getenv("RENDER_PRODUCTION_SERVICE_ID")
# Base URL can come from generic, staging, or production
app_base = os.getenv("APP_BASE_URL") or os.getenv("STAGING_APP_BASE_URL") or os.getenv("PROD_APP_BASE_URL")

missing = []
if not api_key:
    missing.append("RENDER_API_KEY")
if not service_id:
    missing.append("SERVICE_ID (RENDER_*_SERVICE_ID)")
if not app_base:
    missing.append("APP_BASE_URL (or STAGING_APP_BASE_URL/PROD_APP_BASE_URL)")

if missing:
    print("\u274c Missing secrets/env for workflow:", ", ".join(missing), file=sys.stderr)
    sys.exit(1)

print("\u2705 Secrets/vars OK: RENDER_API_KEY, SERVICE_ID, APP_BASE_URL")
