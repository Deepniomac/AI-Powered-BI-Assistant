from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd

from app.models.report import Report

ParserResult = dict[str, Any]


class BaseParser(ABC):
    """
    Abstract parser contract used by the processing engine.
    """

    def __init__(self, file_path: Path, report: Report):
        self.file_path = file_path
        self.report = report

    @abstractmethod
    def parse(self) -> ParserResult:
        """
        Parses the target file and returns a standardized parser result.
        """

    def _base_metadata(self) -> dict[str, Any]:
        extension = self.file_path.suffix.lower().lstrip(".")
        return {
            "filename": self.report.original_name,
            "extension": extension,
            "file_size": self.report.file_size,
            "upload_timestamp": self.report.upload_time.isoformat(),
        }

    def _finalize_result(
        self,
        dataframe: pd.DataFrame | None,
        metadata: dict[str, Any] | None = None,
        *,
        success: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> ParserResult:
        final_metadata = self._base_metadata()
        if metadata:
            final_metadata.update(metadata)

        if dataframe is not None:
            final_metadata.update(
                {
                    "total_rows": int(dataframe.shape[0]),
                    "total_columns": int(dataframe.shape[1]),
                    "column_names": [str(column) for column in dataframe.columns.tolist()],
                    "detected_dtypes": {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()},
                }
            )
        else:
            final_metadata.setdefault("total_rows", 0)
            final_metadata.setdefault("total_columns", 0)
            final_metadata.setdefault("column_names", [])
            final_metadata.setdefault("detected_dtypes", {})

        return {
            "success": success,
            "dataframe": dataframe,
            "metadata": final_metadata,
            "errors": errors or [],
            "warnings": warnings or [],
        }


class UnsupportedParser(BaseParser):
    """
    Parser used for uploaded types that are not parsable in this phase.
    """

    def parse(self) -> ParserResult:
        file_type = (self.report.file_type or self.file_path.suffix.lstrip(".")).lower()
        message = f"{file_type.upper()} files are unsupported for parsing in this phase"
        return self._finalize_result(
            None,
            success=False,
            errors=[message],
            warnings=[],
        )
