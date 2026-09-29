"""Test script for Amadeus GDS official API adapter."""
import os
from loguru import logger
from scrapers.base.registry import ScraperFactory
import scrapers


def test_amadeus():
    logger.info("[AMADEUS TEST] Testing Amadeus GDS adapter via ScraperFactory...")
    adapter = ScraperFactory.get("amadeus")
    dto = adapter.fetch_fare("DEL", "BOM", "2026-10-01", "T+7", bypass_gap=True)
    print(f"\nCaptured Amadeus Fare Result:")
    print(f"  Source       : {dto.source} ({dto.source_type})")
    print(f"  Route        : {dto.origin} -> {dto.destination}")
    print(f"  Window       : {dto.window} (Travel Date: {dto.travel_date})")
    print(f"  Price (INR)  : INR {dto.price_total:,.2f}")
    print(f"  Quality Flag : {dto.quality_flag}")
    print(f"  Scraped At   : {dto.scraped_at}\n")
    assert dto.price_total > 500.0


if __name__ == "__main__":
    test_amadeus()
