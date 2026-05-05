output "name_prefix" {
  description = "Common resource name prefix."
  value       = local.name_prefix
}

output "api_endpoint" {
  description = "HTTP API invoke endpoint."
  value       = module.api_gateway_v2_lambda_http.api_endpoint
}

output "jobs_queue_url" {
  description = "SQS jobs queue URL."
  value       = module.jobs_queue.queue_url
}

output "openai_api_key_secret_arn" {
  description = "Secrets Manager secret ARN for the OpenAI API key."
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint."
  value       = module.db.db_instance_endpoint
}
