# Backend

## Render ENV

- DATABASE_URL
- SECRET_KEY
- ALGORITHM
- ACCESS_TOKEN_EXPIRES_MIN
- REFRESH_TOKEN_EXPIRES_DAYS
- ADMIN_EMAIL
- ADMIN_PASSWORD
- ADMIN_NAME

## Admin seed

Create superuser from ENV:

```bash
python -m app.services.user_service --ensure-admin
```

## Smoke

Run the API smoke check once the server is running.

### Bash

```bash
python scripts/smoke_check.py
```

### PowerShell

```powershell
python .\scripts\smoke_check.py
```
