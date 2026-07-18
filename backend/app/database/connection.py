from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Create database engine based on configurations
# (Supports sqlite connection argument for local testing if configured)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Create SessionLocal class for local session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy declarative models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    Provides a session for the request lifespan and ensures it is closed
    when the request handling completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
