from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.processing import ProcessingResponse
from app.services.processing.processor import ReportProcessor
from app.services.report_service import require_owned_report

router = APIRouter(tags=["Processing"])
processor = ReportProcessor()


@router.post("/api/reports/{report_id}/process", response_model=ProcessingResponse)
def process_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProcessingResponse:
    """
    Parses, validates, and persists structured processing output for an owned report.
    """
    report = require_owned_report(db, report_id, current_user.id)
    return processor.process_report(db, report)


@router.get("/api/reports/{report_id}/process", response_model=ProcessingResponse)
def get_processing_result(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProcessingResponse:
    """
    Returns the latest processing result for an owned report.
    """
    report = require_owned_report(db, report_id, current_user.id)
    return processor.get_latest_processing_result(db, report)
