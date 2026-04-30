module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  function_name = "${local.name_prefix}-worker"
  description   = "Processes queued AI content jobs from SQS"
  handler       = "app.workers.sqs_worker.lambda_handler"
  runtime       = "python3.13"
  source_path   = "../build/lambda-src"

  event_source_mapping = {
    jobs_queue = {
      event_source_arn        = module.jobs_queue.queue_arn
      batch_size              = 1
      function_response_types = ["ReportBatchItemFailures"]
    }
  }

  attach_policy_statements = true
  policy_statements = {
    jobs_queue_consume = {
      effect = "Allow"
      actions = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:ChangeMessageVisibility",
      ]
      resources = [module.jobs_queue.queue_arn]
    }
  }

  tags = local.tags
}
