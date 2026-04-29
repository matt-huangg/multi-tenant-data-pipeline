# TODO: Add Lambda and RDS security groups.

# resource "aws_security_group" "lambda" {
#   name        = "${local.name_prefix}-lambda"
#   description = "Lambda worker security group"
#   vpc_id      = aws_vpc.this.id
# }
#
# resource "aws_security_group" "rds" {
#   name        = "${local.name_prefix}-rds"
#   description = "RDS PostgreSQL security group"
#   vpc_id      = aws_vpc.this.id
# }
