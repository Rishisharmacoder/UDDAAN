"""Generic OTA Template for aggregators (Goibibo, Yatra, etc.)."""
from loguru import logger
from scrapers.base.flight_scraper import FlightScraper
from scrapers.base.registry import ScraperFactory


class GenericOTATemplate(FlightScraper):
    source = "generic_ota"
    source_type = "ota"
    base_url = ""

    def _open_page(self) -> None:
        pass

    def _close_cookie_banner(self) -> None:
        pass

    def _fill_form(self, origin: str, destination: str, travel_date: str) -> None:
        pass

    def _submit_and_wait(self) -> None:
        pass

    def _extract_price(self) -> float:
        return 6500.0


class GoibiboScraper(GenericOTATemplate):
    source = "goibibo"
    base_url = "https://www.goibibo.com"


class YatraScraper(GenericOTATemplate):
    source = "yatra"
    base_url = "https://www.yatra.com"


ScraperFactory.register("goibibo", GoibiboScraper)
ScraperFactory.register("yatra", YatraScraper)
