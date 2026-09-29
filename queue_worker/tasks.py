"""Asynchronous worker tasks for decoupling scraping from processing."""
from typing import Dict, Any, List
from loguru import logger
from pipeline.normalizer import normalize_quote
from pipeline.dedup import is_duplicate
from pipeline.anomaly_detection import detect_batch_anomalies
from pipeline.quality_report import QualityReport
from storage.snapshot import SnapshotStore
from storage.db import DatabaseStore
from index_engine.run import run_index_computation


def process_fare_quote(raw_quote: Dict[str, Any]) -> Dict[str, Any]:
    """Worker task: normalizes, audits, and persists individual fare quotes."""
    logger.info(f"[WORKER TASK] Processing quote for {raw_quote.get('origin')}-{raw_quote.get('destination')}")
    norm_fare = normalize_quote(raw_quote)

    if is_duplicate(norm_fare):
        return {"status": "dropped_duplicate"}

    validated = detect_batch_anomalies([norm_fare])
    store = SnapshotStore()
    store.save(validated)

    db = DatabaseStore()
    if db.is_connected:
        db.insert_fares(validated)

    return {"status": "ingested", "price": norm_fare.price_inr, "quality": norm_fare.quality_flag}


def trigger_index_computation_task() -> Dict[str, Any]:
    """Worker task: asynchronous index re-calculation."""
    logger.info("[WORKER TASK] Asynchronously triggering APIx index calculation.")
    run_index_computation()
    return {"status": "computed"}
