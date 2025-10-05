# AWS Prod инфраструктура

## Структура Terraform
- `infra/aws/prod/*.tf` — описание VPC, ECS Fargate, RDS, S3, CloudFront, WAF, EventBridge и секретов.
- Используются два провайдера AWS: основной (me-central-1) и алиас `us_east_1` для ACM/CloudFront.

## Шаги развёртывания
1. Выполнить `scripts/bootstrap_aws_infra.sh` для подготовки ECR и запроса сертификата ACM.
2. После подтверждения сертификата в Route53 перейти в каталог `infra/aws/prod` и выполнить:
   ```bash
   terraform init
   terraform workspace select prod || terraform workspace new prod
   terraform plan -var "project=oppo-kz" -var "container_image=<ACCOUNT_ID>.dkr.ecr.me-central-1.amazonaws.com/oppo-kz/prod/backend:latest" -var "db_username=oppo" -var "db_password=<secure>" -var "sentry_backend_dsn=<dsn>" -var "sentry_frontend_dsn=<dsn>" -var "hosted_zone_id=<ZID>"
   terraform apply
   ```
3. После создания CloudFront обновить запись A в внешнем DNS, если используется сторонний регистратор.

## Настройка домена
- В Route53 hosted zone `oppo-kz.kz` будет создана A-запись `app.oppo-kz.kz` (alias на CloudFront).
- Для backend использовать поддомен `api.oppo-kz.kz` (создать отдельно и направить на ALB, если потребуется публичный API). В противном случае — доступ только через ALB DNS.

## Переменные окружения и секреты
- Secrets Manager: `/oppo-kz/prod/backend_env`, `/oppo-kz/prod/db_password`, `/oppo-kz/prod/sentry_*`.
- Parameter Store: `/oppo-kz/prod/DATABASE_URL`, `/oppo-kz/prod/openai_api_key`.
- CI/CD workflows обращаются к этим секретам через IAM роли GitHub OIDC (см. `.github/workflows`).

## Мониторинг и логирование
- CloudWatch log groups: `/ecs/oppo-kz-prod-backend`, `/aws/events/oppo-kz-prod-scheduled`.
- Рекомендуется подключить Sentry DSN в Secrets Manager, чтобы ECS сервис пробросил переменные.

## Крон-задачи
- EventBridge запускает Fargate задачи с тегом `job` (sales/pops/anomalies каждую час; план-факт/seasonality/bonus_liability в 02:00 UTC).
- Backend должен обрабатывать входящий payload JSON с ключом `job`.
