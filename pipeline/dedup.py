"""Deduplication filter: drops duplicate fare quotes within 60 minutes."""
from datetime import datetime
from typing import Dict, Set, Optional
from loguru import logger
from pipeline.models import NormalizedFare

# In-memory deduplication set storing (signature, timestamp_epoch)
_SEEN_CACHE: Dict[str, float] = {}


def generate_fare_signature(fare: NormalizedFare) -> str:
    return f"{fare.source}:{fare.origin}:{fare.destination}:{fare.travel_date}:{fare.window}:{fare.airline_code}"


def is_duplicate(fare: NormalizedFare, window_seconds: float = 3600.0) -> bool:
    """Checks if identical fare was already captured within window_seconds (default 1 hour)."""
    sig = generate_fare_signature(fare)
    try:
        current_time = datetime.fromisoformat(fare.scraped_at).timestamp()
    except Exception:
        current_time = datetime.utcnow().timestamp()

    if sig in _SEEN_CACHE:
        prev_time = _SEEN_CACHE[sig]
        if current_time - prev_time < window_seconds:
            logger.debug(f"[DEDUP] Dropping duplicate fare quote for {sig} (elapsed: {current_time - prev_time:.0f}s)")
            return True

    _SEEN_CACHE[sig] = current_time
    return False


def clear_dedup_cache() -> None:
    _SEEN_CACHE.clear()
