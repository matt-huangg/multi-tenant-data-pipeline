"""Client-related service helpers."""

from app.services.jobs import job_service
from app.services.sqs import send_message


def get_clients():
    """Return the in-memory client list placeholder."""
    return {"message": "get all clients"}


def get_client(client_id: int):
    """Return a single client placeholder."""
    return {"message": "get client", "client_id": client_id}


def create_client():
    """Create a client and queue its initial job."""
    client_id = 1
    job = job_service.create_job(client_id)
    send_message({"job_id": job["id"], "client_id": client_id, "event_type": "client.created"})

    return {
        "message": "create client",
        "client_id": client_id,
        "job": job,
    }


def update_client(client_id: int):
    """Update a client placeholder."""
    return {"message": "update client", "client_id": client_id}


def delete_client(client_id: int):
    """Delete a client placeholder."""
    return {"message": "delete client", "client_id": client_id}
