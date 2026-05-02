module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  # TODO: Add a separate API Lambda for accepting HTTP job requests.
  # This worker Lambda should stay focused on consuming SQS messages.
  #
  # Suggested flow:
  #   API Gateway -> API Lambda -> SQS -> this worker Lambda
  #
  # The API Lambda should:
  #   - expose a handler such as app.api.jobs.lambda_handler
  #   - validate and authenticate incoming requests
  #   - send messages to module.jobs_queue.queue_url
  #   - return 202 Accepted after enqueueing the job
  #   - avoid doing long-running AI processing directly in the request path
  #
  # Terraform pieces to add later:
  #   - module "api_lambda" with sqs:SendMessage permission
  #   - aws_apigatewayv2_api using protocol_type = "HTTP"
  #   - aws_apigatewayv2_integration using AWS_PROXY to the API Lambda
  #   - aws_apigatewayv2_route for POST /jobs
  #   - aws_apigatewayv2_stage, likely "$default" with auto_deploy = true
  #   - aws_lambda_permission allowing API Gateway to invoke the API Lambda
  #   - optional auth, throttling, CORS, and job-status routes
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

    secrets_read = {
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
      ]
      resources = [
        aws_secretsmanager_secret.openai_api_key.arn,
        module.db.db_instance_master_user_secret_arn,
      ]
    }

    vpc_network_interface_access = {
      effect = "Allow"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeSubnets",
        "ec2:AssignPrivateIpAddresses",
        "ec2:UnassignPrivateIpAddresses",
      ]
      resources = ["*"]
    }
  }

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.lambda.id]

  environment_variables = {
    OPENAI_API_KEY_SECRET_ARN = aws_secretsmanager_secret.openai_api_key.arn
    DB_SECRET_ARN             = module.db.db_instance_master_user_secret_arn
    DB_HOST                   = module.db.db_instance_address
    DB_NAME                   = var.db_name
    DB_PORT                   = "5432"
  }

  tags = local.tags
}
