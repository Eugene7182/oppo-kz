resource "aws_cloudwatch_log_group" "ecs_backend" {
  name              = "/ecs/${local.backend_name}"
  retention_in_days = var.log_retention_days
  tags              = local.tags
}
