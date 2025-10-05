output "frontend_bucket" {
  description = "Имя S3 бакета для фронтенда"
  value       = aws_s3_bucket.frontend.bucket
}

output "files_bucket" {
  description = "S3 бакет для загружаемых файлов"
  value       = aws_s3_bucket.files.bucket
}

output "cloudfront_domain" {
  description = "Домен CloudFront"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "alb_dns_name" {
  description = "DNS ALB"
  value       = aws_lb.this.dns_name
}

output "rds_endpoint" {
  description = "Endpoint базы данных"
  value       = aws_db_instance.postgres.address
}

output "ecs_cluster_name" {
  description = "Имя ECS кластера"
  value       = aws_ecs_cluster.this.name
}

output "ecr_repository_url" {
  description = "URL ECR репозитория"
  value       = aws_ecr_repository.backend.repository_url
}
