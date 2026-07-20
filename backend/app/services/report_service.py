from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.report import Report


def create_report(
    db: Session,
    *,
    user_id: int,
    original_name: str,
    stored_name: str,
    file_type: str,
    file_size: int,
) -> Report:
    """
    Creates a report metadata record scoped to the uploading user.
    """
    report = Report(
        user_id=user_id,
        original_name=original_name,
        stored_name=stored_name,
        file_type=file_type,
        file_size=file_size,
        status="Uploaded",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, user_id: int) -> list[Report]:
    """
    Lists non-deleted reports for the given user, newest first.
    """
    return (
        db.query(Report)
        .filter(Report.user_id == user_id, Report.status != "Deleted")
        .order_by(Report.upload_time.desc())
        .all()
    )


def get_report_by_id(db: Session, report_id: int, user_id: int) -> Optional[Report]:
    """
    Retrieves a single non-deleted report owned by the requesting user.
    """
    return (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == user_id, Report.status != "Deleted")
        .first()
    )


def require_owned_report(db: Session, report_id: int, user_id: int) -> Report:
    """
    Returns the requested report or a 404 when it does not exist for the current user.
    """
    report = get_report_by_id(db, report_id, user_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


def soft_delete_report(db: Session, report: Report) -> Report:
    """
    Marks a report as deleted while keeping its metadata history.
    """
    report.status = "Deleted"
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
