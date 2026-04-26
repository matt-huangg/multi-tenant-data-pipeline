"""Root HTTP routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_root():
    """Health-style root response."""
    return {"message": "hello world"}
