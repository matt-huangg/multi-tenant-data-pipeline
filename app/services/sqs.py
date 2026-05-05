"""Small SQS helper used for local queue testing."""

import json

import boto3
import pprint

from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
    SQS_QUEUE_URL,
)


def build_sqs_client():
    """Create a boto3 SQS client from environment-backed settings."""
    client_kwargs = {"region_name": AWS_REGION}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
        if AWS_SESSION_TOKEN:
            client_kwargs["aws_session_token"] = AWS_SESSION_TOKEN

    return boto3.client("sqs", **client_kwargs)


def send_message(payload: dict):
    """Send a JSON payload to the configured queue."""
    if not SQS_QUEUE_URL:
        raise RuntimeError("SQS_QUEUE_URL is not set")

    sqs = build_sqs_client()
    response = sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(payload))
    message_id = response.get("MessageId")
    if not message_id:
        raise RuntimeError(f"Unexpected SQS response: {response}")

    return response


def receive_messages(max_messages: int = 1, wait_time_seconds: int = 10):
    """Poll the configured queue for messages."""
    if not SQS_QUEUE_URL:
        raise RuntimeError("SQS_QUEUE_URL is not set")

    sqs = build_sqs_client()
    response = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=wait_time_seconds,
    )
    return response.get("Messages", [])


def delete_message(receipt_handle: str):
    """Delete a processed message from the configured queue."""
    if not SQS_QUEUE_URL:
        raise RuntimeError("SQS_QUEUE_URL is not set")

    sqs = build_sqs_client()
    return sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)


def test_sqs_client():
    """Send a test message to SQS and print the response."""
    send_resp = send_message({"test": True, "message": "heyo"})

    print("sent:")
    pprint.pprint(send_resp)


if __name__ == "__main__":
    test_sqs_client()
