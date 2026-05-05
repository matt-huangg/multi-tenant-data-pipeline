"""Central app configuration loaded from environment variables."""

import json
import os
from functools import lru_cache
from urllib.parse import quote_plus

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def _build_boto3_client(service_name: str):
    client_kwargs = {"region_name": AWS_REGION}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    return boto3.client(service_name, **client_kwargs)


@lru_cache(maxsize=16)
def get_secret_string(secret_arn: str) -> str:
    """Read and cache a Secrets Manager secret value."""
    response = _build_boto3_client("secretsmanager").get_secret_value(
        SecretId=secret_arn
    )
    return response["SecretString"]


def _database_url_from_secret() -> str:
    secret_arn = os.getenv("DB_SECRET_ARN")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_port = os.getenv("DB_PORT", "5432")

    if not secret_arn or not db_host or not db_name:
        return ""

    secret = json.loads(get_secret_string(secret_arn))
    username = quote_plus(secret["username"])
    password = quote_plus(secret["password"])

    return f"postgresql://{username}:{password}@{db_host}:{db_port}/{db_name}"


def _openai_api_key_from_secret() -> str | None:
    secret_arn = os.getenv("OPENAI_API_KEY_SECRET_ARN")
    if not secret_arn:
        return None

    secret_string = get_secret_string(secret_arn)
    try:
        secret = json.loads(secret_string)
    except json.JSONDecodeError:
        return secret_string

    return secret.get("OPENAI_API_KEY") or secret.get("api_key")


DATABASE_URL = os.getenv("DATABASE_URL") or _database_url_from_secret()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or _openai_api_key_from_secret()
