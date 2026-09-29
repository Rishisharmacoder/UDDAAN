"""Legal, Ethical Scraping & IT Act 2000 / DPDP Act 2023 Compliance Guardrails."""
import requests
import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict, Any, List
from loguru import logger

FORBIDDEN_PII_KEYS = {
    "name", "first_name", "last_name", "passenger", "email", "phone",
    "mobile", "passport", "aadhaar", "dob", "birth", "gender", "address",
    "credit_card", "cvv", "payment_info"
}


def check_robots_txt(target_url: str, user_agent: str = "*", timeout: float = 2.5) -> bool:
    """Check if target URL path is permitted under robots.txt with strict timeout to prevent hangs."""
    try:
        parsed = urlparse(target_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"

        # Fetch with explicit short timeout
        resp = requests.get(robots_url, headers={"User-Agent": user_agent}, timeout=timeout)
        if resp.status_code == 200:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(resp.text.splitlines())
            can_fetch = rp.can_fetch(user_agent, target_url)
            if not can_fetch:
                logger.warning(f"[COMPLIANCE] robots.txt disallows {target_url} for '{user_agent}'")
            return bool(can_fetch)
        elif resp.status_code in [401, 403]:
            logger.info(f"[COMPLIANCE] robots.txt returned HTTP {resp.status_code} for {base_url}; adhering to polite access")
            return True
        return True
    except Exception as e:
        logger.debug(f"[COMPLIANCE] robots.txt probe timed out or failed for {target_url} ({e}); continuing with safe limits.")
        return True


def assert_no_pii(data_dict: Dict[str, Any]) -> None:
    """Verifies that no Personally Identifiable Information (PII) is present in the ingested record."""
    for key in data_dict.keys():
        lower_k = key.lower()
        for forbidden in FORBIDDEN_PII_KEYS:
            if forbidden in lower_k:
                raise ValueError(
                    f"[COMPLIANCE BREACH] Ingestion rejected: detected forbidden PII field '{key}'!"
                )
