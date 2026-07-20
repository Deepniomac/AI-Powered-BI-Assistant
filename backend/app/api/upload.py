from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.report import DeleteReportResponse, ReportResponse
from app.services.file_service import delete_file, save_upload_file
from app.services.report_service import create_report, list_reports, require_owned_report, soft_delete_report

router = APIRouter(tags=["Reports"])


@router.post("/api/upload", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Validates, stores, and persists metadata for a user-uploaded report.
    """
    saved_file = await save_upload_file(file)
    try:
        report = create_report(
            db,
            user_id=current_user.id,
            original_name=saved_file["original_name"],
            stored_name=saved_file["stored_name"],
            file_type=saved_file["file_type"],
            file_size=saved_file["file_size"],
        )
        return report
    except HTTPException:
        delete_file(saved_file["stored_name"])
        raise
    except Exception as exc:
        delete_file(saved_file["stored_name"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save report metadata",
        ) from exc


@router.get("/api/reports", response_model=list[ReportResponse])
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the current user's active upload history.
    """
    return list_reports(db, current_user.id)


@router.delete("/api/reports/{report_id}", response_model=DeleteReportResponse)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Removes a stored file from disk and soft-deletes its report record.
    """
    report = require_owned_report(db, report_id, current_user.id)
    delete_file(report.stored_name)
    soft_delete_report(db, report)
    return {"message": "Report deleted successfully"}
