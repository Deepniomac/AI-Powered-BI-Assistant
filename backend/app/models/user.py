from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database.connection import Base

class User(Base):
    """
    SQLAlchemy model representing system users.
    Contains profile information, security credentials, and system roles.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="analyst", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
