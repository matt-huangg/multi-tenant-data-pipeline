"""Processing service for text and image jobs."""

from app.services.jobs import job_service


class ProcessingService:
    """Create and process AI content jobs."""

    def create_text_job(self, text: str):
        """Create and queue a text processing job."""
        return job_service.create_job(job_type="text", payload={"text": text})

    def create_image_job(self, image_url: str):
        """Create and queue an image processing job."""
        return job_service.create_job(job_type="image", payload={"image_url": image_url})


processing_service = ProcessingService()
