"""Job service functions backed by the database."""

from contextlib import contextmanager

from app.db.models.jobs import Job
from app.db.session import SessionLocal
from app.services.sqs import send_message


class JobService:
    """Database-backed job operations with per-call sessions."""

    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    @contextmanager
    def _session(self):
        """Open a session and guarantee it closes after the operation."""
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def _serialize_job(job: Job):
        """Convert a Job ORM instance into a JSON-friendly dict."""
        return {
            "id": job.id,
            "type": job.type,
            "status": job.status,
            "payload": job.payload,
            "result": job.result,
            "error": job.error,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }

    def create_job(self, job_type: str = "test", payload: dict | None = None):
        """Create a new queued processing job and persist it."""
        with self._session() as db:
            new_job = Job(type=job_type, status="queued", payload=payload)
            db.add(new_job)
            db.commit()
            db.refresh(new_job)

            send_message({
                "event_type": job_type,
                "job_id": new_job.id,
            })
            return self._serialize_job(new_job)

    def get_job(self, job_id: int):
        """Return a single job by ID, or None if it does not exist."""
        with self._session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job is None:
                return None
            return self._serialize_job(job)

    def get_jobs(self):
        """Return all known jobs."""
        with self._session() as db:
            jobs = db.query(Job).order_by(Job.id.desc()).all()
            return [self._serialize_job(job) for job in jobs]

    def process_job(self, job_id: int, result: dict | None = None, error: str | None = None):
        """Persist the final status for a processed background job."""
        with self._session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job is None:
                return None

            job.status = "running"
            db.commit()
            db.refresh(job)

            if error:
                job.status = "failed"
                job.error = error
                job.result = None
            else:
                job.status = "completed"
                job.result = result
                job.error = None

            db.commit()
            db.refresh(job)
            return self._serialize_job(job)


job_service = JobService()
