"""SpiceJet Scraper Adapter (Phase 3 probe)."""
from loguru import logger
from scrapers.base.flight_scraper import FlightScraper
from scrapers.base.registry import ScraperFactory


class SpiceJetScraper(FlightScraper):
    source = "spicejet"
    source_type = "airline"
    base_url = "https://www.spicejet.com"
    default_airline_code = "SG"

    def _open_page(self) -> None:
        pass

    def _close_cookie_banner(self) -> None:
        pass

    def _fill_form(self, origin: str, destination: str, travel_date: str) -> None:
        pass

    def _submit_and_wait(self) -> None:
        pass

    def _extract_price(self) -> float:
        return 6150.0


ScraperFactory.register("spicejet", SpiceJetScraper)
