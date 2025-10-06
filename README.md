# OPPO KZ Data Platform

Платформа данных по продажам и остаткам OPPO Казахстан.

## Структура проекта
```
backend/
  app/
    api/ core/ db/ models/ schemas/ services/ feature_flags/
  alembic.ini
  migrations/
frontend/
  src/
    app/ shared/ entities/ features/ pages/ widgets/
  .env.example
infra/
  render.yaml
  render.md
  scripts/
  aws/
    README.md
    prod/
.env.example
```

## Инвентаризация
| From | To | Scope |
|---|---|---|
| `scripts/` | `infra/scripts/` | infra |
| `render.yaml` | `infra/render.yaml` | infra |
| `backend/alembic/` | `backend/migrations/` | backend |
| `backend/app/core/feature_flags.py` | `backend/app/feature_flags/__init__.py` | backend |
| `frontend/src/App.tsx` | `frontend/src/app/App.tsx` | frontend |
| `frontend/src/main.tsx` | `frontend/src/app/main.tsx` | frontend |
| `frontend/src/routes.tsx` | `frontend/src/app/routes.tsx` | frontend |
| `frontend/src/styles/` | `frontend/src/app/styles/` | frontend |
| `frontend/src/context/` | `frontend/src/shared/context/` | frontend |
| `frontend/src/lib/http.ts` | `frontend/src/shared/api/http.ts` | frontend |
| `frontend/src/lib/toast.tsx` | `frontend/src/shared/ui/toast.tsx` | frontend |
| `frontend/src/components/` | `frontend/src/widgets/` | frontend |

## Render
- **Backend start**: `export PYTHONPATH="$(pwd)" && alembic -c alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Frontend build**: `npm ci --include=dev && npm run build`

## ENV
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `VITE_API_URL`
- дополнительные переменные для продакшена описаны в `infra/ENV.md`

## Инфраструктура
- **Staging** — Render (см. `infra/render.md`, `render.yaml`). Автодеплой из ветки `develop` через GitHub Actions `frontend-ci`/`deploy_render` и backend веб-сервис Render.
- **Production** — AWS (Terraform в `infra/aws/prod`). Bootstrap-скрипт: `scripts/bootstrap_aws_infra.sh`.

## Запуск локально
```bash
# Backend
cd backend && uvicorn app.main:app

# Frontend
cd frontend && npm install && npm run dev
```

## Демо-сиды
```bash
PYTHONPATH=backend python backend/scripts/seed_demo_data.py --purge
```

- сиды создают регионы, сети, магазины, пользователей всех ролей, планы, продажи, бонусные схемы и закрытый период на август 2024.
- исходные данные описаны в `ops/demo/demo_data.json`.

## E2E (Playwright)

```bash
# Требуется запущенный backend с доступом к API (по умолчанию http://localhost:8000/api/v1)
API_BASE_URL=http://localhost:8000/api/v1 npm run test:e2e
```

- глобальный setup автоматически пересоздаёт demo-данные через `backend/scripts/seed_demo_data.py`.
- сценарии живут в `e2e/tests/scenarios.spec.ts`.
