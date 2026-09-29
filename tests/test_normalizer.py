"""Unit tests for pipeline.normalizer functions."""
import pytest
from pipeline.normalizer import (
    normalize_price,
    normalize_airport_code,
    normalize_date,
    normalize_quote
)


def test_normalize_price():
    assert normalize_price("₹6,442") == 6442.0
    assert normalize_price("INR 6,442.50") == 6442.50
    assert normalize_price(" 12500 ") == 12500.0
    assert normalize_price(5999) == 5999.0

    with pytest.raises(ValueError):
        normalize_price("INVALID")


def test_normalize_airport_code():
    assert normalize_airport_code("DEL") == "DEL"
    assert normalize_airport_code("del") == "DEL"
    assert normalize_airport_code("Mumbai") == "BOM"
    assert normalize_airport_code("Bengaluru") == "BLR"
    assert normalize_airport_code("New Delhi") == "DEL"
    assert normalize_airport_code("Calcutta") == "CCU"

    with pytest.raises(ValueError):
        normalize_airport_code("UnknownCity")


def test_normalize_date():
    assert normalize_date("2026-09-21") == "2026-09-21"
    assert normalize_date("21-09-2026") == "2026-09-21"
    assert normalize_date("21/09/2026") == "2026-09-21"
    assert normalize_date("21-Sep-2026") == "2026-09-21"

    with pytest.raises(ValueError):
        normalize_date("InvalidDateString")


def test_normalize_quote():
    raw = {
        "source": "indigo",
        "origin": "Mumbai",
        "destination": "Delhi",
        "travel_date": "21-Sep-2026",
        "window": "T+7",
        "price_total": "₹6,442"
    }
    fare = normalize_quote(raw)
    assert fare.source == "indigo"
    assert fare.origin == "BOM"
    assert fare.destination == "DEL"
    assert fare.route == "BOM-DEL"
    assert fare.travel_date == "2026-09-21"
    assert fare.price_inr == 6442.0
    assert fare.quality_flag == "ok"
