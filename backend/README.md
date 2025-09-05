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

## Feature flags

| Flag | Default | Description |
|------|---------|-------------|
| `ENABLE_BONUSES`   | `false` | демо-роут бонусов |
| `ENABLE_MESSAGES`  | `false` | модуль сообщений |
| `ENABLE_IMPORTS`   | `false` | загрузки файлов |
| `ENABLE_ANALYTICS` | `false` | аналитические отчёты |

### Render

Добавьте флаги в Render Dashboard:

```env
ENABLE_BONUSES=true
ENABLE_MESSAGES=false
ENABLE_IMPORTS=false
ENABLE_ANALYTICS=false
```

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
