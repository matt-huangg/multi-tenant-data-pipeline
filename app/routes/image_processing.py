"""Image processing HTTP routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_processing import processing_service

router = APIRouter(prefix="/image-processing", tags=["image-processing"])


class ImageProcessingRequest(BaseModel):
    image_url: str


@router.post("/")
def create_image_processing_job(payload: ImageProcessingRequest):
    """Create and queue an image processing job."""
    return processing_service.create_image_job(payload.image_url)
