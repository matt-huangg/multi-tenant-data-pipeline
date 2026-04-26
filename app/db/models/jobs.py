from sqlalchemy import Column, Integer, String

from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
