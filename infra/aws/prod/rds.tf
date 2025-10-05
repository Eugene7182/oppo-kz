resource "aws_db_instance" "postgres" {
  identifier              = "${var.project}-${var.environment}-pg"
  engine                  = "postgres"
  engine_version          = "15.4"
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  storage_type            = "gp3"
  multi_az                = true
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  username                = var.db_username
  password                = var.db_password
  backup_retention_period = 14
  delete_automated_backups = true
  maintenance_window      = "Sun:00:00-Sun:03:00"
  backup_window           = "03:00-06:00"
  auto_minor_version_upgrade = true
  publicly_accessible     = false
  storage_encrypted       = true
  deletion_protection     = true

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-pg" })
}
