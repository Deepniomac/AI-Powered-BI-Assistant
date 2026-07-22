from typing import Optional

from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """
    Structured validation issue entry.
    """

    severity: str
    type: str
    column: Optional[str] = None
    description: str
    affected_rows: list[int] | int | None = None
    recommendation: str
    count: Optional[int] = None


class ValidationSummary(BaseModel):
    """
    Summary block for a validation run.
    """

    status: str = Field(..., description="passed or failed")
    errors: int
    warnings: int


class ValidationReportPayload(BaseModel):
    """
    Root validation report payload returned by the validator.
    """

    summary: ValidationSummary
    issues: list[ValidationIssue]
