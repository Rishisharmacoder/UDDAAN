"""Command-line runner for index computation and cache warming."""
import os
import pandas as pd
from loguru import logger
from storage.snapshot import SnapshotStore
from storage.redis_cache import RedisCache
from storage.db import DatabaseStore
from index_engine.apix import APIxIndexEngine
from index_engine.validation import validate_index_series


def run_index_computation():
    logger.info("[INDEX RUNNER] Triggering APIx Index Engine...")

    # Load data from snapshot CSV
    store = SnapshotStore()
    fares_df = store.get_dataframe()

    if fares_df.empty:
        logger.warning("[INDEX RUNNER] No fare data available in snapshot. Generating initial seed...")
        from scripts.seed_data import generate_seed_data
        generate_seed_data()
        fares_df = store.get_dataframe()

    logger.info(f"[INDEX RUNNER] Ingested {len(fares_df)} historical fare observations.")

    engine = APIxIndexEngine(base_month="2026-07")
    cache = RedisCache()
    db = DatabaseStore()

    # 1. Compute Monthly APIx Series
    monthly = engine.compute_monthly_series(fares_df)
    validate_index_series(monthly)
    cache.set_latest_index("monthly", monthly)
    logger.info(f"[INDEX RUNNER] Monthly APIx: {list(zip(monthly['labels'], monthly['values']))}")

    # 2. Compute Daily APIx Series
    daily = engine.compute_daily_series(fares_df, days_limit=30)
    validate_index_series(daily)
    cache.set_latest_index("daily", daily)
    logger.info(f"[INDEX RUNNER] Daily APIx (Latest: {daily['latest']}, MoM%: {daily['change_pct']}%)")

    # 3. Compute Weekly APIx Series
    weekly = engine.compute_weekly_series(fares_df)
    validate_index_series(weekly)
    cache.set_latest_index("weekly", weekly)

    # Persist to database if reachable
    if db.is_connected:
        for idx, month in enumerate(monthly["labels"]):
            db.upsert_index_value("monthly", month, monthly["values"][idx], monthly["mom_pct"][idx])
        for idx, day in enumerate(daily["labels"]):
            db.upsert_index_value("daily", day, daily["values"][idx], None)
        logger.info("[INDEX RUNNER] Persisted index series to PostgreSQL.")

    print("\n" + "=" * 50)
    print("  APIx INDEX COMPUTATION COMPLETE")
    print(f"  Base Month (100.0) : {monthly['base_month']}")
    print(f"  Latest Monthly     : {monthly['latest']} (Change: {monthly['change_pct']:+.2f}%)")
    print(f"  Latest Daily       : {daily['latest']} (Change: {daily['change_pct']:+.2f}%)")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_index_computation()
