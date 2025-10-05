locals {
  tags = {
    Project     = var.project
    Environment = var.environment
  }

  backend_name = "${var.project}-${var.environment}-backend"
  frontend_id  = "${var.project}-${var.environment}-frontend"
  files_bucket = "${var.project}-${var.environment}-files"
}
