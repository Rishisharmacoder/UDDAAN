"""Scrapers package auto-importing all modules to ensure factory registration."""
import scrapers.airline.indigo_stealth
import scrapers.airline.spicejet
import scrapers.ota.makemytrip_stealth
import scrapers.ota.generic_ota_template
import scrapers.api_sources.amadeus_source
import scrapers.api_sources.air_india_ndc
import scrapers.api_sources.cleartrip_api

from scrapers.base.registry import ScraperFactory
from scrapers.base.models import FlightResult

__all__ = ["ScraperFactory", "FlightResult"]
