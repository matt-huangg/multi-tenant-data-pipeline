module "api_gateway_v2_lambda_http" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 5.0"

  name        = "${local.name_prefix}-http"
  description = "HTTP API for the AI content processor"

  create_domain_name    = false
  create_domain_records = false
  create_certificate    = false

  cors_configuration = {
    allow_headers = ["content-type"]
    allow_methods = ["*"]
    allow_origins = ["*"]
  }

  stage_access_log_settings = {
    create_log_group            = true
    log_group_retention_in_days = 7
    format = jsonencode({
      requestId               = "$context.requestId"
      requestTime             = "$context.requestTime"
      httpMethod              = "$context.httpMethod"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      protocol                = "$context.protocol"
      responseLength          = "$context.responseLength"
      sourceIp                = "$context.identity.sourceIp"
      errorMessage            = "$context.error.message"
      integrationErrorMessage = "$context.integrationErrorMessage"
    })
  }

  # Routes & Integration(s)
  routes = {
    "POST /" = {
      integration = {
        uri                    = module.lambda_function_http.lambda_function_arn
        payload_format_version = "2.0"
        timeout_milliseconds   = 12000
      }
    }
  }

  tags = local.tags
}
