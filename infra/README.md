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
- Interface VPC endpoints for private Lambda access to SQS and Secrets Manager

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

## Private Lambda Egress

Lambda functions run in private subnets so they can reach RDS. SQS and Secrets
Manager access stays private through VPC endpoints.

The worker still needs public internet egress to call OpenAI. Set
`enable_nat_gateway = true` before applying if deployed AI processing should
work end to end. Leaving it `false` keeps the lower-cost dev posture, but worker
OpenAI calls will fail without another egress design.
