variable "project" {
  description = "Имя проекта для тегирования ресурсов"
  type        = string
}

variable "environment" {
  description = "Имя окружения (prod/staging и т.д.)"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS регион для основного провайдера"
  type        = string
  default     = "me-central-1"
}

variable "vpc_cidr" {
  description = "CIDR блок для VPC"
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Список CIDR блоков для публичных подсетей"
  type        = list(string)
  default     = [
    "10.42.0.0/24",
    "10.42.1.0/24"
  ]
}

variable "private_subnet_cidrs" {
  description = "Список CIDR блоков для приватных подсетей"
  type        = list(string)
  default     = [
    "10.42.10.0/24",
    "10.42.11.0/24"
  ]
}

variable "database_subnet_cidrs" {
  description = "CIDR блоки для выделенных подсетей БД"
  type        = list(string)
  default     = [
    "10.42.20.0/24",
    "10.42.21.0/24"
  ]
}

variable "domain_name" {
  description = "Полный домен фронтенда"
  type        = string
  default     = "app.oppo-kz.kz"
}

variable "hosted_zone_id" {
  description = "ID существующей Route53 hosted zone"
  type        = string
}

variable "container_image" {
  description = "Docker образ backend"
  type        = string
}

variable "container_port" {
  description = "Порт контейнера backend"
  type        = number
  default     = 8080
}

variable "desired_count" {
  description = "Желаемое количество задач ECS"
  type        = number
  default     = 2
}

variable "sentry_backend_dsn" {
  description = "Sentry DSN для backend"
  type        = string
  sensitive   = true
}

variable "sentry_frontend_dsn" {
  description = "Sentry DSN для frontend"
  type        = string
  sensitive   = true
}

variable "allowed_cidr_ingress" {
  description = "Список CIDR для доступа к ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "db_username" {
  description = "Имя пользователя Postgres"
  type        = string
}

variable "db_password" {
  description = "Пароль Postgres"
  type        = string
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Размер хранилища RDS в ГБ"
  type        = number
  default     = 100
}

variable "db_instance_class" {
  description = "Тип инстанса БД"
  type        = string
  default     = "db.m6gd.large"
}

variable "log_retention_days" {
  description = "Срок хранения логов CloudWatch"
  type        = number
  default     = 30
}

variable "cpu_target_utilization" {
  description = "Целевой уровень CPU для автоскейлинга"
  type        = number
  default     = 60
}

variable "latency_target_ms" {
  description = "Порог P90 latency в мс для автоскейлинга"
  type        = number
  default     = 500
}

variable "container_cpu" {
  description = "CPU для задачи Fargate"
  type        = number
  default     = 1024
}

variable "container_memory" {
  description = "Память для задачи Fargate"
  type        = number
  default     = 2048
}

variable "feature_flags" {
  description = "Карта feature-флагов для backend"
  type        = map(string)
  default     = {
    FEATURE_AI_INSIGHTS = "false"
  }
}

variable "openai_api_key_ssm_param" {
  description = "Имя параметра SSM для OPENAI_API_KEY"
  type        = string
  default     = "/oppo-kz/prod/openai_api_key"
}
