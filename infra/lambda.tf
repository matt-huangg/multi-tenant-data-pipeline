locals {
  lambda_runtime     = "python3.13"
  lambda_source_path = "../build/lambda-src"

  lambda_common_environment_variables = {
    DB_SECRET_ARN = module.db.db_instance_master_user_secret_arn
    DB_HOST       = module.db.db_instance_address
    DB_NAME       = var.db_name
    DB_PORT       = "5432"
    SQS_QUEUE_URL = module.jobs_queue.queue_url
  }

  lambda_db_secret_arns = [module.db.db_instance_master_user_secret_arn]

  lambda_common_policy_statements = {
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
}

module "lambda_function_worker" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  function_name                     = "${local.name_prefix}-worker"
  description                       = "Processes queued AI content jobs from SQS"
  handler                           = "app.workers.sqs_worker.lambda_handler"
  runtime                           = local.lambda_runtime
  source_path                       = local.lambda_source_path
  cloudwatch_logs_retention_in_days = 14

  event_source_mapping = {
    jobs_queue = {
      event_source_arn        = module.jobs_queue.queue_arn
      batch_size              = 1
      function_response_types = ["ReportBatchItemFailures"]
    }
  }

  attach_policy_statements = true
  policy_statements = merge(local.lambda_common_policy_statements, {
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
      resources = concat(
        [aws_secretsmanager_secret.openai_api_key.arn],
        local.lambda_db_secret_arns,
      )
    }
  })

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.lambda.id]

  environment_variables = merge(local.lambda_common_environment_variables, {
    OPENAI_API_KEY_SECRET_ARN = aws_secretsmanager_secret.openai_api_key.arn
  })

  tags = local.tags
}

module "lambda_function_http" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "~> 7.0"
  function_name = "${local.name_prefix}-http"

  description = "Serves the AI content processor HTTP API"

  handler                           = "app.lambda_http.lambda_handler"
  runtime                           = local.lambda_runtime
  source_path                       = local.lambda_source_path
  cloudwatch_logs_retention_in_days = 14

  attach_policy_statements = true
  policy_statements = merge(local.lambda_common_policy_statements, {
    jobs_queue_send = {
      effect = "Allow"
      actions = [
        "sqs:SendMessage",
      ]
      resources = [module.jobs_queue.queue_arn]
    }

    secrets_read = {
      effect = "Allow"
      actions = [
        "secretsmanager:GetSecretValue",
      ]
      resources = local.lambda_db_secret_arns
    }
  })

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [aws_security_group.lambda.id]

  environment_variables = local.lambda_common_environment_variables

  # Allows API Gateway to invoke this Lambda. This creates Lambda resource
  # policy permissions, not execution-role permissions.
  allowed_triggers = {
    api_gateway = {
      principal  = "apigateway.amazonaws.com"
      source_arn = "${module.api_gateway_v2_lambda_http.api_execution_arn}/*/*/*"
    }
  }

  create_current_version_allowed_triggers = false

  tags = local.tags
}
