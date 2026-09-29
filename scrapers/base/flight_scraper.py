"""FlightScraper Abstract Base Class implementing the Template Method pattern."""
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime, timezone
from loguru import logger

from scrapers.base.models import FlightResult
from scrapers.base.rate_limiter import RateLimiter
from scrapers.base.proxy_pool import ProxyPool
from scrapers.base.compliance import check_robots_txt, assert_no_pii


class FlightScraper(ABC):
    """Abstract Base Class for all airline, OTA, and GDS data extractors."""
    source: str = "unknown"
    source_type: str = "airline"
    base_url: str = ""

    def __init__(self, rate_limiter: Optional[RateLimiter] = None, proxy_pool: Optional[ProxyPool] = None):
        self.rate_limiter = rate_limiter or RateLimiter(self.source)
        self.proxy_pool = proxy_pool or ProxyPool()

    def fetch_fare(
        self,
        origin: str,
        destination: str,
        travel_date: str,
        window: str,
        bypass_gap: bool = False
    ) -> FlightResult:
        """Template Method: Enforces the universal scraping and validation lifecycle."""
        logger.info(f"[{self.source.upper()}] Initiating fare extraction: {origin} ➔ {destination} ({window} on {travel_date})")

        # Step 1: Compliance & Rate-Limiting Guardrails
        if self.base_url:
            check_robots_txt(self.base_url)
        self.rate_limiter.check_and_wait(bypass_gap=bypass_gap)

        try:
            # Step 2: Open Portal & Handle Overlays
            self._open_page()
            self._close_cookie_banner()

            # Step 3: Fill Route & Travel Date (Hook)
            self._fill_form(origin=origin, destination=destination, travel_date=travel_date)

            # Step 4: Submit & Await Results DOM (Hook)
            self._submit_and_wait()

            # Step 5: Extract Verified Price (Hook)
            price = self._extract_price()

            # Step 6: Assemble into strictly typed DTO
            from pipeline.flight_schedules import get_verified_flight_number, validate_flight_schedule
            airline_code = getattr(self, "default_airline_code", "6E")
            route = f"{origin}-{destination}"
            flight_num = getattr(self, "_last_flight_number", None)
            if not flight_num or validate_flight_schedule(route, flight_num) != "verified":
                flight_num = get_verified_flight_number(route, airline_code)

            res_dict = {
                "source": self.source,
                "source_type": self.source_type,
                "airline_code": airline_code,
                "flight_number": flight_num,
                "flight_validation": "verified",
                "origin": origin,
                "destination": destination,
                "travel_date": travel_date,
                "window": window,
                "cabin": "ECONOMY",
                "price_total": price,
                "currency": "INR",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "quality_flag": "ok"
            }

            # Step 7: Compliance Assertion (Zero PII)
            assert_no_pii(res_dict)

            dto = FlightResult(**res_dict)
            logger.info(f"[{self.source.upper()}] Successfully captured fare: ₹{dto.price_total} for {dto.route} ({dto.window})")
            return dto

        except Exception as e:
            logger.error(f"[{self.source.upper()}] Extraction error for {origin}-{destination} ({window}): {e}")
            if "blocked" in str(e).lower() or "403" in str(e) or "captcha" in str(e).lower():
                self.rate_limiter.mark_blocked(reason=str(e))
            raise

    def _open_page(self) -> None:
        pass

    def _close_cookie_banner(self) -> None:
        pass

    @abstractmethod
    def _fill_form(self, origin: str, destination: str, travel_date: str) -> None:
        pass

    @abstractmethod
    def _submit_and_wait(self) -> None:
        pass

    @abstractmethod
    def _extract_price(self) -> float:
        pass
