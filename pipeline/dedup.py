"""Deduplication filter: drops duplicate identical fare quotes within a time window."""
import time
from datetime import datetime
from typing import Dict
from loguru import logger
from pipeline.models import NormalizedFare

# In-memory deduplication cache storing {signature: timestamp_epoch}
_SEEN_CACHE: Dict[str, float] = {}


def generate_fare_signature(fare: NormalizedFare) -> str:
    """Generates a composite hash key for route, flight, date, and price."""
    fnum = getattr(fare, "flight_number", "") or ""
    return f"{fare.source}:{fare.route}:{fare.travel_date}:{fare.window}:{fnum}:{round(float(fare.price_inr), 2)}"


def is_duplicate(fare: NormalizedFare, window_seconds: float = 3600.0) -> bool:
    """Checks if identical fare (same route, date, flight, and price) was already recorded within window_seconds (default 1 hour).
    
    If price has changed, signature changes and the new fare is accepted immediately.
    """
    sig = generate_fare_signature(fare)
    now = time.time()

    if sig in _SEEN_CACHE:
        prev_time = _SEEN_CACHE[sig]
        if now - prev_time < window_seconds:
            logger.debug(f"[DEDUP] Dropping duplicate unchanged fare: {fare.route} {fare.flight_number} @ INR {fare.price_inr} (recorded {now - prev_time:.0f}s ago)")
            return True

    _SEEN_CACHE[sig] = now
    # Evict cache entries older than 2 hours to avoid memory growth
    if len(_SEEN_CACHE) > 5000:
        cutoff = now - 7200.0
        keys_to_remove = [k for k, ts in _SEEN_CACHE.items() if ts < cutoff]
        for k in keys_to_remove:
            _SEEN_CACHE.pop(k, None)

    return False


def clear_dedup_cache() -> None:
    _SEEN_CACHE.clear()
