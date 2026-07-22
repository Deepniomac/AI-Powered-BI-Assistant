from pathlib import Path

from app.models.report import Report
from app.services.parser.base_parser import BaseParser, UnsupportedParser
from app.services.parser.csv_parser import CsvParser
from app.services.parser.excel_parser import ExcelParser
from app.services.parser.json_parser import JsonParser


def get_parser(report: Report, file_path: Path) -> BaseParser:
    """
    Selects the concrete parser based on the already-validated report file type.
    """
    file_type = (report.file_type or file_path.suffix.lstrip(".")).lower()

    if file_type == "csv":
        return CsvParser(file_path, report)
    if file_type in {"xlsx", "xls"}:
        return ExcelParser(file_path, report)
    if file_type == "json":
        return JsonParser(file_path, report)
    return UnsupportedParser(file_path, report)
