import pandas as pd

from app.services.validation.validator import DatasetValidator


def test_validator_reports_expected_issue_categories(sample_dataframe):
    validator = DatasetValidator()

    report = validator.validate(sample_dataframe)
    issue_types = {issue.type for issue in report.issues}

    assert report.summary.warnings >= 1
    assert "missing_values" in issue_types
    assert "invalid_numeric_values" in issue_types
    assert "invalid_dates" in issue_types
    assert "negative_values" in issue_types
    assert "single_repeated_value" in issue_types


def test_validator_detects_duplicate_rows_and_blank_rows():
    dataframe = pd.DataFrame(
        {
            "product": ["A", "A", None],
            "amount": [10, 10, None],
        }
    )
    dataframe = pd.concat([dataframe, dataframe.iloc[[0]]], ignore_index=True)
    validator = DatasetValidator()

    report = validator.validate(dataframe)
    issue_types = {issue.type for issue in report.issues}

    assert "duplicate_rows" in issue_types


def test_validator_flags_empty_dataset():
    validator = DatasetValidator()

    report = validator.validate(pd.DataFrame())

    assert report.summary.status == "failed"
    assert report.summary.errors == 1
    assert report.issues[0].type == "empty_dataset"


def test_validator_detects_empty_and_whitespace_columns():
    dataframe = pd.DataFrame(
        {
            "empty_col": [None, None, None],
            "notes": [" ", "filled", "\t"],
        }
    )
    validator = DatasetValidator()

    report = validator.validate(dataframe)
    issue_types = {issue.type for issue in report.issues}

    assert "empty_column" in issue_types
    assert "whitespace_only_values" in issue_types
