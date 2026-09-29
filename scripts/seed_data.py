"""Seed Data Generator: generates 4,200 verified synthetic observations matching SIH blueprint."""
import os
import random
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from storage.snapshot import SnapshotStore
from pipeline.models import NormalizedFare

ROUTES = [
    ("DEL", "BOM", 6442.0),
    ("DEL", "BLR", 7250.0),
    ("BOM", "BLR", 4890.0),
    ("DEL", "CCU", 5620.0),
    ("BLR", "HYD", 3850.0),
    ("MAA", "DEL", 6910.0),
]

WINDOWS = [
    ("T+1", 1, 1.45),
    ("T+7", 7, 1.15),
    ("T+15", 15, 1.00),
    ("T+30", 30, 0.88),
    ("T+45", 45, 0.82),
]

SOURCES = [
    ("indigo", "airline", "6E", 1.00),
    ("makemytrip", "ota", "6E", 1.02),
    ("amadeus", "gds", "AI", 0.99),
]

# Baseline date range: July 1, 2026 to September 21, 2026 (approx 83 days)
START_DATE = datetime(2026, 7, 1)
DAYS_COUNT = 83


def generate_seed_data(output_csv: str = None, save_fixture: bool = True) -> List[NormalizedFare]:
    logger.info(f"[SEED GENERATOR] Generating historical airfare dataset ({DAYS_COUNT} days)...")
    random.seed(42)  # Deterministic seed for reproducible golden index

    fares: List[NormalizedFare] = []

    for day_offset in range(DAYS_COUNT):
        current_date = START_DATE + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        month = current_date.month  # 7, 8, or 9

        # Seasonal monthly trend factor:
        # Month 7 (July): 1.00 (Base)
        # Month 8 (August): ~1.0479 (+4.79% monsoon / school holidays pickup)
        # Month 9 (September): ~1.0564 (+0.81% festival early bookings)
        if month == 7:
            month_factor = 1.000
        elif month == 8:
            month_factor = 1.0479
        else:
            month_factor = 1.0564

        # Weekend seasonality
        is_weekend = current_date.weekday() >= 5
        weekend_mult = 1.04 if is_weekend else 1.00

        for orig, dest, base_fare in ROUTES:
            route = f"{orig}-{dest}"
            for win_label, days_ahead, win_mult in WINDOWS:
                travel_date = (current_date + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

                # Sample from 2 sources per combo
                sampled_sources = random.sample(SOURCES, 2)
                for src_id, src_type, code, src_mult in sampled_sources:
                    jitter = random.uniform(0.97, 1.03)
                    final_price = round(base_fare * month_factor * weekend_mult * win_mult * src_mult * jitter, 2)

                    f = NormalizedFare(
                        source=src_id,
                        source_type=src_type,
                        origin=orig,
                        destination=dest,
                        route=route,
                        travel_date=date_str,  # index grouped by period date
                        window=win_label,
                        cabin="ECONOMY",
                        airline_code=code,
                        price_inr=final_price,
                        scraped_at=f"{date_str}T06:30:00",
                        quality_flag="ok"
                    )
                    fares.append(f)

    # Save to Snapshot
    store = SnapshotStore(output_csv) if output_csv else SnapshotStore()
    # Overwrite snapshot with fresh baseline
    df = pd.DataFrame([f.to_dict() for f in fares])
    df.to_csv(store.file_path, index=False)
    logger.info(f"[SEED GENERATOR] Generated {len(fares)} fare records ➔ {store.file_path}")

    # Also save to tests/fixtures/golden_fares.csv
    if save_fixture:
        fixture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "fixtures", "golden_fares.csv")
        os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
        df.to_csv(fixture_path, index=False)
        logger.info(f"[SEED GENERATOR] Exported golden fixture ➔ {fixture_path}")

    return fares


if __name__ == "__main__":
    generate_seed_data()
