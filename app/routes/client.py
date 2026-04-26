"""Client HTTP routes."""

from fastapi import APIRouter

from app.services import clients as client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/")
def get_clients():
    """List clients."""
    return client_service.get_clients()


@router.get("/{client_id}")
def get_client(client_id: int):
    """Fetch one client."""
    return client_service.get_client(client_id)


@router.post("/")
def create_client():
    """Create a client and enqueue its follow-up job."""
    return client_service.create_client()


@router.put("/{client_id}")
def update_client(client_id: int):
    """Update a client."""
    return client_service.update_client(client_id)


@router.delete("/{client_id}")
def delete_client(client_id: int):
    """Delete a client."""
    return client_service.delete_client(client_id)
