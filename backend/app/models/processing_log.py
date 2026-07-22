from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


class ProcessingLog(Base):
    """
    SQLAlchemy model recording each processing attempt for an uploaded report.
    """
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    error_count = Column(Integer, nullable=False, default=0)
    warning_count = Column(Integer, nullable=False, default=0)
    validation_status = Column(String, nullable=False, default="failed")
    parsed_data_path = Column(String, nullable=True)
