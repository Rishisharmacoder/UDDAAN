"""Quality report generator for sweep auditing."""
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from pipeline.models import NormalizedFare

DEBUG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "debug")


class QualityReport:
    """Calculates audit metrics for every ingestion run."""

    @staticmethod
    def generate(fares: List[NormalizedFare], run_id: str = None) -> Dict[str, Any]:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        run_id = run_id or str(uuid.uuid4())[:8]

        total = len(fares)
        valid = sum(1 for f in fares if f.quality_flag == "ok")
        flagged = sum(1 for f in fares if f.quality_flag == "flagged")
        rejected = sum(1 for f in fares if f.quality_flag == "rejected")

        report = {
            "run_id": run_id,
            "generated_at": datetime.utcnow().isoformat(),
            "rows_collected": total,
            "rows_valid": valid,
            "rows_flagged": flagged,
            "rows_rejected": rejected,
            "valid_rate_pct": round((valid / total * 100.0) if total > 0 else 0.0, 2),
            "anomalies": [
                {
                    "route": f.route,
                    "window": f.window,
                    "source": f.source,
                    "price_inr": f.price_inr,
                    "flag": f.quality_flag
                }
                for f in fares if f.quality_flag != "ok"
            ]
        }

        report_file = os.path.join(DEBUG_DIR, f"quality_report_{run_id}.json")
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info(f"[QUALITY REPORT] Saved audit summary ({valid}/{total} valid) ➔ {report_file}")
        except Exception as e:
            logger.error(f"[QUALITY REPORT] Error saving quality report: {e}")

        return report
