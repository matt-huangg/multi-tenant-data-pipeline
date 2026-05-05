"""SQS worker for queued content processing jobs."""

import json
import time

from app.services.ai_processing import processing_service
from app.services.jobs import job_service
from app.services.sqs import delete_message
from app.services.sqs import receive_messages


def process_message_body(body: str) -> None:
    """Apply one SQS message body to the persisted job store."""
    payload = json.loads(body)
    job_id = payload.get("job_id")
    if job_id is None:
        return

    job = job_service.get_job(job_id)
    if job is None:
        return

    try:
        result = processing_service.process_job(job)
        job_service.process_job(job_id, result=result)
    except Exception as exc:
        job_service.process_job(job_id, error=str(exc))


def lambda_handler(event, context):
    """Process messages delivered by an SQS Lambda event source mapping."""
    batch_item_failures = []

    for record in event.get("Records", []):
        try:
            process_message_body(record["body"])
        except Exception:
            batch_item_failures.append({
                "itemIdentifier": record["messageId"],
            })

    return {"batchItemFailures": batch_item_failures}


def poll_queue():
    """Continuously poll SQS and process incoming job messages."""
    while True:
        messages = receive_messages(max_messages=5, wait_time_seconds=10)
        if not messages:
            time.sleep(1)
            continue

        for message in messages:
            process_message_body(message["Body"])
            delete_message(message["ReceiptHandle"])


if __name__ == "__main__":
    poll_queue()
