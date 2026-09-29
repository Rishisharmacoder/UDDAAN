"""Background automated live scraper feed engine."""
import time
import random
import threading
from datetime import datetime, timezone, timedelta
from loguru import logger

import scrapers
from scrapers.base.registry import ScraperFactory
from pipeline.normalizer import normalize_quote
from pipeline.dedup import is_duplicate
from pipeline.anomaly_detection import detect_batch_anomalies
from storage.snapshot import SnapshotStore
from storage.db import DatabaseStore
from index_engine.apix import APIxIndexEngine
from storage.redis_cache import RedisCache

ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL")
]

WINDOWS = [
    ("T+1", 1),
    ("T+7", 7),
    ("T+15", 15),
    ("T+30", 30),
    ("T+45", 45)
]

SOURCES = ["indigo", "makemytrip", "amadeus"]

_running = False
_thread = None


def scrape_single_flight(site: str = None, route: str = None, window: str = None):
    """Scrapes a single real-time flight quote and writes directly to DB and CSV."""
    if not site:
        site = random.choice(SOURCES)
    if not route:
        orig, dest = random.choice(ROUTES)
    else:
        orig, dest = route.split("-")

    if not window:
        win_label, days = random.choice(WINDOWS)
    else:
        win_label = window.strip().replace(" ", "+").upper()
        offsets = {"T+1": 1, "T+7": 7, "T+15": 15, "T+30": 30, "T+45": 45}
        days = offsets.get(win_label, 7)

    tdate = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")

    scraper = ScraperFactory.get(site)
    dto = scraper.fetch_fare(orig, dest, tdate, win_label, bypass_gap=True)
    norm = normalize_quote(dto.to_dict())
    validated = detect_batch_anomalies([norm])
    final_fare = validated[0]

    # 1. Save to CSV snapshot
    store = SnapshotStore()
    store.save([final_fare])

    # 2. Save to PostgreSQL DB
    db = DatabaseStore()
    if db.is_connected:
        db.insert_fares([final_fare])

    # 3. Update Redis Hot Cache with active source
    cache = RedisCache()
    cache.set_active_datasource({
        "active": f"{site} (live automated feed)",
        "source_type": final_fare.source_type,
        "description": f"Real-time stream from {site.upper()}"
    })

    logger.info(f"[LIVE SCRAPER] Ingested: {final_fare.source.upper()} {final_fare.route} ({final_fare.window}) ➔ INR {final_fare.price_inr:,.2f}")
    return final_fare


def _live_feed_worker(interval_sec: float = 12.0):
    global _running
    logger.info(f"[LIVE SCRAPER DAEMON] Started real-time background scraper (cycle: every {interval_sec}s)...")
    while _running:
        try:
            scrape_single_flight()
        except Exception as e:
            logger.error(f"[LIVE SCRAPER DAEMON] Cycle error: {e}")
        time.sleep(interval_sec)


def start_live_feed(interval_sec: float = 12.0):
    """Starts background scraper thread."""
    global _running, _thread
    if _running:
        return
    _running = True
    _thread = threading.Thread(target=_live_feed_worker, args=(interval_sec,), daemon=True)
    _thread.start()


def stop_live_feed():
    global _running
    _running = False
