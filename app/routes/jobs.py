"""Job HTTP routes."""

from fastapi import APIRouter, HTTPException

from app.services.jobs import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/")
def list_jobs():
    """List all jobs."""
    return job_service.get_jobs()


@router.get("/{job_id}")
def get_job(job_id: int):
    """Fetch a single job."""
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/")
def create_job(client_id: int):
    """Create a queued job for a client."""
    return job_service.create_job(client_id)
