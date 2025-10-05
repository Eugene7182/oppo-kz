resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project}-${var.environment}-ecs-execution"

  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.project}-${var.environment}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json

  tags = local.tags
}

resource "aws_iam_policy" "ecs_task_extra" {
  name        = "${var.project}-${var.environment}-ecs-task-extra"
  description = "Доступ к S3, Secrets Manager и Parameter Store"

  policy = data.aws_iam_policy_document.ecs_task_extra.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_extra" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_extra.arn
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "ecs_task_extra" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.files.arn}/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue", "ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = [
      aws_secretsmanager_secret.backend_env.arn,
      aws_secretsmanager_secret.db_password.arn,
      aws_secretsmanager_secret.sentry_backend.arn,
      aws_secretsmanager_secret.sentry_frontend.arn,
      aws_ssm_parameter.openai_api_key.arn,
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/oppo-kz/*"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${local.backend_name}:*"
    ]
  }
}

data "aws_caller_identity" "current" {}
