import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.processing_log import ProcessingLog
from app.models.report import Report
from app.models.validation_report import ValidationReport
from app.schemas.processing import ProcessingResponse
from app.services.file_service import UPLOADS_DIR
from app.services.parser.parser_factory import get_parser
from app.services.validation.validation_models import ValidationIssue, ValidationReportPayload, ValidationSummary
from app.services.validation.validator import DatasetValidator

logger = logging.getLogger(__name__)

PARSED_REPORTS_DIR = Path(__file__).resolve().parents[3] / "reports"


class ReportProcessor:
    """
    Orchestrates parse, validate, persistence, and response shaping for Phase 3.1.
    """

    def __init__(self):
        self.validator = DatasetValidator()

    def process_report(self, db: Session, report: Report) -> ProcessingResponse:
        started_at = datetime.now(timezone.utc)
        processing_log = ProcessingLog(
            report_id=report.id,
            status="pending",
            started_at=started_at,
            validation_status="failed",
            error_count=0,
            warning_count=0,
            parsed_data_path=None,
        )
        db.add(processing_log)
        db.commit()
        db.refresh(processing_log)

        file_path = UPLOADS_DIR / report.stored_name
        metadata = self._base_metadata(report)

        try:
            if not file_path.exists():
                return self._finalize_failed_processing(
                    db,
                    processing_log,
                    report,
                    metadata,
                    "Uploaded file is missing on disk",
                )

            parser = get_parser(report, file_path)
            logger.info("Processing report_id=%s with parser=%s", report.id, parser.__class__.__name__)

            parse_started = time.perf_counter()
            parser_result = parser.parse()
            parse_duration = time.perf_counter() - parse_started
            logger.info("Report parse completed for report_id=%s in %.4fs", report.id, parse_duration)

            metadata.update(parser_result["metadata"])
            parse_issues = self._build_parser_issues(parser_result)

            if not parser_result["success"] or parser_result["dataframe"] is None:
                validation_payload = self._build_validation_payload(parse_issues)
                return self._persist_and_respond(
                    db,
                    processing_log,
                    report,
                    metadata,
                    validation_payload,
                    None,
                    status_label="processing_failed",
                    message=parser_result["errors"][0] if parser_result["errors"] else "Processing failed",
                )

            dataframe: pd.DataFrame = parser_result["dataframe"]

            validation_started = time.perf_counter()
            validation_payload = self.validator.validate(dataframe)
            validation_duration = time.perf_counter() - validation_started
            logger.info(
                "Report validation completed for report_id=%s in %.4fs with errors=%s warnings=%s",
                report.id,
                validation_duration,
                validation_payload.summary.errors,
                validation_payload.summary.warnings,
            )

            combined_issues = parse_issues + validation_payload.issues
            combined_payload = self._build_validation_payload(combined_issues)
            parsed_data_path = self._persist_dataframe(dataframe, report.id)
            return self._persist_and_respond(
                db,
                processing_log,
                report,
                metadata,
                combined_payload,
                parsed_data_path,
                status_label="processing_completed",
                message="Report processed successfully",
            )
        except PermissionError:
            return self._finalize_failed_processing(
                db,
                processing_log,
                report,
                metadata,
                "Permission denied while accessing report files",
            )
        except Exception as exc:
            logger.exception("Unexpected processing failure for report_id=%s", report.id)
            return self._finalize_failed_processing(
                db,
                processing_log,
                report,
                metadata,
                f"Unexpected processing error: {exc}",
            )

    def get_latest_processing_result(self, db: Session, report: Report) -> ProcessingResponse:
        processing_log = (
            db.query(ProcessingLog)
            .filter(ProcessingLog.report_id == report.id)
            .order_by(ProcessingLog.started_at.desc(), ProcessingLog.id.desc())
            .first()
        )
        if processing_log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report has not been processed yet",
            )

        validation_record = (
            db.query(ValidationReport)
            .filter(ValidationReport.processing_log_id == processing_log.id)
            .order_by(ValidationReport.id.desc())
            .first()
        )
        if validation_record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation report not found for the latest processing run",
            )

        validation_payload = ValidationReportPayload.model_validate(validation_record.report_json)
        metadata = self._load_persisted_metadata(report, processing_log.parsed_data_path)

        return ProcessingResponse(
            processing_log_id=processing_log.id,
            report_id=report.id,
            status="processing_completed" if processing_log.status == "completed" else "processing_failed",
            validation_status=processing_log.validation_status,
            parsed_data_path=processing_log.parsed_data_path,
            metadata=metadata,
            validation_report=validation_payload,
            message="Latest processing result loaded successfully",
            error_count=processing_log.error_count,
            warning_count=processing_log.warning_count,
        )

    def _persist_dataframe(self, dataframe: pd.DataFrame, report_id: int) -> str:
        PARSED_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = PARSED_REPORTS_DIR / f"report-{report_id}-{uuid.uuid4()}.parquet"
        dataframe.to_parquet(file_path, index=False)
        return str(file_path)

    def _persist_and_respond(
        self,
        db: Session,
        processing_log: ProcessingLog,
        report: Report,
        metadata: dict[str, Any],
        validation_payload: ValidationReportPayload,
        parsed_data_path: str | None,
        *,
        status_label: str,
        message: str,
    ) -> ProcessingResponse:
        completed_at = datetime.now(timezone.utc)
        processing_log.status = "completed" if status_label == "processing_completed" else "failed"
        processing_log.completed_at = completed_at
        processing_log.duration_seconds = max((completed_at - processing_log.started_at).total_seconds(), 0.0)
        processing_log.error_count = validation_payload.summary.errors
        processing_log.warning_count = validation_payload.summary.warnings
        processing_log.validation_status = validation_payload.summary.status
        processing_log.parsed_data_path = parsed_data_path
        db.add(processing_log)
        db.commit()
        db.refresh(processing_log)

        validation_record = ValidationReport(
            processing_log_id=processing_log.id,
            report_json=validation_payload.model_dump(),
        )
        db.add(validation_record)
        db.commit()

        return ProcessingResponse(
            processing_log_id=processing_log.id,
            report_id=report.id,
            status=status_label,
            validation_status=processing_log.validation_status,
            parsed_data_path=processing_log.parsed_data_path,
            metadata=metadata,
            validation_report=validation_payload,
            message=message,
            error_count=processing_log.error_count,
            warning_count=processing_log.warning_count,
        )

    def _finalize_failed_processing(
        self,
        db: Session,
        processing_log: ProcessingLog,
        report: Report,
        metadata: dict[str, Any],
        message: str,
    ) -> ProcessingResponse:
        validation_payload = self._build_validation_payload(
            [
                ValidationIssue(
                    severity="error",
                    type="processing_error",
                    column=None,
                    description=message,
                    affected_rows=None,
                    recommendation="Inspect the uploaded file and re-run processing",
                    count=1,
                )
            ]
        )
        return self._persist_and_respond(
            db,
            processing_log,
            report,
            metadata,
            validation_payload,
            None,
            status_label="processing_failed",
            message=message,
        )

    def _build_validation_payload(self, issues: list[ValidationIssue]) -> ValidationReportPayload:
        error_count = sum(1 for issue in issues if issue.severity == "error")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")
        return ValidationReportPayload(
            summary=ValidationSummary(
                status="failed" if error_count > 0 else "passed",
                errors=error_count,
                warnings=warning_count,
            ),
            issues=issues,
        )

    def _build_parser_issues(self, parser_result: dict[str, Any]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for warning in parser_result.get("warnings", []):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    type="parser_warning",
                    column=None,
                    description=warning,
                    affected_rows=None,
                    recommendation="Review the parsing note before downstream cleaning",
                    count=1,
                )
            )
        for error in parser_result.get("errors", []):
            issues.append(
                ValidationIssue(
                    severity="error",
                    type="parser_error",
                    column=None,
                    description=error,
                    affected_rows=None,
                    recommendation="Verify the file format and contents, then process it again",
                    count=1,
                )
            )
        return issues

    def _base_metadata(self, report: Report) -> dict[str, Any]:
        file_path = UPLOADS_DIR / report.stored_name
        extension = (report.file_type or file_path.suffix.lstrip(".")).lower()
        return {
            "filename": report.original_name,
            "extension": extension,
            "file_size": report.file_size,
            "upload_timestamp": report.upload_time.isoformat(),
        }

    def _load_persisted_metadata(self, report: Report, parsed_data_path: str | None) -> dict[str, Any]:
        metadata = self._base_metadata(report)
        if not parsed_data_path:
            metadata.update(
                {
                    "total_rows": 0,
                    "total_columns": 0,
                    "column_names": [],
                    "detected_dtypes": {},
                }
            )
            return metadata

        parquet_path = Path(parsed_data_path)
        if parquet_path.exists():
            dataframe = pd.read_parquet(parquet_path)
            metadata.update(
                {
                    "total_rows": int(dataframe.shape[0]),
                    "total_columns": int(dataframe.shape[1]),
                    "column_names": [str(column) for column in dataframe.columns.tolist()],
                    "detected_dtypes": {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()},
                }
            )
        else:
            metadata.update(
                {
                    "total_rows": 0,
                    "total_columns": 0,
                    "column_names": [],
                    "detected_dtypes": {},
                }
            )
        return metadata
