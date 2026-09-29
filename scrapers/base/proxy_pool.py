"""Proxy pool manager with ipify verification and polite rotation."""
import requests
from typing import List, Optional
from loguru import logger


class ProxyPool:
    """Manages HTTP/HTTPS proxy validation and rotation."""

    def __init__(self, max_live: int = 10, timeout: float = 5.0):
        self.max_live = max_live
        self.timeout = timeout
        self.proxies: List[str] = []
        self._current_idx = 0

    def validate_proxy(self, proxy_url: str) -> bool:
        """Validates proxy connectivity through api.ipify.org within timeout."""
        try:
            proxies = {"http": proxy_url, "https": proxy_url}
            resp = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=self.timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def add_proxy(self, proxy_url: str) -> bool:
        if len(self.proxies) >= self.max_live:
            return False
        if self.validate_proxy(proxy_url):
            self.proxies.append(proxy_url)
            logger.debug(f"[PROXY POOL] Added validated proxy: {proxy_url}")
            return True
        return False

    def get_proxy(self) -> Optional[str]:
        """Returns next live proxy or None for direct polite connection."""
        if not self.proxies:
            return None
        proxy = self.proxies[self._current_idx % len(self.proxies)]
        self._current_idx += 1
        return proxy

    def remove_proxy(self, proxy_url: str) -> None:
        if proxy_url in self.proxies:
            self.proxies.remove(proxy_url)
            logger.warning(f"[PROXY POOL] Removed dead proxy: {proxy_url}")
