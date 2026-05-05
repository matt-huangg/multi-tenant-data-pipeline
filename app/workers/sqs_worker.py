"""SQS worker for queued content processing jobs."""

import json
import logging
import time

from app.services.ai_processing import processing_service
from app.services.jobs import job_service
from app.services.sqs import delete_message
from app.services.sqs import receive_messages


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def process_message_body(body: str) -> None:
    """Apply one SQS message body to the persisted job store."""
    payload = json.loads(body)
    job_id = payload.get("job_id")
    if job_id is None:
        logger.warning("Skipping SQS message without job_id: %s", body)
        return

    logger.info("Processing job %s", job_id)
    job = job_service.get_job(job_id)
    if job is None:
        logger.warning("Skipping SQS message for missing job %s", job_id)
        return

    try:
        result = processing_service.process_job(job)
        job_service.process_job(job_id, result=result)
        logger.info("Completed job %s", job_id)
    except Exception as exc:
        logger.exception("Failed to process job %s", job_id)
        job_service.process_job(job_id, error=str(exc))


def lambda_handler(event, context):
    """Process messages delivered by an SQS Lambda event source mapping."""
    batch_item_failures = []
    records = event.get("Records", [])
    logger.info("Received %s SQS record(s)", len(records))

    for record in records:
        try:
            process_message_body(record["body"])
        except Exception:
            logger.exception("Failed to handle SQS record %s", record.get("messageId"))
            batch_item_failures.append({
                "itemIdentifier": record["messageId"],
            })

    logger.info("Returning %s batch item failure(s)", len(batch_item_failures))
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
