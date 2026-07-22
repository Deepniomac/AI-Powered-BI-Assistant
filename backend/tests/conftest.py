from datetime import datetime, timezone
from pathlib import Path
import sys

import pandas as pd
import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.report import Report


@pytest.fixture
def sample_report() -> Report:
    return Report(
        id=1,
        user_id=1,
        original_name="sample.csv",
        stored_name="stored-sample.csv",
        file_type="csv",
        file_size=128,
        upload_time=datetime.now(timezone.utc),
        status="Uploaded",
    )


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "revenue": [100, 150, None, -25],
            "quantity": [2, 2, "bad", 4],
            "sale_date": ["2026-01-01", "invalid", None, "2026-01-04"],
            "notes": ["ok", "  ", None, "ok"],
            "constant": ["A", "A", "A", "A"],
        }
    )
