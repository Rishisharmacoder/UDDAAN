"""Master sweep runner: executes multi-source airfare extraction across 6 routes x 5 windows."""
import os
import sys
import yaml
import argparse
from datetime import datetime, timezone, timedelta
from loguru import logger

import scrapers  # register all adapters
from scrapers.base.registry import ScraperFactory
from pipeline.normalizer import normalize_quote
from pipeline.dedup import is_duplicate
from pipeline.anomaly_detection import detect_batch_anomalies
from pipeline.quality_report import QualityReport
from storage.snapshot import SnapshotStore
from storage.db import DatabaseStore

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


def run_driver_sweep(sites=None, routes=None, windows=None, dry_run=False):
    logger.info("[DRIVER LOOP] Commencing multi-source ingestion sweep...")

    # Load configurations
    with open(os.path.join(CONFIG_DIR, "routes.yaml"), "r", encoding="utf-8") as f:
        routes_all = [f"{r['origin']}-{r['destination']}" for r in yaml.safe_load(f).get("routes", []) if r.get("enabled", True)]
    with open(os.path.join(CONFIG_DIR, "windows.yaml"), "r", encoding="utf-8") as f:
        windows_all = [w["label"] for w in yaml.safe_load(f).get("windows", []) if w.get("enabled", True)]

    target_routes = routes or routes_all
    target_windows = windows or windows_all
    target_sites = sites or ["indigo", "makemytrip", "amadeus"]

    logger.info(f"Target Sites   : {target_sites}")
    logger.info(f"Target Routes  : {target_routes}")
    logger.info(f"Target Windows : {target_windows}")

    window_offsets = {"T+1": 1, "T+7": 7, "T+15": 15, "T+30": 30, "T+45": 45}
    collected = []
    store = SnapshotStore()
    db = DatabaseStore()

    for site in target_sites:
        if not ScraperFactory.is_registered(site):
            logger.warning(f"Skipping unregistered site '{site}'")
            continue

        scraper = ScraperFactory.get(site)
        logger.info(f"\n--- Ingesting from {site.upper()} ({scraper.source_type}) ---")

        for r in target_routes:
            orig, dest = r.split("-")
            for win in target_windows:
                days = window_offsets.get(win, 7)
                tdate = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")

                try:
                    dto = scraper.fetch_fare(orig, dest, tdate, win, bypass_gap=dry_run)
                    norm_fare = normalize_quote(dto.to_dict())

                    if not is_duplicate(norm_fare):
                        collected.append(norm_fare)
                        print(f"  [{norm_fare.source.upper()}] {r} ({win}) -> INR {norm_fare.price_inr:,.2f}")
                except Exception as e:
                    logger.error(f"  Error on {site} for {r} ({win}): {e}")

    # Pipeline: Anomaly check & Quality report
    if collected:
        validated = detect_batch_anomalies(collected)
        report = QualityReport.generate(validated)

        # Persist
        store.save(validated)
        if db.is_connected:
            db.insert_fares(validated)

        print("\n" + "=" * 50)
        print("  SWEEP SUMMARY REPORT")
        print(f"  Total Ingested : {report['rows_collected']}")
        print(f"  Valid Fares    : {report['rows_valid']}")
        print(f"  Flagged Fares  : {report['rows_flagged']}")
        print(f"  Rejected Fares : {report['rows_rejected']}")
        print(f"  Validity Rate  : {report['valid_rate_pct']}%")
        print("=" * 50 + "\n")
        return 0
    else:
        logger.warning("[DRIVER LOOP] 0 fares collected.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APIx Master Driver Sweep Runner")
    parser.add_argument("--sites", type=str, help="Comma-separated sites e.g. indigo,makemytrip")
    parser.add_argument("--routes", type=str, help="Comma-separated routes e.g. DEL-BOM,DEL-BLR")
    parser.add_argument("--windows", type=str, help="Comma-separated windows e.g. T+7,T+15")
    parser.add_argument("--dry", action="store_true", help="Dry run mode (bypasses 45s sleep for instant testing)")
    args = parser.parse_args()

    s = [x.strip() for x in args.sites.split(",")] if args.sites else None
    r = [x.strip() for x in args.routes.split(",")] if args.routes else None
    w = [x.strip() for x in args.windows.split(",")] if args.windows else None

    exit_code = run_driver_sweep(sites=s, routes=r, windows=w, dry_run=args.dry)
    sys.exit(exit_code)
