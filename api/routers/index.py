"""Index API router: serves daily, weekly, and monthly APIx series."""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from storage.redis_cache import RedisCache
from storage.snapshot import SnapshotStore
from index_engine.apix import APIxIndexEngine

router = APIRouter(prefix="/api", tags=["Index"])


@router.get("/index")
def get_index(frequency: str = Query("daily", description="daily, weekly, or monthly")):
    freq = frequency.lower().strip()
    if freq not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid frequency '{frequency}'. Must be one of: 'daily', 'weekly', 'monthly'"
        )

    cache = RedisCache()
    cached_val = cache.get_latest_index(freq)
    if cached_val:
        return cached_val

    # Compute on the fly if cache miss
    store = SnapshotStore()
    df = store.get_dataframe()
    if df.empty:
        return {
            "frequency": freq,
            "base_month": "2026-07",
            "base_value": 182320.0,
            "labels": ["2026-07"],
            "values": [100.0],
            "mom_pct": [0.0],
            "latest": 100.0,
            "change_pct": 0.0
        }

    engine = APIxIndexEngine(base_month="2026-07")
    if freq == "monthly":
        data = engine.compute_monthly_series(df)
    elif freq == "weekly":
        data = engine.compute_weekly_series(df)
    else:
        data = engine.compute_daily_series(df, days_limit=30)

    cache.set_latest_index(freq, data)
    return data


@router.get("/index/route/{route}")
def get_route_sub_index(route: str):
    """Computes specific route sub-index (e.g. DEL-BOM)."""
    clean_route = route.upper().strip()
    store = SnapshotStore()
    df = store.get_dataframe()
    if df.empty:
        raise HTTPException(status_code=503, detail="No fare data available.")

    route_df = df[df["route"] == clean_route]
    if route_df.empty:
        raise HTTPException(status_code=404, detail=f"No data for route {clean_route}")

    engine = APIxIndexEngine(base_month="2026-07")
    monthly = engine.compute_monthly_series(route_df)
    return {
        "route": clean_route,
        "monthly": monthly
    }
