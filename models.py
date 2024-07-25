import enum
from sqlalchemy import Column, String, Integer, Enum
from database import Base


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)


class JobStatus(enum.Enum):
    completed = "completed"
    running = "running"
    incomplete = "incomplete"


class Job(Base):
    __tablename__ = "jobs"

    filename = Column(String(50), primary_key=True, unique=True, nullable=False)
    description = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(JobStatus), nullable=False)
    progress = Column(Integer, nullable=False, default=0)
