"""Text processing HTTP routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.jobs import job_service

router = APIRouter(prefix="/text-processing", tags=["text-processing"])


class TextProcessingRequest(BaseModel):
    text: str


@router.post("/")
def create_text_processing_job(payload: TextProcessingRequest):
    """Create and queue a text processing job."""
    return job_service.create_job(job_type="text", payload={"text": payload.text})


@router.get("/{job_id}")
def get_text_summary(job_id: int):
    """Get text process result"""
    return job_service.get_job(job_id)
