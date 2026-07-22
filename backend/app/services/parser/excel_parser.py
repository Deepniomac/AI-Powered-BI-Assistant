from pathlib import Path

import pandas as pd

from app.models.report import Report
from app.services.parser.base_parser import BaseParser, ParserResult


class ExcelParser(BaseParser):
    """
    Parser for XLSX and legacy XLS workbooks.
    """

    def __init__(self, file_path: Path, report: Report):
        super().__init__(file_path, report)

    def parse(self) -> ParserResult:
        warnings: list[str] = []
        file_type = (self.report.file_type or self.file_path.suffix.lstrip(".")).lower()
        engine = "xlrd" if file_type == "xls" else "openpyxl"

        try:
            workbook = pd.ExcelFile(self.file_path, engine=engine)
            if not workbook.sheet_names:
                return self._finalize_result(
                    None,
                    {"sheet_name": None},
                    success=False,
                    errors=["Excel workbook does not contain any sheets"],
                )

            sheet_name = workbook.sheet_names[0]
            if len(workbook.sheet_names) > 1:
                warnings.append("Workbook contains multiple sheets; only the first sheet was parsed")

            dataframe = workbook.parse(sheet_name=sheet_name)
            return self._finalize_result(
                dataframe,
                {"sheet_name": sheet_name},
                success=True,
                warnings=warnings,
            )
        except Exception as exc:
            return self._finalize_result(
                None,
                {"sheet_name": None},
                success=False,
                errors=[f"Failed to parse Excel workbook: {exc}"],
                warnings=warnings,
            )
