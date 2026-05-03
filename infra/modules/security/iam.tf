# TODO: Add Lambda IAM role and policies.

# resource "aws_iam_role" "lambda_worker" {
#   name = "${local.name_prefix}-lambda-worker"
#
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       }
#       Action = "sts:AssumeRole"
#     }]
#   })
# }
