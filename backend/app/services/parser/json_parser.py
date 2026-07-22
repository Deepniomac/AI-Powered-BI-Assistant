import json
from pathlib import Path
from typing import Any

import chardet
import pandas as pd

from app.models.report import Report
from app.services.parser.base_parser import BaseParser, ParserResult


class JsonParser(BaseParser):
    """
    Parser for JSON uploads with flattening-oriented normalization.
    """

    def __init__(self, file_path: Path, report: Report):
        super().__init__(file_path, report)

    def parse(self) -> ParserResult:
        warnings: list[str] = []

        try:
            sample = self.file_path.read_bytes()[:65536]
            detected = chardet.detect(sample)
            encoding = detected.get("encoding") or "utf-8"

            with self.file_path.open("r", encoding=encoding) as json_file:
                payload = json.load(json_file)

            dataframe = self._normalize_payload(payload, warnings)
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
                errors=[f"Failed to parse JSON file: {exc}"],
                warnings=warnings,
            )

    def _normalize_payload(self, payload: Any, warnings: list[str]) -> pd.DataFrame:
        if isinstance(payload, list):
            if not payload:
                warnings.append("JSON payload is an empty list")
                return pd.DataFrame()

            if all(isinstance(item, dict) for item in payload):
                if any(self._contains_nested_values(item) for item in payload):
                    warnings.append("Nested JSON fields were flattened using dotted column names where possible")
                return pd.json_normalize(payload, sep=".")

            warnings.append("JSON list items were not object records; values were stored in a single 'value' column")
            return pd.DataFrame({"value": payload})

        if isinstance(payload, dict):
            if self._contains_nested_values(payload):
                warnings.append("JSON root object was flattened into a single-row dataset")
            else:
                warnings.append("JSON root object was converted into a single-row dataset")
            return pd.json_normalize(payload, sep=".")

        warnings.append("JSON payload was scalar; wrapped into a single-row dataset")
        return pd.DataFrame({"value": [payload]})

    @staticmethod
    def _contains_nested_values(record: dict[str, Any]) -> bool:
        return any(isinstance(value, (dict, list)) for value in record.values())
