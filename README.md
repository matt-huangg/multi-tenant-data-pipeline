# AI Content Processor

AI Content Processor is a small job-based content processing service. It exposes
a FastAPI HTTP API for text and image jobs, stores job state in PostgreSQL,
queues work through SQS, and processes jobs asynchronously in a Lambda worker.

The deployed architecture is intentionally simple: API requests return quickly
after creating a queued job, while slower AI processing happens in the
background.

## Key Features

- Create text processing jobs from submitted text.
- Create image processing jobs from submitted image URLs.
- Persist job payloads, status, results, and errors in PostgreSQL.
- Queue background work through Amazon SQS.
- Process queued jobs with an SQS-triggered Lambda worker.
- Store OpenAI API credentials in AWS Secrets Manager.
- Use RDS-managed Secrets Manager credentials for the database password.
- Run the HTTP API through API Gateway, Lambda, FastAPI, and Mangum.
- Keep Lambda-to-SQS and Lambda-to-Secrets Manager traffic private through VPC
  endpoints.
- Emit worker progress and failures to CloudWatch Logs.

## Architecture

```text
Client
  |
  v
API Gateway HTTP API
  |
  v
HTTP Lambda
  |
  v
FastAPI app
  |
  +--> PostgreSQL/RDS: create and read job records
  |
  +--> SQS: enqueue job id

SQS
  |
  v
Worker Lambda
  |
  +--> PostgreSQL/RDS: load job and update status/result/error
  |
  +--> OpenAI API: process text or image payload
  |
  +--> CloudWatch Logs: worker progress and exceptions
```

## Request Flow

1. A client sends a request to `POST /text-processing/` or
   `POST /image-processing/`.
2. API Gateway forwards the request to the HTTP Lambda.
3. Mangum adapts the Lambda event into an ASGI request for FastAPI.
4. FastAPI creates a `queued` job row in PostgreSQL.
5. The API sends the job id to SQS and returns the job record to the client.
6. SQS invokes the worker Lambda.
7. The worker loads the job, calls OpenAI, and updates the job to `completed`.
8. If processing fails, the worker stores the error message and marks the job
   as `failed`.
9. The client can poll `GET /text-processing/{job_id}` to see job status,
   result, or error.

## Tech Stack

- Python 3.13
- FastAPI
- Mangum
- SQLAlchemy
- PostgreSQL on Amazon RDS
- Amazon API Gateway HTTP API
- AWS Lambda
- Amazon SQS with a dead-letter queue
- AWS Secrets Manager
- AWS VPC, security groups, and interface VPC endpoints
- CloudWatch Logs
- Terraform
- Docker Compose for local development

## Project Structure

```text
app/
  main.py                  FastAPI app entry point
  lambda_http.py           API Gateway/Lambda adapter for FastAPI
  config.py                Environment and Secrets Manager-backed settings
  routes/                  HTTP routes
  services/                Job, SQS, and AI processing services
  workers/sqs_worker.py    SQS-triggered worker Lambda
  db/                      SQLAlchemy session, base, and models
infra/                     Terraform infrastructure definitions
scripts/
  prepare_lambda_source.py Builds the Lambda source tree used by Terraform
docker-compose.yaml        Local API and PostgreSQL services
Dockerfile                 Python application image
requirements.txt           Python dependencies
```

## Lambda Packaging

Terraform packages Lambda from `build/lambda-src`, not directly from `app/`.
After changing application code, refresh that generated folder before applying:

```bash
python3 scripts/prepare_lambda_source.py
```

The Lambda package installs Python dependencies for Amazon Linux:

```bash
python3 -m pip install --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.13 \
  --only-binary=:all: \
  --target=. \
  -r requirements.txt
```

This matters when dependencies include compiled wheels such as `pydantic-core`,
`psycopg2`, or `greenlet`. Wheels installed on macOS are not compatible with the
Lambda Linux runtime.

## Configuration

The app supports two configuration modes.

