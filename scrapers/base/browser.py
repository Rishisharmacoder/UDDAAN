"""Undetected ChromeDriver (uc) browser manager with stealth configurations."""
from typing import Optional, Any
from loguru import logger

try:
    import undetected_chromedriver as uc
except ImportError:
    uc = None


class BrowserManager:
    """Initializes and manages undetected-chromedriver sessions."""

    @staticmethod
    def get_driver(headless: bool = True, proxy: Optional[str] = None) -> Any:
        if uc is None:
            raise RuntimeError("undetected-chromedriver is not installed in the current environment")

        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=en-US,en;q=0.9")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        logger.info(f"[BROWSER] Launching uc.Chrome session (headless={headless})")
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(45)
        return driver

    @staticmethod
    def quit_driver(driver: Any) -> None:
        if driver:
            try:
                driver.quit()
                logger.info("[BROWSER] uc.Chrome session safely closed")
            except Exception as e:
                logger.debug(f"[BROWSER] Exception while quitting driver: {e}")
