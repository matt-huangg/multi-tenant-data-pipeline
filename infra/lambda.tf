# TODO: Add Lambda worker and SQS trigger.

# resource "aws_lambda_function" "worker" {
#   function_name = "${local.name_prefix}-worker"
#   role          = aws_iam_role.lambda_worker.arn
#   runtime       = "python3.13"
#   handler       = "app.workers.sqs_worker.lambda_handler"
#   filename      = var.lambda_package_path
#   timeout       = 120
#   memory_size   = 512
#
#   vpc_config {
#     subnet_ids         = []
#     security_group_ids = [aws_security_group.lambda.id]
#   }
# }
#
# resource "aws_lambda_event_source_mapping" "jobs" {
#   event_source_arn = aws_sqs_queue.jobs.arn
#   function_name    = aws_lambda_function.worker.arn
#   batch_size       = 5
# }
