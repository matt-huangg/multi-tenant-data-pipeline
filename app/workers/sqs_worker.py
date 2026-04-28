"""SQS polling worker for client jobs."""

import json
import time

from app.services.jobs import job_service
from app.services.ai_processing import processing_service
from app.services.sqs import delete_message
from app.services.sqs import receive_messages


def process_message(message):
    """Apply one SQS message to the persisted job store."""
    body = json.loads(message["Body"])
    job_id = body.get("job_id")
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


def poll_queue():
    """Continuously poll SQS and process incoming job messages."""
    print('polling triggered')
    while True:
        print('polling')
        messages = receive_messages(max_messages=5, wait_time_seconds=10)
        if not messages:
            time.sleep(1)
            continue

        for message in messages:
            process_message(message)
            delete_message(message["ReceiptHandle"])


if __name__ == "__main__":
    poll_queue()
