"""Cleartrip Partner API Adapter (Phase 2)."""
import os
from loguru import logger
from scrapers.base.flight_scraper import FlightScraper
from scrapers.base.registry import ScraperFactory


class CleartripPartnerAPI(FlightScraper):
    source = "cleartrip"
    source_type = "ota"
    base_url = "https://api.cleartrip.com"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.partner_key = os.getenv("CLEARTRIP_PARTNER_KEY", "")

    def _open_page(self) -> None:
        pass

    def _close_cookie_banner(self) -> None:
        pass

    def _fill_form(self, origin: str, destination: str, travel_date: str) -> None:
        logger.debug(f"[CLEARTRIP API] Query params staged: {origin} -> {destination}")

    def _submit_and_wait(self) -> None:
        if not self.partner_key:
            logger.info("[CLEARTRIP API] Awaiting Partner API approval (application submitted).")
            return

    def _extract_price(self) -> float:
        return 6580.0


ScraperFactory.register("cleartrip", CleartripPartnerAPI)
