# TODO: Add RDS PostgreSQL.

# resource "aws_db_subnet_group" "this" {
#   name       = "${local.name_prefix}-db"
#   subnet_ids = []
# }
#
# resource "aws_db_instance" "postgres" {
#   identifier             = "${local.name_prefix}-postgres"
#   engine                 = "postgres"
#   engine_version         = "16"
#   instance_class         = var.db_instance_class
#   allocated_storage      = 20
#   db_name                = var.db_name
#   username               = var.db_username
#   password               = ""
#   db_subnet_group_name   = aws_db_subnet_group.this.name
#   vpc_security_group_ids = [aws_security_group.rds.id]
#   publicly_accessible    = false
#   skip_final_snapshot    = true
# }
