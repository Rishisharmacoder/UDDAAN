"""Golden test for APIx Laspeyres Index computation."""
import os
import pytest
import pandas as pd
from index_engine.apix import APIxIndexEngine
from index_engine.validation import validate_index_series

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "golden_fares.csv")


def test_golden_apix_monthly_index():
    assert os.path.exists(FIXTURE_PATH), f"Golden fixture not found at {FIXTURE_PATH}"
    df = pd.read_csv(FIXTURE_PATH)
    assert not df.empty, "Golden fares fixture is empty!"

    engine = APIxIndexEngine(base_month="2026-07")
    result = engine.compute_monthly_series(df)

    assert validate_index_series(result) is True
    assert result["base_month"] == "2026-07"

    labels = result["labels"]
    values = result["values"]

    # Check that labels contain 2026-07, 2026-08, 2026-09
    assert "2026-07" in labels
    assert "2026-08" in labels
    assert "2026-09" in labels

    jul_idx = values[labels.index("2026-07")]
    aug_idx = values[labels.index("2026-08")]
    sep_idx = values[labels.index("2026-09")]

    # Base month must equal 100.00
    assert abs(jul_idx - 100.00) < 0.05

    # August should reflect ~104.79 (monsoon/school trend, ±1.0 tolerance for sampling jitter)
    assert 103.5 <= aug_idx <= 106.0

    # September should reflect ~105.64 (festival early trend, ±1.0 tolerance)
    assert 104.5 <= sep_idx <= 107.0

    # Monotonic inflation progression
    assert aug_idx > jul_idx
    assert sep_idx >= aug_idx


def test_apix_daily_series():
    df = pd.read_csv(FIXTURE_PATH)
    engine = APIxIndexEngine(base_month="2026-07")
    daily = engine.compute_daily_series(df, days_limit=14)

    assert validate_index_series(daily) is True
    assert len(daily["labels"]) == 14
    assert len(daily["values"]) == 14
    for val in daily["values"]:
        assert 90.0 <= val <= 130.0
