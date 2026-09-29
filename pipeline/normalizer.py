"""Data Normalizer: cleans raw currency strings, airport codes, and dates."""
import re
from datetime import datetime
from typing import Dict, Any, Union
from loguru import logger
from pipeline.models import NormalizedFare

CITY_TO_IATA = {
    "DELHI": "DEL", "NEW DELHI": "DEL", "DEL": "DEL",
    "MUMBAI": "BOM", "BOMBAY": "BOM", "BOM": "BOM",
    "BENGALURU": "BLR", "BANGALORE": "BLR", "BLR": "BLR",
    "KOLKATA": "CCU", "CALCUTTA": "CCU", "CCU": "CCU",
    "HYDERABAD": "HYD", "HYD": "HYD",
    "CHENNAI": "MAA", "MADRAS": "MAA", "MAA": "MAA",
    "GOA": "GOI", "GOI": "GOI"
}


def normalize_price(val: Union[str, float, int]) -> float:
    """Parses raw text like '₹6,442', 'INR 6,442.50', or ' 6442 ' into float."""
    if isinstance(val, (int, float)):
        return float(val)
    text = str(val).strip()
    cleaned = re.sub(r"[^\d.]", "", text)
    if not cleaned:
        raise ValueError(f"Unable to parse price from string '{val}'")
    return float(cleaned)


def normalize_airport_code(val: str) -> str:
    """Converts airport name or city alias to 3-letter IATA uppercase code."""
    clean = val.strip().upper()
    if clean in CITY_TO_IATA:
        return CITY_TO_IATA[clean]
    if len(clean) == 3 and clean.isalpha():
        return clean
    raise ValueError(f"Unrecognized airport or city name: '{val}'")


def normalize_date(val: str) -> str:
    """Standardizes dates into ISO YYYY-MM-DD."""
    clean = val.strip()
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%d-%b-%y",
        "%d %b %Y"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(clean, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{val}'")


def normalize_quote(raw: Dict[str, Any]) -> NormalizedFare:
    """Transforms raw dictionary or FlightResult into NormalizedFare model."""
    price = normalize_price(raw.get("price_total") or raw.get("price_inr", 0.0))
    orig = normalize_airport_code(raw.get("origin", ""))
    dest = normalize_airport_code(raw.get("destination", ""))
    travel_date = normalize_date(str(raw.get("travel_date", "")))
    window = raw.get("window", "T+7")
    source = raw.get("source", "unknown")
    source_type = raw.get("source_type", "airline")
    airline_code = raw.get("airline_code", "6E")
    flight_number = raw.get("flight_number") or ""
    flight_validation = raw.get("flight_validation") or "verified"
    cabin = raw.get("cabin", "ECONOMY")
    scraped_at = raw.get("scraped_at") or datetime.utcnow().isoformat()
    quality = raw.get("quality_flag", "ok")

    return NormalizedFare(
        source=source,
        source_type=source_type,
        origin=orig,
        destination=dest,
        route=f"{orig}-{dest}",
        flight_number=flight_number,
        flight_validation=flight_validation,
        travel_date=travel_date,
        window=window,
        cabin=cabin,
        airline_code=airline_code,
        price_inr=price,
        scraped_at=scraped_at,
        quality_flag=quality
    )
