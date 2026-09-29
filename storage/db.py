"""Database layer: PostgreSQL + TimescaleDB hypertables with graceful offline fallback."""
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from loguru import logger
from pipeline.models import NormalizedFare

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError:
    create_engine = None
    text = None
    sessionmaker = None


DDL_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    source_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_success_at TIMESTAMPTZ,
    fail_count_24h INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fares (
    fare_id BIGSERIAL,
    source_id INT,
    origin CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    route TEXT NOT NULL,
    flight_number TEXT DEFAULT '',
    flight_validation TEXT DEFAULT 'verified',
    travel_date DATE NOT NULL,
    "window" TEXT NOT NULL,
    cabin TEXT DEFAULT 'ECONOMY',
    airline_code TEXT,
    price_inr NUMERIC(10,2) NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    quality_flag TEXT DEFAULT 'ok'
);

CREATE TABLE IF NOT EXISTS index_values (
    index_id BIGSERIAL PRIMARY KEY,
    frequency TEXT NOT NULL,
    period TEXT NOT NULL,
    apix_value NUMERIC(10,4) NOT NULL,
    mom_pct NUMERIC(7,3),
    yoy_pct NUMERIC(7,3),
    computed_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (frequency, period)
);

CREATE TABLE IF NOT EXISTS basket_weights (
    route TEXT NOT NULL,
    "window" TEXT NOT NULL,
    weight NUMERIC(6,4) DEFAULT 1.0,
    base_price NUMERIC(10,2),
    base_month CHAR(7),
    PRIMARY KEY (route, "window")
);

CREATE TABLE IF NOT EXISTS scrape_runs (
    run_id BIGSERIAL PRIMARY KEY,
    source_id INT,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    rows_fetched INT,
    rows_valid INT,
    rows_anomaly INT,
    status TEXT,
    notes TEXT
);
"""


class DatabaseStore:
    """Manages PostgreSQL connection and time-series hypertable queries."""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.name = os.getenv("DB_NAME", "apix")
        self.user = os.getenv("DB_USER", "apix_user")
        self.password = os.getenv("DB_PASSWORD", "apix_secure_pass")
        self.is_connected = False
        self.engine = None
        self._init_connection()

    def _init_connection(self) -> None:
        if not create_engine:
            return
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            db_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        try:
            self.engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            self.is_connected = True
            logger.info(f"[DATABASE] Connected to PostgreSQL/TimescaleDB successfully!")
            self.create_all_tables()
        except Exception as e:
            logger.warning(f"[DATABASE] PostgreSQL offline ({e}). Using file-backed snapshot fallback.")
            self.is_connected = False

    def create_all_tables(self) -> None:
        if not self.is_connected:
            return
        try:
            with self.engine.begin() as conn:
                for statement in DDL_SCHEMA.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        conn.execute(text(stmt))
                # Auto-migrate flight_number and flight_validation if table was created earlier without it
                try:
                    conn.execute(text("ALTER TABLE fares ADD COLUMN IF NOT EXISTS flight_number TEXT DEFAULT '';"))
                    conn.execute(text("ALTER TABLE fares ADD COLUMN IF NOT EXISTS flight_validation TEXT DEFAULT 'verified';"))
                except Exception:
                    pass
                # Attempt to enable Timescale hypertable partition if extension available
                try:
                    conn.execute(text("SELECT create_hypertable('fares', 'scraped_at', if_not_exists => TRUE);"))
                    logger.info("[DATABASE] TimescaleDB hypertable partition configured on 'fares'.")
                except Exception:
                    logger.debug("[DATABASE] Standard table structure retained.")
        except Exception as e:
            logger.error(f"[DATABASE] Schema initialization error: {e}")

    def insert_fares(self, fares: List[NormalizedFare]) -> bool:
        if not self.is_connected or not fares:
            return False
        try:
            with self.engine.begin() as conn:
                for f in fares:
                    conn.execute(
                        text("""
                            INSERT INTO fares (origin, destination, route, flight_number, flight_validation, travel_date, "window", cabin, airline_code, price_inr, scraped_at, quality_flag)
                            VALUES (:orig, :dest, :route, :fnum, :fval, :tdate, :win, :cabin, :code, :price, :scraped, :quality)
                        """),
                        {
                            "orig": f.origin, "dest": f.destination, "route": f.route,
                            "fnum": f.flight_number or "",
                            "fval": getattr(f, "flight_validation", "verified"),
                            "tdate": f.travel_date, "win": f.window, "cabin": f.cabin,
                            "code": f.airline_code, "price": f.price_inr, "scraped": f.scraped_at,
                            "quality": f.quality_flag
                        }
                    )
            return True
        except Exception as e:
            logger.error(f"[DATABASE] Insert fares failed: {e}")
            return False

    def upsert_index_value(self, frequency: str, period: str, apix_val: float, mom_pct: Optional[float] = None) -> bool:
        if not self.is_connected:
            return False
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO index_values (frequency, period, apix_value, mom_pct, computed_at)
                        VALUES (:freq, :per, :val, :mom, now())
                        ON CONFLICT (frequency, period)
                        DO UPDATE SET apix_value = :val, mom_pct = :mom, computed_at = now();
                    """),
                    {"freq": frequency, "per": period, "val": apix_val, "mom": mom_pct}
                )
            return True
        except Exception as e:
            logger.error(f"[DATABASE] Upsert index failed: {e}")
            return False
