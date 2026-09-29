"""Master Unified Single-Command Runner for APIx Platform."""
import os
import sys
import time
import webbrowser
import uvicorn
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Banner
BANNER = """
======================================================================
     APIx -- Real-time Airfare Price Index Platform (SIH26056)
     Ministry of Statistics & Programme Implementation (MoSPI DIID)
======================================================================
  [+] Backend API    : http://127.0.0.1:8000/docs
  [+] React Dashboard: http://127.0.0.1:8000
  [+] Database       : PostgreSQL (Port 5435) + CSV Snapshot Fallback
  [+] Live Scraper   : ACTIVE (Auto-scraping every 10-15s in background)
======================================================================
"""


def main():
    print(BANNER)

    # 1. Check data availability
    from storage.snapshot import SnapshotStore
    snapshot = SnapshotStore()
    df = snapshot.get_dataframe()
    if os.getenv("AUTO_SEED", "false").lower() == "true" and (df.empty or len(df) < 10):
        logger.info("[INIT] Seeding baseline historical observations for accurate Laspeyres Index...")
        from scripts.seed_data import generate_seed_data
        generate_seed_data(save_fixture=False)
        logger.info("[INIT] Baseline data initialized successfully.")
    else:
        logger.info(f"[INIT] Live storage initialized with {len(df)} records in snapshot.")

    # 2. Check Database & Auto-initialize schema if available
    from storage.db import DatabaseStore
    db = DatabaseStore()
    if db.is_connected:
        logger.info("[DATABASE] PostgreSQL is ONLINE! Verifying table schemas...")
        db.create_all_tables()
    else:
        logger.warning("[DATABASE] PostgreSQL is offline. APIx will use file-backed snapshot & memory fallback.")

    # 3. Warm up Laspeyres index calculation
    from index_engine.run import run_index_computation
    try:
        run_index_computation()
    except Exception as e:
        logger.warning(f"[INDEX ENGINE] Startup calculation note: {e}")

    # 4. Start the background live automated scraper thread!
    from pipeline.live_feed import start_live_feed
    interval = float(os.getenv("SCRAPE_INTERVAL_SEC", "45.0"))
    start_live_feed(interval_sec=interval)
    logger.info(f"[LIVE ENGINE] Polite background scraper active (cycle: {interval}s with deduplication & FIFO storage cap).")

    # 5. Start Uvicorn Server serving React Dashboard + APIs
    port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    host = os.getenv("API_HOST", "0.0.0.0")
    logger.info(f"[SERVER] Launching FastAPI + React Dashboard on http://{host}:{port} ...")
    uvicorn.run("api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
