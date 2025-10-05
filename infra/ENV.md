# Переменные окружения

## Backend (FastAPI)
| Variable | Назначение | Где хранить |
|----------|------------|-------------|
| `DATABASE_URL` | Подключение к Postgres | AWS SSM Parameter Store `/oppo-kz/prod/DATABASE_URL`, Render secret для стейджинга |
| `SECRET_KEY` | Секрет JWT/шифрования | AWS Secrets Manager `/oppo-kz/prod/backend_env`, Render secret |
| `CORS_ORIGINS` | Разрешённые источники | AWS Secrets Manager `/oppo-kz/prod/backend_env`, Render environment |
| `S3_BUCKET` | Рабочий бакет для файлов | AWS Secrets Manager `/oppo-kz/prod/backend_env` |
| `AWS_REGION` | Регион AWS | AWS Secrets Manager `/oppo-kz/prod/backend_env` |
| `SENTRY_DSN` | DSN для Sentry backend | AWS Secrets Manager `/oppo-kz/prod/sentry_backend_dsn`, Render secret |
| `FEATURE_AI_INSIGHTS` | Фичефлаг AI аналитики | AWS Secrets Manager `/oppo-kz/prod/backend_env`, Render env |
| `OPENAI_API_KEY` | Опциональный ключ OpenAI | AWS SSM Parameter `/oppo-kz/prod/openai_api_key`, Render secret |

## Frontend (Vite)
| Variable | Назначение | Где хранить |
|----------|------------|-------------|
| `VITE_API_URL` | Базовый URL API | Render static site env (`https://<staging-backend>`), S3 build-time переменная через GitHub Actions | 

## Порядок обновления секретов
1. Обновите секреты в AWS Secrets Manager/SSM CLI или через консоль.
2. В GitHub → Settings → Secrets and variables → Actions добавьте:
   - `AWS_IAM_ROLE_TO_ASSUME`, `AWS_ECS_CLUSTER_NAME`, `AWS_ECS_SERVICE_NAME`, `AWS_ECS_SUBNETS`, `AWS_ECS_SECURITY_GROUPS`, `AWS_FRONTEND_BUCKET`, `AWS_CLOUDFRONT_DISTRIBUTION_ID`.
   - Render API ключи: `RENDER_API_KEY`, `RENDER_BACKEND_SERVICE_ID`, `RENDER_STATIC_SITE_ID`.
3. Для стейджинга (Render) используйте `render.yaml` и панель Render для установки `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, `VITE_API_URL`.

## Домены
- **Production frontend**: `app.oppo-kz.kz` → CloudFront (Terraform создаёт alias запись).
- **Production API**: ALB DNS `oppo-kz-prod-alb-*.amazonaws.com` или пользовательский поддомен `api.oppo-kz.kz` (создать CNAME/ALIAS в Route53).
- **Staging**: Render выдаёт свои URL вида `https://oppo-kz-staging.onrender.com`. Пропишите их в `CORS_ORIGINS` и `VITE_API_URL`.
