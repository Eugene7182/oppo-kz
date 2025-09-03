# ops/check_secrets.py
import os, sys
required = ["RENDER_API_KEY", "RENDER_BACKEND_SERVICE_ID", "APP_BASE_URL"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print("❌ Missing secrets/env for workflow:", ", ".join(missing), file=sys.stderr)
    sys.exit(1)
print("✅ Secrets OK:", ", ".join(required))
