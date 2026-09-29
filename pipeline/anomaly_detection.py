"""Anomaly Detection using Median Absolute Deviation (MAD) and strict sanity boundaries."""
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
from loguru import logger
from pipeline.models import NormalizedFare

MIN_VALID_PRICE = 500.0
MAX_VALID_PRICE = 100000.0
MAD_THRESHOLD = 3.0


def check_single_fare_sanity(fare: NormalizedFare) -> NormalizedFare:
    """Hard boundary check for CAPTCHA bypass failures, price bounds, and schedule consistency."""
    if fare.price_inr < MIN_VALID_PRICE or fare.price_inr > MAX_VALID_PRICE:
        logger.warning(f"[ANOMALY] Out-of-bounds fare ₹{fare.price_inr} rejected for {fare.route} ({fare.source})")
        fare.quality_flag = "rejected"
        return fare

    # Official DGCA Flight Schedule Consistency Validation
    from pipeline.flight_schedules import validate_flight_schedule, get_verified_flight_number
    if not fare.flight_number:
        fare.flight_number = get_verified_flight_number(fare.route, fare.airline_code)
        fare.flight_validation = "verified"
    else:
        status = validate_flight_schedule(fare.route, fare.flight_number)
        fare.flight_validation = status
        if status == "invalid":
            logger.warning(f"[SCHEDULE AUDIT] Flight '{fare.flight_number}' not on published schedule for {fare.route}. Flagged for review.")
            fare.quality_flag = "flagged"

    return fare


def detect_batch_anomalies(fares: List[NormalizedFare], z_threshold: float = MAD_THRESHOLD) -> List[NormalizedFare]:
    """Applies Median Absolute Deviation (MAD) modified z-score outlier detection grouped by (route, window)."""
    # 1. First pass: Apply hard boundary validation
    for fare in fares:
        check_single_fare_sanity(fare)

    # 2. Group prices by (route, window)
    groups: Dict[Tuple[str, str], List[NormalizedFare]] = defaultdict(list)
    for fare in fares:
        if fare.quality_flag != "rejected":
            groups[(fare.route, fare.window)].append(fare)

    # 3. Compute MAD per cohort
    for (route, window), cohort in groups.items():
        if len(cohort) < 3:
            # Insufficient sample size for statistical MAD; rely on sanity bounds
            continue

        prices = np.array([f.price_inr for f in cohort], dtype=float)
        median = np.median(prices)
        abs_dev = np.abs(prices - median)
        mad = np.median(abs_dev)

        if mad == 0:
            # Highly uniform pricing; check for severe deviations from median
            for f in cohort:
                if abs(f.price_inr - median) / (median + 1e-6) > 0.8:
                    f.quality_flag = "flagged"
                    logger.warning(f"[ANOMALY] Flagged fare ₹{f.price_inr} against invariant median ₹{median}")
            continue

        # Standard modified Z-score using 0.6745 consistency constant
        mod_z = 0.6745 * abs_dev / mad

        for idx, z_val in enumerate(mod_z):
            if z_val > z_threshold:
                target_fare = cohort[idx]
                target_fare.quality_flag = "flagged"
                logger.warning(f"[ANOMALY] Statistical outlier: ₹{target_fare.price_inr} for {route} {window} (MAD z={z_val:.2f})")

    return fares
