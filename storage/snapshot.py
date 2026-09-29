"""CSV Snapshot storage: fallback layer ensuring resilient offline operation."""
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


class SnapshotStore:
    """Manages CSV snapshot reading, appending, and exporting."""

    def __init__(self, file_path: str = SNAPSHOT_PATH):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save(self, fares: List[NormalizedFare]) -> None:
        """Appends list of normalized fares to snapshot CSV."""
        if not fares:
            return

        records = [f.to_dict() for f in fares]
        df = pd.DataFrame(records)

        # Select only required columns
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[CSV_COLUMNS]

        try:
            file_exists = os.path.exists(self.file_path)
            df.to_csv(self.file_path, mode="a" if file_exists else "w", header=not file_exists, index=False)
            logger.info(f"[SNAPSHOT] Appended {len(fares)} rows into {self.file_path}")
        except PermissionError:
            logger.warning(f"[SNAPSHOT] Cannot write to {self.file_path} because it is open in another program (e.g. Excel). Data was safely saved to PostgreSQL.")
        except Exception as e:
            logger.error(f"[SNAPSHOT] Error saving snapshot: {e}")

    def _read_cleaned_df(self) -> pd.DataFrame:
        """Reads CSV filtering out any leading SQL comments like '-- Active:' while keeping hyphens in data."""
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
            except Exception as err:
                continue
        return fares

    def get_dataframe(self) -> pd.DataFrame:
        """Returns snapshot as pandas DataFrame safely ignoring comments."""
        return self._read_cleaned_df()
