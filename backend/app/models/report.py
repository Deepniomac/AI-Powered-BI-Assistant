from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database.connection import Base


class Report(Base):
    """
    SQLAlchemy model representing uploaded reports owned by individual users.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_name = Column(String, nullable=False)
    stored_name = Column(String, unique=True, nullable=False, index=True)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String, default="Uploaded", nullable=False)
