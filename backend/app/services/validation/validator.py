import re
from typing import Iterable

import pandas as pd

from app.services.validation.validation_models import ValidationIssue, ValidationReportPayload, ValidationSummary

PRICE_COLUMN_PATTERN = re.compile(r"(price|cost|amount|revenue|total)", re.IGNORECASE)
QUANTITY_COLUMN_PATTERN = re.compile(r"(qty|quantity|count|units)", re.IGNORECASE)
DATE_COLUMN_PATTERN = re.compile(r"(date|time|day|month|year)", re.IGNORECASE)
NUMERIC_EXPECTED_PATTERN = re.compile(r"(price|cost|amount|revenue|total|qty|quantity|count|units)", re.IGNORECASE)


class DatasetValidator:
    """
    Applies reusable dataset validation rules to parsed tabular data.
    """

    def validate(self, dataframe: pd.DataFrame) -> ValidationReportPayload:
        issues: list[ValidationIssue] = []

        if dataframe.empty or dataframe.shape[1] == 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    type="empty_dataset",
                    column=None,
                    description="The dataset does not contain any rows or columns to process",
                    affected_rows=0,
                    recommendation="Upload a report that contains tabular data",
                    count=0,
                )
            )
            return self._build_report(issues)

        issues.extend(self._check_duplicate_columns(dataframe))
        issues.extend(self._check_missing_values(dataframe))
        issues.extend(self._check_duplicate_rows(dataframe))
        issues.extend(self._check_empty_columns(dataframe))
        issues.extend(self._check_whitespace_only_columns(dataframe))
        issues.extend(self._check_blank_rows(dataframe))
        issues.extend(self._check_mixed_data_types(dataframe))
        issues.extend(self._check_invalid_numeric_columns(dataframe))
        issues.extend(self._check_invalid_dates(dataframe))
        issues.extend(self._check_negative_values(dataframe))
        issues.extend(self._check_null_percentage(dataframe))
        issues.extend(self._check_single_repeated_values(dataframe))
        return self._build_report(issues)

    def _build_report(self, issues: list[ValidationIssue]) -> ValidationReportPayload:
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

    def _check_missing_values(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            missing_mask = dataframe[column].isna()
            missing_count = int(missing_mask.sum())
            if missing_count > 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="missing_values",
                        column=str(column),
                        description=f"Column '{column}' contains {missing_count} missing values",
                        affected_rows=self._compress_rows(dataframe.index[missing_mask].tolist()),
                        recommendation="Fill missing values or remove incomplete rows before downstream analysis",
                        count=missing_count,
                    )
                )
        return issues

    def _check_duplicate_rows(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        duplicate_mask = dataframe.duplicated(keep=False)
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count == 0:
            return []

        return [
            ValidationIssue(
                severity="warning",
                type="duplicate_rows",
                column=None,
                description=f"Dataset contains {duplicate_count} duplicated rows",
                affected_rows=self._compress_rows(dataframe.index[duplicate_mask].tolist()),
                recommendation="Review and deduplicate repeated rows where appropriate",
                count=duplicate_count,
            )
        ]

    def _check_duplicate_columns(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        duplicates = dataframe.columns[dataframe.columns.duplicated()].tolist()
        if not duplicates:
            return []

        return [
            ValidationIssue(
                severity="error",
                type="duplicate_columns",
                column=", ".join(str(column) for column in duplicates),
                description=f"Dataset contains duplicate column names: {', '.join(str(column) for column in duplicates)}",
                affected_rows=None,
                recommendation="Rename duplicate columns before mapping the dataset schema",
                count=len(duplicates),
            )
        ]

    def _check_empty_columns(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            series = dataframe[column]
            normalized = series.map(self._normalize_string)
            if normalized.isna().all():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        type="empty_column",
                        column=str(column),
                        description=f"Column '{column}' is entirely empty",
                        affected_rows=int(len(series)),
                        recommendation="Remove empty columns or populate them before continuing",
                        count=int(len(series)),
                    )
                )
        return issues

    def _check_whitespace_only_columns(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            if not pd.api.types.is_object_dtype(dataframe[column]) and not pd.api.types.is_string_dtype(dataframe[column]):
                continue

            whitespace_mask = dataframe[column].fillna("").map(lambda value: isinstance(value, str) and value.strip() == "")
            whitespace_count = int(whitespace_mask.sum())
            if whitespace_count > 0 and whitespace_count != len(dataframe[column]):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="whitespace_only_values",
                        column=str(column),
                        description=f"Column '{column}' contains {whitespace_count} whitespace-only values",
                        affected_rows=self._compress_rows(dataframe.index[whitespace_mask].tolist()),
                        recommendation="Trim and clean whitespace-only values before schema mapping",
                        count=whitespace_count,
                    )
                )
        return issues

    def _check_blank_rows(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        normalized = dataframe.map(self._normalize_string)
        blank_row_mask = normalized.isna().all(axis=1)
        blank_row_count = int(blank_row_mask.sum())
        if blank_row_count == 0:
            return []

        return [
            ValidationIssue(
                severity="warning",
                type="blank_rows",
                column=None,
                description=f"Dataset contains {blank_row_count} fully blank rows",
                affected_rows=self._compress_rows(dataframe.index[blank_row_mask].tolist()),
                recommendation="Remove unexpected blank rows before cleaning or aggregation",
                count=blank_row_count,
            )
        ]

    def _check_mixed_data_types(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            series = dataframe[column].dropna()
            if series.empty:
                continue

            observed_types = {type(value).__name__ for value in series.tolist()}
            if len(observed_types) > 1:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="mixed_datatypes",
                        column=str(column),
                        description=f"Column '{column}' contains mixed data types: {', '.join(sorted(observed_types))}",
                        affected_rows=int(len(series)),
                        recommendation="Standardize values in this column to a single consistent type",
                        count=len(observed_types),
                    )
                )
        return issues

    def _check_invalid_numeric_columns(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            if not NUMERIC_EXPECTED_PATTERN.search(str(column)):
                continue

            series = dataframe[column]
            normalized = series.map(self._normalize_string)
            non_blank_mask = normalized.notna()
            if not non_blank_mask.any():
                continue

            numeric_series = pd.to_numeric(series, errors="coerce")
            invalid_mask = non_blank_mask & numeric_series.isna()
            invalid_count = int(invalid_mask.sum())
            if invalid_count > 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="invalid_numeric_values",
                        column=str(column),
                        description=f"Column '{column}' contains {invalid_count} values that could not be interpreted as numbers",
                        affected_rows=self._compress_rows(dataframe.index[invalid_mask].tolist()),
                        recommendation="Clean non-numeric values before running KPI or aggregation logic",
                        count=invalid_count,
                    )
                )
        return issues

    def _check_invalid_dates(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            if not DATE_COLUMN_PATTERN.search(str(column)):
                continue

            series = dataframe[column]
            normalized = series.map(self._normalize_string)
            non_blank_mask = normalized.notna()
            if not non_blank_mask.any():
                continue

            parsed_dates = pd.to_datetime(series, errors="coerce")
            invalid_mask = non_blank_mask & parsed_dates.isna()
            invalid_count = int(invalid_mask.sum())
            if invalid_count > 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="invalid_dates",
                        column=str(column),
                        description=f"Column '{column}' contains {invalid_count} values that could not be parsed as dates",
                        affected_rows=self._compress_rows(dataframe.index[invalid_mask].tolist()),
                        recommendation="Normalize the date format before time-based analysis",
                        count=invalid_count,
                    )
                )
        return issues

    def _check_negative_values(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            column_name = str(column)
            if not PRICE_COLUMN_PATTERN.search(column_name) and not QUANTITY_COLUMN_PATTERN.search(column_name):
                continue

            numeric_series = pd.to_numeric(dataframe[column], errors="coerce")
            negative_mask = numeric_series < 0
            negative_count = int(negative_mask.sum())
            if negative_count > 0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="negative_values",
                        column=column_name,
                        description=f"Column '{column_name}' contains {negative_count} negative values",
                        affected_rows=self._compress_rows(dataframe.index[negative_mask].tolist()),
                        recommendation="Verify whether negative values are valid for this business metric",
                        count=negative_count,
                    )
                )
        return issues

    def _check_null_percentage(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            null_percentage = float(dataframe[column].isna().mean() * 100)
            if null_percentage >= 20.0:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="high_null_percentage",
                        column=str(column),
                        description=f"Column '{column}' has a null percentage of {null_percentage:.2f}%",
                        affected_rows=int(dataframe[column].isna().sum()),
                        recommendation="Assess whether this column should be imputed, dropped, or remapped",
                        count=int(dataframe[column].isna().sum()),
                    )
                )
        return issues

    def _check_single_repeated_values(self, dataframe: pd.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for column in dataframe.columns:
            non_null = dataframe[column].dropna()
            if len(non_null) > 1 and non_null.nunique(dropna=True) == 1:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        type="single_repeated_value",
                        column=str(column),
                        description=f"Column '{column}' contains the same repeated value across all non-null rows",
                        affected_rows=int(len(non_null)),
                        recommendation="Verify whether this column carries useful signal for downstream analytics",
                        count=1,
                    )
                )
        return issues

    @staticmethod
    def _normalize_string(value: object) -> object:
        if pd.isna(value):
            return pd.NA
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else pd.NA
        return value

    @staticmethod
    def _compress_rows(rows: Iterable[int]) -> list[int] | int:
        row_list = [int(row) for row in rows]
        if len(row_list) <= 25:
            return row_list
        return len(row_list)
