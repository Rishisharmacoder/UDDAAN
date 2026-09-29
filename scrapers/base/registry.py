"""ScraperFactory for dynamic registration and runtime instantiation of adapters."""
from typing import Dict, Type, List, Optional
from loguru import logger
from scrapers.base.flight_scraper import FlightScraper


class ScraperFactory:
    """Registry maintaining active and registered scrapers."""
    _registry: Dict[str, Type[FlightScraper]] = {}

    @classmethod
    def register(cls, name: str, scraper_cls: Type[FlightScraper]) -> None:
        key = name.strip().lower()
        cls._registry[key] = scraper_cls
        logger.debug(f"[SCRAPER FACTORY] Registered adapter: '{key}' ➔ {scraper_cls.__name__}")

    @classmethod
    def get(cls, name: str, **kwargs) -> FlightScraper:
        key = name.strip().lower()
        if key not in cls._registry:
            registered = list(cls._registry.keys())
            raise ValueError(f"Unknown scraper: '{name}'. Available registered adapters: {registered}")
        return cls._registry[key](**kwargs)

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name.strip().lower() in cls._registry
