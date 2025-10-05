#!/usr/bin/env bash
set -euo pipefail

# Скрипт подготовки AWS ресурсов до запуска Terraform/CI
# Требует установленный aws cli и авторизацию с правами администратора.

PROJECT="oppo-kz"
ENVIRONMENT="prod"
REGION="me-central-1"
ACM_REGION="us-east-1"

if ! command -v aws >/dev/null 2>&1; then
  echo "aws cli не найден" >&2
  exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Создание ECR репозитория (если нет)
REPO_NAME="${PROJECT}/${ENVIRONMENT}/backend"
if ! aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" >/dev/null 2>&1; then
  aws ecr create-repository \
    --repository-name "$REPO_NAME" \
    --image-scanning-configuration scanOnPush=true \
    --region "$REGION"
  echo "Создан репозиторий ECR: $REPO_NAME"
else
  echo "ECR репозиторий уже существует: $REPO_NAME"
fi

# S3 для CI артефактов (опционально)
ARTIFACT_BUCKET="${PROJECT}-${ENVIRONMENT}-artifacts"
if ! aws s3api head-bucket --bucket "$ARTIFACT_BUCKET" >/dev/null 2>&1; then
  aws s3api create-bucket --bucket "$ARTIFACT_BUCKET" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"
  aws s3api put-bucket-versioning --bucket "$ARTIFACT_BUCKET" --versioning-configuration Status=Enabled
  echo "Создан бакет для артефактов: s3://$ARTIFACT_BUCKET"
fi

# Предварительный запрос ACM сертификата (в us-east-1 для CloudFront)
CERT_ARN=$(aws acm list-certificates --region "$ACM_REGION" --query "CertificateSummaryList[?DomainName=='app.oppo-kz.kz'].CertificateArn" --output text)
if [ -z "$CERT_ARN" ] || [ "$CERT_ARN" = "None" ]; then
  CERT_ARN=$(aws acm request-certificate \
    --region "$ACM_REGION" \
    --domain-name "app.oppo-kz.kz" \
    --validation-method DNS \
    --idempotency-token "${PROJECT}${ENVIRONMENT}" \
    --query CertificateArn --output text)
  echo "Запрошен ACM сертификат: $CERT_ARN"
else
  echo "Найден существующий сертификат: $CERT_ARN"
fi

echo "Проверьте Route53 и добавьте записи CNAME для валидации сертификата."

echo "Bootstrap завершён. Далее: terraform init/plan/apply в infra/aws/prod"
