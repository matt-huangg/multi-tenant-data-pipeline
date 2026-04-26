"""Database session and engine setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.db.base import Base

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Create tables for all registered models."""
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session for request or worker usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
