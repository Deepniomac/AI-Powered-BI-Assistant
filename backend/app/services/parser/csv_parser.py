from pathlib import Path

import chardet
import pandas as pd

from app.models.report import Report
from app.services.parser.base_parser import BaseParser, ParserResult


class CsvParser(BaseParser):
    """
    Parser for CSV uploads with lightweight encoding detection.
    """

    def __init__(self, file_path: Path, report: Report):
        super().__init__(file_path, report)

    def parse(self) -> ParserResult:
        warnings: list[str] = []

        try:
            sample = self.file_path.read_bytes()[:65536]
            if b"\x00" in sample:
                return self._finalize_result(
                    None,
                    success=False,
                    errors=["Failed to parse CSV file: file contains binary null bytes"],
                )

            detected = chardet.detect(sample)
            encoding = detected.get("encoding") or "utf-8"

            try:
                dataframe = pd.read_csv(self.file_path, encoding=encoding)
            except UnicodeDecodeError:
                encoding = "latin-1"
                warnings.append("Primary encoding detection failed; CSV was read using latin-1 fallback")
                dataframe = pd.read_csv(self.file_path, encoding=encoding)

            return self._finalize_result(
                dataframe,
                {"encoding": encoding},
                success=True,
                warnings=warnings,
            )
        except Exception as exc:
            return self._finalize_result(
                None,
                success=False,
                errors=[f"Failed to parse CSV file: {exc}"],
                warnings=warnings,
            )