For local development, use normal environment variables:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_content_processor
AWS_REGION=us-west-2
SQS_QUEUE_URL=https://sqs.us-west-2.amazonaws.com/YOUR_ACCOUNT/YOUR_QUEUE
OPENAI_API_KEY=your-openai-api-key
```

For AWS deployment, Terraform passes these Lambda environment variables:

```env
DB_SECRET_ARN=<rds-managed-secret-arn>
DB_HOST=<rds-host>
DB_NAME=ai_content_processor
DB_PORT=5432
SQS_QUEUE_URL=<jobs-queue-url>
OPENAI_API_KEY_SECRET_ARN=<openai-secret-arn>
```

The app builds `DATABASE_URL` at runtime from the RDS-managed secret and the DB
host/name/port values. You do not manually store the database URL or database
password in `.env`, Terraform variables, or your own Secrets Manager secret for
the deployed path.

## Secrets

RDS manages the database password because Terraform sets:

```hcl
manage_master_user_password = true
```

That creates an AWS-managed database credential secret automatically.

You only need to provide the OpenAI key. Terraform creates the secret container:

```text
ai-content-processor-dev/openai-api-key
```

Put the value into Secrets Manager after the secret exists. Either raw text or
JSON works:

```json
{
  "OPENAI_API_KEY": "your-openai-api-key"
}
```

If the secret page says `No secret value set`, Lambda will fail with:

```text
Secrets Manager can't find the specified secret value for staging label: AWSCURRENT
```

Click **Set secret value** in the AWS console to create the current secret
version.

Do not commit real API keys, `.env` files, Terraform state, or tfvars files.

## Infrastructure

Terraform in `infra/` creates the deployed dev environment:

- VPC with public and private subnets
- Optional NAT Gateway for private subnet internet egress
- Interface VPC endpoints for SQS and Secrets Manager
- RDS PostgreSQL in private subnets
- SQS jobs queue and dead-letter queue
- HTTP Lambda for the FastAPI API
- Worker Lambda subscribed to SQS
- API Gateway HTTP API with a default proxy route to the HTTP Lambda
- Security groups allowing Lambda to reach RDS and VPC endpoints
- IAM permissions for SQS, Secrets Manager, Lambda VPC networking, and API
  Gateway invocation
- CloudWatch log groups managed by the Lambda module with 14-day retention

Lambda functions run in private subnets so they can reach private RDS. SQS and
Secrets Manager are reachable privately through VPC endpoints.

The worker needs public internet egress to call OpenAI. Set this in your tfvars
file if deployed AI processing should work end to end:

```hcl
enable_nat_gateway = true
```

Leaving it `false` keeps the lower-cost dev posture, but worker calls to OpenAI
will fail with a connectivity error unless another egress design is added.

## Deploy

Use an AWS CLI profile or exported credentials before running Terraform:

```bash
export AWS_PROFILE=ai-processing-app-user
aws sts get-caller-identity
```

Prepare the Lambda source tree from the project root:

```bash
python3 scripts/prepare_lambda_source.py
```

Create a dev tfvars file if you need overrides:

```bash
cd infra
cp tfvars/dev.tfvars.example tfvars/dev.tfvars
```

Initialize, validate, and review the Terraform plan:

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -var-file=tfvars/dev.tfvars
```

Apply after reviewing the plan:

```bash
terraform apply -var-file=tfvars/dev.tfvars
```

Get the deployed API URL:

```bash
terraform output -raw api_endpoint
```

This project currently uses local Terraform state. Add an S3 backend before
sharing deployments across multiple machines, teammates, or CI/CD.

## API Endpoints

### Health Check

```http
GET /
```

Response:

```json
{
  "message": "hello world"
}
```

### Create a Text Processing Job

```http
POST /text-processing/
Content-Type: application/json
```

Request:

```json
{
  "text": "Summarize this content"
}
```

Example:

```bash
curl -X POST "$API_URL/text-processing/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Summarize this content"}'
```

### Get a Text Processing Job

```http
GET /text-processing/{job_id}
```

Example:

