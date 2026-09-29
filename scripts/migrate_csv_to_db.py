"""Migration script: imports CSV snapshot data into PostgreSQL / TimescaleDB."""
import os
import sys
from loguru import logger
from storage.snapshot import SnapshotStore
from storage.db import DatabaseStore


def migrate():
    logger.info("[MIGRATION] Reading historical fares from CSV snapshot...")
    store = SnapshotStore()
    fares = store.load()

    if not fares:
        logger.warning("[MIGRATION] No fares found in snapshot. Nothing to migrate.")
        return

    logger.info(f"[MIGRATION] Found {len(fares)} fares in snapshot. Connecting to Database...")
    db = DatabaseStore()

    if not db.is_connected:
        logger.error("[MIGRATION] PostgreSQL is not reachable! Ensure database container is running.")
        sys.exit(1)

    db.create_all_tables()
    success = db.insert_fares(fares)
    if success:
        logger.info(f"[MIGRATION SUCCESS] Migrated {len(fares)} fares into PostgreSQL hypertable.")
    else:
        logger.error("[MIGRATION FAILED] Error during database insertion.")
        sys.exit(1)


if __name__ == "__main__":
    migrate()
