locals {
  hourly_jobs = ["sales", "pops", "anomalies"]
  nightly_jobs = ["plan_vs_fact", "seasonality", "bonus_liability"]
}

resource "aws_iam_role" "eventbridge_invoke" {
  name = "${var.project}-${var.environment}-eventbridge"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = local.tags
}

resource "aws_iam_role_policy" "eventbridge_invoke" {
  role = aws_iam_role.eventbridge_invoke.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ecs:RunTask"
      Resource = aws_ecs_task_definition.backend.arn
      Condition = {
        ArnEquals = {
          "ecs:cluster" = aws_ecs_cluster.this.arn
        }
      }
    }, {
      Effect   = "Allow"
      Action   = ["iam:PassRole"]
      Resource = [aws_iam_role.ecs_task_execution_role.arn, aws_iam_role.ecs_task_role.arn]
    }]
  })
}

resource "aws_cloudwatch_log_group" "scheduled_tasks" {
  name              = "/aws/events/${var.project}-${var.environment}-scheduled"
  retention_in_days = var.log_retention_days
  tags              = local.tags
}

resource "aws_cloudwatch_event_rule" "hourly" {
  name                = "${var.project}-${var.environment}-hourly"
  description         = "Ежечасные задания"
  schedule_expression = "cron(0 * * * ? *)"
  tags                = local.tags
}

resource "aws_cloudwatch_event_rule" "nightly" {
  name                = "${var.project}-${var.environment}-nightly"
  description         = "Ночные задания"
  schedule_expression = "cron(0 2 * * ? *)"
  tags                = local.tags
}

resource "aws_cloudwatch_event_target" "hourly" {
  for_each = toset(local.hourly_jobs)

  rule      = aws_cloudwatch_event_rule.hourly.name
  target_id = each.key
  arn       = aws_ecs_cluster.this.arn
  role_arn  = aws_iam_role.eventbridge_invoke.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.backend.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = [for s in aws_subnet.private : s.id]
      security_groups = [aws_security_group.ecs.id]
    }
    platform_version = "1.4.0"
    task_count       = 1
    propagate_tags   = "TASK_DEFINITION"
  }

  input = jsonencode({
    detail-type = "scheduled-task"
    source      = "eventbridge"
    job         = each.key
  })
}

resource "aws_cloudwatch_event_target" "nightly" {
  for_each = toset(local.nightly_jobs)

  rule      = aws_cloudwatch_event_rule.nightly.name
  target_id = each.key
  arn       = aws_ecs_cluster.this.arn
  role_arn  = aws_iam_role.eventbridge_invoke.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.backend.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets         = [for s in aws_subnet.private : s.id]
      security_groups = [aws_security_group.ecs.id]
    }
    platform_version = "1.4.0"
    task_count       = 1
    propagate_tags   = "TASK_DEFINITION"
  }

  input = jsonencode({
    detail-type = "scheduled-task"
    source      = "eventbridge"
    job         = each.key
  })
}
