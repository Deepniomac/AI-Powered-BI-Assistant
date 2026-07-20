from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    """
    API response schema for uploaded report metadata.
    """
    id: int
    original_name: str
    stored_name: str
    file_type: str
    file_size: int
    upload_time: datetime
    status: str

    model_config = {
        "from_attributes": True
    }


class DeleteReportResponse(BaseModel):
    """
    API response schema returned after a successful report deletion.
    """
    message: str
