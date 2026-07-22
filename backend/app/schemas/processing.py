from typing import Any

from pydantic import BaseModel

from app.services.validation.validation_models import ValidationReportPayload


class ProcessingResponse(BaseModel):
    """
    API response schema for processing results.
    """

    processing_log_id: int
    report_id: int
    status: str
    validation_status: str
    parsed_data_path: str | None = None
    metadata: dict[str, Any]
    validation_report: ValidationReportPayload
    message: str
    error_count: int
    warning_count: int
