from datetime import datetime, timezone
from pathlib import Path
import shutil
import uuid

import pandas as pd

from app.models.report import Report
from app.services.parser.csv_parser import CsvParser
from app.services.parser.excel_parser import ExcelParser
from app.services.parser.json_parser import JsonParser
from app.services.parser.parser_factory import get_parser


TEST_TMP_ROOT = Path(__file__).resolve().parents[1] / '.test_tmp_files'
TEST_TMP_ROOT.mkdir(exist_ok=True)


def build_report(file_type: str, name: str) -> Report:
    return Report(
        id=1,
        user_id=1,
        original_name=name,
        stored_name=f"stored-{name}",
        file_type=file_type,
        file_size=256,
        upload_time=datetime.now(timezone.utc),
        status="Uploaded",
    )


def make_case_dir() -> Path:
    case_dir = TEST_TMP_ROOT / uuid.uuid4().hex
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


def cleanup_case_dir(case_dir: Path) -> None:
    if case_dir.exists():
        shutil.rmtree(case_dir, ignore_errors=True)


def test_csv_parser_success():
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'report.csv'
        file_path.write_text('col1,col2\n1,2\n3,4\n', encoding='utf-8')
        parser = CsvParser(file_path, build_report('csv', 'report.csv'))

        result = parser.parse()

        assert result['success'] is True
        assert result['metadata']['encoding'].lower() in {'ascii', 'utf-8', 'utf_8'}
        assert result['metadata']['total_rows'] == 2
    finally:
        cleanup_case_dir(case_dir)


def test_csv_parser_corrupted_file():
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'bad.csv'
        file_path.write_bytes(b'\x00\x00\x00')
        parser = CsvParser(file_path, build_report('csv', 'bad.csv'))

        result = parser.parse()

        assert result['success'] is False
        assert result['errors']
    finally:
        cleanup_case_dir(case_dir)


def test_xlsx_parser_success():
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'report.xlsx'
        dataframe = pd.DataFrame({'name': ['A', 'B'], 'value': [1, 2]})
        dataframe.to_excel(file_path, index=False)
        parser = ExcelParser(file_path, build_report('xlsx', 'report.xlsx'))

        result = parser.parse()

        assert result['success'] is True
        assert result['metadata']['sheet_name'] == 'Sheet1'
        assert result['metadata']['total_columns'] == 2
    finally:
        cleanup_case_dir(case_dir)


def test_xls_parser_success_with_monkeypatch(monkeypatch):
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'legacy.xls'
        file_path.write_bytes(b'legacy')

        class FakeWorkbook:
            sheet_names = ['LegacySheet']

            def parse(self, sheet_name):
                assert sheet_name == 'LegacySheet'
                return pd.DataFrame({'amount': [10, 20]})

        monkeypatch.setattr(pd, 'ExcelFile', lambda *args, **kwargs: FakeWorkbook())
        parser = ExcelParser(file_path, build_report('xls', 'legacy.xls'))

        result = parser.parse()

        assert result['success'] is True
        assert result['metadata']['sheet_name'] == 'LegacySheet'
    finally:
        cleanup_case_dir(case_dir)


def test_json_parser_success_with_nested_warning():
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'report.json'
        file_path.write_text('[{"user":"A","metrics":{"revenue":100}},{"user":"B","metrics":{"revenue":200}}]', encoding='utf-8')
        parser = JsonParser(file_path, build_report('json', 'report.json'))

        result = parser.parse()

        assert result['success'] is True
        assert 'metrics.revenue' in result['metadata']['column_names']
        assert result['warnings']
    finally:
        cleanup_case_dir(case_dir)


def test_parser_factory_returns_unsupported_parser_for_pdf():
    case_dir = make_case_dir()
    try:
        file_path = case_dir / 'report.pdf'
        file_path.write_bytes(b'%PDF-1.4')
        parser = get_parser(build_report('pdf', 'report.pdf'), file_path)

        result = parser.parse()

        assert result['success'] is False
        assert 'unsupported for parsing' in result['errors'][0].lower()
    finally:
        cleanup_case_dir(case_dir)
