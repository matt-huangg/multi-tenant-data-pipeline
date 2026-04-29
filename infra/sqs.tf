# TODO: Add SQS queue and DLQ.

# resource "aws_sqs_queue" "jobs_dlq" {
#   name = "${local.name_prefix}-jobs-dlq"
# }
#
# resource "aws_sqs_queue" "jobs" {
#   name                       = "${local.name_prefix}-jobs"
#   visibility_timeout_seconds = 180
#   redrive_policy             = jsonencode({
#     deadLetterTargetArn = aws_sqs_queue.jobs_dlq.arn
#     maxReceiveCount     = 3
#   })
# }
