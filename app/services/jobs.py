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
            "client_id": job.client_id,
            "status": job.status,
        }

    def create_job(self, client_id: int):
        """Create a new queued job for a client and persist it."""
        with self._session() as db:
            new_job = Job(client_id=client_id, status="queued")
            db.add(new_job)
            db.commit()
            db.refresh(new_job)

            send_message({
                'event_type': 'test',
                'job_id': new_job.id,
                'client_id': client_id
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

    def process_job(self, job_id: int):
        """Simulate background work for a job and persist the status changes."""
        import time

        with self._session() as db:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job is None:
                return None

            job.status = "running"
            db.commit()
            db.refresh(job)

            time.sleep(2)

            job.status = "completed"
            db.commit()
            db.refresh(job)
            return self._serialize_job(job)


job_service = JobService()
