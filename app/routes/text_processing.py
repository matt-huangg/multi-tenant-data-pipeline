"""Text processing HTTP routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_processing import processing_service

router = APIRouter(prefix="/text-processing", tags=["text-processing"])

class TextProcessingRequest(BaseModel):
    text: str

@router.post("/")
def create_text_processing_job(payload: TextProcessingRequest):
    """Create and queue a text processing job."""
    return processing_service.create_text_job(payload.text)
