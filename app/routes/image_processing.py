"""Image processing HTTP routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.jobs import job_service

router = APIRouter(prefix="/image-processing", tags=["image-processing"])


class ImageProcessingRequest(BaseModel):
    image_url: str


@router.post("/")
def create_image_processing_job(payload: ImageProcessingRequest):
    """Create and queue an image processing job."""
    return job_service.create_job(job_type="image", payload={"image_url": payload.image_url})
