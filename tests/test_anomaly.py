"""Unit tests for pipeline.anomaly_detection functions."""
import pytest
from pipeline.models import NormalizedFare
from pipeline.anomaly_detection import detect_batch_anomalies, check_single_fare_sanity


def create_sample_fare(price: float, route: str = "DEL-BOM", window: str = "T+7") -> NormalizedFare:
    orig, dest = route.split("-")
    return NormalizedFare(
        source="indigo",
        source_type="airline",
        origin=orig,
        destination=dest,
        route=route,
        travel_date="2026-10-01",
        window=window,
        price_inr=price,
        scraped_at="2026-09-21T10:00:00"
    )


def test_hard_boundary_rejection():
    # Below min valid boundary (₹500)
    cheap_fare = create_sample_fare(99.0)
    check_single_fare_sanity(cheap_fare)
    assert cheap_fare.quality_flag == "rejected"

    # Extreme CAPTCHA garbage e.g. ₹99,99,999
    huge_fare = create_sample_fare(9999999.0)
    check_single_fare_sanity(huge_fare)
    assert huge_fare.quality_flag == "rejected"

    # Normal valid boundary
    valid_fare = create_sample_fare(5400.0)
    check_single_fare_sanity(valid_fare)
    assert valid_fare.quality_flag == "ok"


def test_mad_zscore_outlier_detection():
    # Cohort of normal fares around ₹6,000
    normal_prices = [5900.0, 6000.0, 6100.0, 6050.0, 5950.0, 6020.0]
    fares = [create_sample_fare(p) for p in normal_prices]

    # Inject high anomaly (e.g. ₹28,000 surge)
    outlier = create_sample_fare(28000.0)
    fares.append(outlier)

    results = detect_batch_anomalies(fares, z_threshold=3.0)
    assert outlier.quality_flag == "flagged"

    # Verify normal fares remain "ok"
    ok_count = sum(1 for f in results if f.quality_flag == "ok")
    assert ok_count == len(normal_prices)
