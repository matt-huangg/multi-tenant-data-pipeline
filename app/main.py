"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import init_db
from app.routes import client, jobs, root


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables before serving requests."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(root.router)
app.include_router(client.router)
app.include_router(jobs.router)
