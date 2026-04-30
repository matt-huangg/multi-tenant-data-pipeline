# AI Content Processor

A FastAPI service that accepts text and image processing jobs, stores them in
PostgreSQL, and queues background work through AWS SQS. A separate worker polls
the queue and updates each job status.

## What It Does

- Creates text processing jobs from submitted text.
- Creates image processing jobs from submitted image URLs.
- Persists jobs, payloads, status, results, and errors in PostgreSQL.
- Sends queued job IDs to SQS.
- Runs a worker process that consumes SQS messages and marks jobs as completed.

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- AWS SQS via boto3
- Docker Compose

## Project Structure

```text
app/
  main.py                  FastAPI app entry point
  config.py                Environment-backed settings
  routes/                  HTTP routes
  services/                Job, SQS, and processing services
  workers/sqs_worker.py    SQS polling worker
  db/                      SQLAlchemy session, base, and models
infra/                     Terraform infrastructure definitions
docker-compose.yaml        API, worker, and PostgreSQL services
Dockerfile                 Python application image
requirements.txt           Python dependencies
```

## Environment Variables

Create a `.env` file in the project root.

```env
AWS_REGION=us-west-2
SQS_QUEUE_URL=https://sqs.us-west-2.amazonaws.com/YOUR_ACCOUNT/YOUR_QUEUE
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

`docker-compose.yaml` sets `DATABASE_URL` automatically for the API and worker:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_content_processor
```

For non-Docker local development, set `DATABASE_URL` yourself.

## Run With Docker Compose

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

This starts:

- `api`: FastAPI app on port `8000`
- `db`: PostgreSQL on port `5432`
- `worker`: SQS polling worker

## Run Locally Without Docker

Start PostgreSQL separately, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set the required environment variables:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_content_processor
export AWS_REGION=us-west-2
export SQS_QUEUE_URL=https://sqs.us-west-2.amazonaws.com/YOUR_ACCOUNT/YOUR_QUEUE
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Start the worker in another terminal:

```bash
python -m app.workers.sqs_worker
```

## Infrastructure

Terraform configuration lives in `infra/`. The current target shape is:

- VPC with public and private subnets
- SQS queue plus dead-letter queue
- RDS PostgreSQL in private subnets
- Lambda or containerized worker for queued jobs
- IAM, Secrets Manager, and CloudWatch resources

The project currently uses local Terraform state because it is a solo side
project. Add an S3 backend later if multiple people, multiple machines, or
CI/CD need to run Terraform against the same AWS account.

Use an AWS CLI profile or exported credentials before running Terraform:

```bash
export AWS_PROFILE=ai-processing-app-user
aws sts get-caller-identity
```

Run Terraform from the `infra/` directory:

```bash
python3 scripts/prepare_lambda_source.py
cd infra
terraform init
terraform fmt
terraform validate
terraform plan
```

The defaults in `infra/variables.tf` are enough for the dev side-project setup.
If overrides are needed, copy the example file:

```bash
cp tfvars/dev.tfvars.example tfvars/dev.tfvars
terraform plan -var-file=tfvars/dev.tfvars
```

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
curl -X POST http://localhost:8000/text-processing/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Summarize this content"}'
```

### Get a Text Processing Job

```http
GET /text-processing/{job_id}
```

Example:

```bash
curl http://localhost:8000/text-processing/1
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
curl -X POST http://localhost:8000/image-processing/ \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/image.jpg"}'
```

## Job Statuses

Jobs are stored in the `jobs` table and move through these statuses:

- `queued`: Created and sent to SQS.
- `running`: Worker received the SQS message and started processing.
- `completed`: Worker finished processing successfully.
- `failed`: Worker finished with an error.

The current worker simulates processing and stores an empty result unless a
caller passes a result or error into the job service.

## Notes

- `SQS_QUEUE_URL` is required when creating jobs because job creation sends a
  message to SQS.
- Database tables are created automatically when the FastAPI app starts.
- The worker must be running for queued jobs to move to `running` and
  `completed`.