```bash
curl "$API_URL/text-processing/1"
```

### Create an Image Processing Job

```http
POST /image-processing/
Content-Type: application/json
```

Request:

```json
{
  "image_url": "https://example.com/image.jpg"
}
```

Example:

```bash
curl -X POST "$API_URL/image-processing/" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/image.jpg"}'
```

## Job Statuses

Jobs are stored in the `jobs` table and move through these statuses:

- `queued`: Created in PostgreSQL and sent to SQS.
- `running`: Worker started processing the job.
- `completed`: Worker finished successfully and stored a result.
- `failed`: Worker caught an error and stored the error message.

The worker logs progress and exceptions to:

```text
/aws/lambda/ai-content-processor-dev-worker
```

The HTTP Lambda logs are in:

```text
/aws/lambda/ai-content-processor-dev-http
```

## Test A Deployed Job

After deployment:

```bash
cd infra
API_URL=$(terraform output -raw api_endpoint)
```

Create a text job:

```bash
curl -X POST "$API_URL/text-processing/" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test worker logging and error handling"}'
```

Check the returned job id:

```bash
curl "$API_URL/text-processing/1"
```

Replace `1` with the id returned by the create request.

If OpenAI credits are unavailable, the job should eventually become `failed`
with the provider error stored in the `error` field. The same exception is also
logged by the worker Lambda in CloudWatch.

For example, a successful infrastructure test with no OpenAI credits will show:

- `Received 1 SQS record(s)`
- `Processing job <id>`
- `Failed to process job <id>`
- `insufficient_quota`
- `Returning 0 batch item failure(s)`

That means API Gateway, HTTP Lambda, RDS, SQS, worker Lambda, Secrets Manager,
and OpenAI network access are all wired correctly. The job failed only because
OpenAI rejected the request.

## Database Access

The RDS instance is private. Lambdas can reach it from inside the VPC, but tools
on your laptop, such as TablePlus, cannot connect directly.

To inspect the database from TablePlus, use one of these approaches:

- Preferred: create a small EC2 bastion or SSM-managed instance in the VPC and
  connect through a port-forwarding tunnel.
- Temporary/dev only: make RDS publicly accessible and allow only your current
  IP address to port `5432` in the RDS security group.

TablePlus connection details are:

```text
Host: <terraform output rds_endpoint host>
Port: 5432
User: <username from the RDS-managed Secrets Manager secret>
Password: <password from the RDS-managed Secrets Manager secret>
Database: <db_name from tfvars>
SSL mode: require or prefer
```

Do not open PostgreSQL to `0.0.0.0/0`.

## Destroy And Recreate

Destroy the AWS resources when you are done testing to avoid ongoing charges:

```bash
cd infra
AWS_PROFILE=ai-processing-app-user terraform destroy -var-file=tfvars/dev.tfvars
```

Terraform will show the destroy plan and ask for `yes`.

You can recreate the environment later:

```bash
cd infra
python3 ../scripts/prepare_lambda_source.py
AWS_PROFILE=ai-processing-app-user terraform apply -var-file=tfvars/dev.tfvars
```

After a destroy/recreate cycle, expect fresh infrastructure:

- RDS data is gone unless you restore from a snapshot.
- SQS messages are gone.
- API Gateway URL may change.
- The OpenAI secret value must be set again.
- CloudWatch logs may be recreated from scratch.

After destroy, check for leftovers that can still cost money:

- RDS snapshots
- CloudWatch log groups
- Secrets Manager secrets scheduled for deletion
- NAT Gateways, if enabled

## Local Development

Local development can still use Docker Compose or a local Python environment,
but the deployed AWS path is the primary architecture.

With Docker Compose:

```bash
docker compose up --build
```

The local API is available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

Without Docker, start PostgreSQL separately, then:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_content_processor
uvicorn app.main:app --reload
```

Run the local worker separately only if `SQS_QUEUE_URL` points at a queue you
want to consume:

```bash
python3 -m app.workers.sqs_worker
```
