"""CSV Snapshot storage: fallback layer ensuring resilient offline operation with FIFO circular retention."""
import io
import os
import pandas as pd
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from loguru import logger
from pipeline.models import NormalizedFare

SNAPSHOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "snapshot.csv")

CSV_COLUMNS = [
    "source", "source_type", "origin", "destination", "route", "flight_number", "flight_validation",
    "travel_date", "window", "cabin", "airline_code", "price_inr",
    "scraped_at", "quality_flag"
]

# Maximum rows retained in snapshot.csv to prevent disk exhaustion (keeps file size bounded ~1 MB)
MAX_SNAPSHOT_ROWS = int(os.getenv("MAX_SNAPSHOT_ROWS", "6500"))
BASE_REFERENCE_MONTH = "2026-07"


class SnapshotStore:
    """Manages CSV snapshot reading, appending, deduplication, and FIFO circular buffer retention."""

    def __init__(self, file_path: str = SNAPSHOT_PATH):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save(self, fares: List[NormalizedFare]) -> None:
        """Appends list of normalized fares to snapshot CSV with automatic FIFO cap and deduplication."""
        if not fares:
            return

        new_records = [f.to_dict() for f in fares]
        new_df = pd.DataFrame(new_records)

        # Ensure all required columns exist
        for col in CSV_COLUMNS:
            if col not in new_df.columns:
                new_df[col] = ""
        new_df = new_df[CSV_COLUMNS]

        try:
            if os.path.exists(self.file_path):
                existing_df = self._read_cleaned_df()
                if not existing_df.empty:
                    # Concat existing and new
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

                    # Deduplicate exact identical consecutive entries
                    combined_df.drop_duplicates(
                        subset=["route", "flight_number", "travel_date", "window", "price_inr", "source"],
                        keep="last",
                        inplace=True
                    )

                    # FIFO Retention Policy:
                    # 1. Always protect the base reference month (2026-07) so base basket V0 remains invariant
                    base_mask = combined_df["travel_date"].astype(str).str.startswith(BASE_REFERENCE_MONTH)
                    base_df = combined_df[base_mask]
                    rolling_df = combined_df[~base_mask]

                    # 2. Keep only the latest (MAX_SNAPSHOT_ROWS - len(base_df)) rows in rolling window
                    max_rolling = max(1000, MAX_SNAPSHOT_ROWS - len(base_df))
                    if len(rolling_df) > max_rolling:
                        rolling_df = rolling_df.tail(max_rolling)

                    final_df = pd.concat([base_df, rolling_df], ignore_index=True)
                else:
                    final_df = new_df
            else:
                final_df = new_df

            # Write cleanly to snapshot file
            final_df.to_csv(self.file_path, index=False)
            logger.info(f"[SNAPSHOT] Stored {len(fares)} new fares. Snapshot strictly bounded at {len(final_df)} rows (FIFO Cap: {MAX_SNAPSHOT_ROWS}).")

        except PermissionError:
            logger.warning(f"[SNAPSHOT] Cannot write to {self.file_path} (open in another program). Appending deferred.")
        except Exception as e:
            logger.error(f"[SNAPSHOT] Error saving snapshot: {e}")

    def _read_cleaned_df(self) -> pd.DataFrame:
        """Reads CSV filtering out any leading SQL comments while keeping hyphens in data."""
        if not os.path.exists(self.file_path):
            return pd.DataFrame(columns=CSV_COLUMNS)
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                valid_lines = [line for line in f if not line.strip().startswith("--")]
            df = pd.read_csv(
                io.StringIO("".join(valid_lines)),
                dtype={"flight_number": str, "flight_validation": str, "source": str, "airline_code": str}
            )
            if "quality_flag" not in df.columns:
                df["quality_flag"] = "ok"

            from pipeline.flight_schedules import get_verified_flight_number, validate_flight_schedule

            def sanitize_flight_num(r):
                fn = str(r.get("flight_number", "")).strip()
                if not fn or fn.lower() in ["nan", "0.0", "0", "none"]:
                    return get_verified_flight_number(str(r.get("route", "")), str(r.get("airline_code", "6E")))
                return fn

            df["flight_number"] = df.apply(sanitize_flight_num, axis=1)
            df["flight_validation"] = df.apply(
                lambda r: validate_flight_schedule(str(r.get("route", "")), str(r.get("flight_number", ""))),
                axis=1
            )
            return df
        except Exception as e:
            logger.error(f"[SNAPSHOT] Error reading snapshot: {e}")
            return pd.DataFrame(columns=CSV_COLUMNS)

    def load(self, limit: Optional[int] = None) -> List[NormalizedFare]:
        """Loads normalized fares from CSV snapshot."""
        df = self._read_cleaned_df()
        if df.empty:
            return []

        if limit:
            df = df.tail(limit)
        fares = []
        for _, row in df.iterrows():
            try:
                f = NormalizedFare(
                    source=str(row["source"]),
                    source_type=str(row.get("source_type", "airline")),
                    origin=str(row["origin"]),
                    destination=str(row["destination"]),
                    route=str(row.get("route", f"{row['origin']}-{row['destination']}")),
                    flight_number=str(row.get("flight_number", "")),
                    flight_validation=str(row.get("flight_validation", "verified")),
                    travel_date=str(row["travel_date"]),
                    window=str(row["window"]),
                    cabin=str(row.get("cabin", "ECONOMY")),
                    airline_code=str(row.get("airline_code", "6E")),
                    price_inr=float(row["price_inr"]),
                    scraped_at=str(row.get("scraped_at", datetime.now(timezone.utc).isoformat())),
                    quality_flag=str(row.get("quality_flag", "ok"))
                )
                fares.append(f)
            except Exception:
                continue
        return fares

    def get_dataframe(self) -> pd.DataFrame:
        """Returns snapshot as pandas DataFrame safely ignoring comments."""
        return self._read_cleaned_df()
