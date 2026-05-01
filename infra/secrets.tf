resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${local.name_prefix}/openai-api-key"
  description             = "OpenAI API key for the Lambda worker"
  recovery_window_in_days = 30

  tags = local.tags
}
