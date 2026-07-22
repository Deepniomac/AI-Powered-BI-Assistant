from sqlalchemy import JSON, Column, ForeignKey, Integer

from app.database.connection import Base


class ValidationReport(Base):
    """
    SQLAlchemy model storing the structured validation report for a processing run.
    """
    __tablename__ = "validation_reports"

    id = Column(Integer, primary_key=True, index=True)
    processing_log_id = Column(Integer, ForeignKey("processing_logs.id"), nullable=False, index=True)
    report_json = Column(JSON, nullable=False)
