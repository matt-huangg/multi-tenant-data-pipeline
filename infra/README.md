# Infrastructure

Terraform scaffold for deploying the AI Content Processor AWS infrastructure.

## Intended Shape

- VPC with public/private subnets
- RDS PostgreSQL in private subnets
- SQS queue plus dead-letter queue
- Lambda worker subscribed to SQS
- IAM roles and policies for Lambda
- Secrets Manager for database credentials or `DATABASE_URL`
- CloudWatch logs for Lambda

## Local Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
```

Use `tfvars/dev.tfvars.example` as a template only when you need to override
the defaults in `variables.tf`.

```bash
cp tfvars/dev.tfvars.example tfvars/dev.tfvars
terraform plan -var-file=tfvars/dev.tfvars
```
