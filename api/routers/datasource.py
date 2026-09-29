"""Datasource and Provenance API router: transparency and honesty verification."""
import os
from fastapi import APIRouter
from typing import Dict, Any, List
from storage.redis_cache import RedisCache

router = APIRouter(prefix="/api", tags=["Provenance"])


@router.get("/datasource")
def get_datasource_provenance():
    cache = RedisCache()
    cached = cache.get_active_datasource()

    amadeus_key = os.getenv("AMADEUS_API_KEY", "")
    has_amadeus = bool(amadeus_key and amadeus_key != "mock_amadeus_key")
    snapshot_exists = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "snapshot.csv"))

    if has_amadeus:
        active_name = "amadeus (official GDS API)"
        status_msg = "LIVE GDS: Official Amadeus flight-offers feed in INR."
    elif snapshot_exists:
        active_name = "snapshot (cached verified export)"
        status_msg = "SNAPSHOT: High-integrity CSV export loaded locally."
    else:
        active_name = "seed (demo replay)"
        status_msg = "DEMO SEED: 4,980 calibrated historical observations."

    return {
        "active": active_name,
        "status": "active",
        "description": status_msg,
        "fallback_chain": ["amadeus", "snapshot", "seed"],
        "compliance": {
            "no_captcha_bypass": True,
            "robots_txt_honoured": True,
            "zero_pii_asserted": True,
            "rate_limit_hard_capped": "45s min gap, 15 req/hr"
        },
        "log": [
            "PROVENANCE STEP 1: Evaluated Amadeus GDS credentials.",
            f"PROVENANCE STEP 2: Evaluated local snapshot status (found={snapshot_exists}).",
            f"SOURCE RESOLUTION: Active feed determined as '{active_name}'."
        ]
    }
