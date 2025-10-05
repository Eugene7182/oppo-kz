resource "aws_secretsmanager_secret" "db_password" {
  name = "/${var.project}/${var.environment}/db_password"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

resource "aws_secretsmanager_secret" "sentry_backend" {
  name = "/${var.project}/${var.environment}/sentry_backend_dsn"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "sentry_backend" {
  secret_id     = aws_secretsmanager_secret.sentry_backend.id
  secret_string = var.sentry_backend_dsn
}

resource "aws_secretsmanager_secret" "sentry_frontend" {
  name = "/${var.project}/${var.environment}/sentry_frontend_dsn"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "sentry_frontend" {
  secret_id     = aws_secretsmanager_secret.sentry_frontend.id
  secret_string = var.sentry_frontend_dsn
}

resource "aws_secretsmanager_secret" "backend_env" {
  name = "/${var.project}/${var.environment}/backend_env"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "backend_env" {
  secret_id = aws_secretsmanager_secret.backend_env.id
  secret_string = jsonencode({
    SECRET_KEY           = "${var.project}-${var.environment}-secret"
    FEATURE_AI_INSIGHTS  = lookup(var.feature_flags, "FEATURE_AI_INSIGHTS", "false")
  })
}

resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.project}/${var.environment}/DATABASE_URL"
  description = "Подключение к Postgres"
  type        = "SecureString"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.project}"
  tags        = local.tags
}

resource "aws_ssm_parameter" "openai_api_key" {
  name        = var.openai_api_key_ssm_param
  description = "Опциональный ключ OpenAI"
  type        = "SecureString"
  value       = ""
  tags        = local.tags
}
