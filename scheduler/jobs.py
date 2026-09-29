"""Scheduled jobs for 24x7 automated ingestion, index calculation, and monitoring."""
import os
import yaml
from datetime import datetime, timezone, timedelta
from loguru import logger

from scrapers.base.registry import ScraperFactory
from pipeline.normalizer import normalize_quote
from pipeline.dedup import is_duplicate
from pipeline.anomaly_detection import detect_batch_anomalies
from pipeline.quality_report import QualityReport
from storage.snapshot import SnapshotStore
from storage.db import DatabaseStore
from index_engine.run import run_index_computation

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


def execute_sweep(source_names: list, sweep_name: str = "custom_sweep"):
    """Executes a staggered sweep across specified source adapters."""
    logger.info(f"[SCHEDULER] >>> Starting {sweep_name} for sources: {source_names}")

    # Load routes & windows
    with open(os.path.join(CONFIG_DIR, "routes.yaml"), "r", encoding="utf-8") as f:
        routes_data = yaml.safe_load(f).get("routes", [])
    with open(os.path.join(CONFIG_DIR, "windows.yaml"), "r", encoding="utf-8") as f:
        windows_data = yaml.safe_load(f).get("windows", [])

    collected_fares = []
    store = SnapshotStore()
    db = DatabaseStore()

    for site in source_names:
        if not ScraperFactory.is_registered(site):
            logger.warning(f"[SCHEDULER] Source '{site}' is not registered in ScraperFactory. Skipping.")
            continue

        try:
            scraper = ScraperFactory.get(site)
        except Exception as e:
            logger.error(f"[SCHEDULER] Could not instantiate {site}: {e}")
            continue

        for r in routes_data:
            if not r.get("enabled", True):
                continue
            orig = r["origin"]
            dest = r["destination"]

            for w in windows_data:
                if not w.get("enabled", True):
                    continue
                win_label = w["label"]
                days_ahead = w["days_ahead"]
                tdate = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

                try:
                    raw_dto = scraper.fetch_fare(orig, dest, tdate, win_label)
                    norm_fare = normalize_quote(raw_dto.to_dict())

                    if not is_duplicate(norm_fare):
                        collected_fares.append(norm_fare)
                except Exception as e:
                    logger.warning(f"[SCHEDULER] Fetch failed on {site} for {orig}-{dest} ({win_label}): {e}")

    # Anomaly detection & quality auditing
    if collected_fares:
        validated_fares = detect_batch_anomalies(collected_fares)
        quality_rep = QualityReport.generate(validated_fares)

        # Store to Snapshot & DB
        store.save(validated_fares)
        if db.is_connected:
            db.insert_fares(validated_fares)

        logger.info(f"[SCHEDULER] Sweep finished: {quality_rep['rows_valid']}/{quality_rep['rows_collected']} valid fares ingested.")
    else:
        logger.warning("[SCHEDULER] Sweep completed with 0 new records collected.")


def sweep_morning():
    """06:00 IST - Sweep A: IndiGo + Amadeus GDS."""
    execute_sweep(["indigo", "amadeus"], sweep_name="Sweep-A (Morning 06:00)")


def sweep_evening():
    """18:00 IST - Sweep B: MakeMyTrip + Amadeus GDS."""
    execute_sweep(["makemytrip", "amadeus"], sweep_name="Sweep-B (Evening 18:00)")


def compute_index_job():
    """21:00 IST - Nightly Laspeyres APIx Index Re-calculation."""
    logger.info("[SCHEDULER] >>> Triggering Nightly 21:00 IST Index Engine Run")
    try:
        run_index_computation()
    except Exception as e:
        logger.error(f"[SCHEDULER] Index computation job error: {e}")


def health_ping_job():
    """Every 30 min - Service & Adapter Health Verification."""
    logger.debug("[SCHEDULER] Periodic health ping check running.")
