"""Validation checks for statistical index reliability."""
from typing import Dict, Any, List
from loguru import logger


def validate_index_series(series_dict: Dict[str, Any]) -> bool:
    """Validates that computed APIx adheres to mathematical and statistical constraints."""
    values = series_dict.get("values", [])
    if not values:
        logger.error("[INDEX VALIDATION] Empty series values!")
        return False

    # 1. Base period check (first value in monthly baseline must be 100.0)
    if series_dict.get("frequency") == "monthly":
        if abs(values[0] - 100.0) > 0.05:
            logger.error(f"[INDEX VALIDATION] Base period is not 100.0 (got {values[0]})")
            return False

    # 2. Boundary sanity: domestic inflation index cannot be negative or absurdly high
    for val in values:
        if val < 40.0 or val > 350.0:
            logger.error(f"[INDEX VALIDATION] Implausible index value {val} detected!")
            return False

    # 3. Continuity check (no sudden 100% jumping between adjacent daily periods)
    for i in range(1, len(values)):
        step_change = abs(values[i] - values[i - 1]) / values[i - 1]
        if step_change > 0.50:  # 50% single-step jump is flagged for statistical investigation
            logger.warning(f"[INDEX VALIDATION] Severe step change between {values[i-1]} and {values[i]} ({step_change*100:.1f}%)")

    logger.info(f"[INDEX VALIDATION] Index series ({series_dict.get('frequency')}) successfully verified.")
    return True
