"""Polite Rate Limiter with 45s minimum gap, 15 req/hour cap, and 24h block cooldown."""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "state")


class RateLimiter:
    """Manages rate-limiting state per data source, surviving application restarts."""

    def __init__(
        self,
        site_id: str,
        min_gap_sec: float = 45.0,
        max_req_per_hour: int = 15,
        blocked_cooldown_hours: int = 24
    ):
        self.site_id = site_id
        self.min_gap_sec = min_gap_sec
        self.max_req_per_hour = max_req_per_hour
        self.blocked_cooldown_hours = blocked_cooldown_hours
        os.makedirs(STATE_DIR, exist_ok=True)
        self.state_file = os.path.join(STATE_DIR, f"{self.site_id}_rate.json")
        self._load_state()

    def _load_state(self) -> None:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading rate state for {self.site_id}: {e}")
                self.state = self._default_state()
        else:
            self.state = self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        return {
            "last_request_time": 0.0,
            "hourly_requests": [],
            "blocked_until": None,
            "total_requests": 0
        }

    def _save_state(self) -> None:
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save rate state for {self.site_id}: {e}")

    def is_blocked(self) -> bool:
        """Returns True if site is in 24h block cooldown."""
        blocked_until_str = self.state.get("blocked_until")
        if not blocked_until_str:
            return False
        try:
            blocked_until = datetime.fromisoformat(blocked_until_str)
            if datetime.utcnow() < blocked_until:
                logger.warning(f"[RATE LIMITER] {self.site_id} is in cooldown until {blocked_until_str}")
                return True
            else:
                self.state["blocked_until"] = None
                self._save_state()
                return False
        except Exception:
            return False

    def mark_blocked(self, reason: str = "WAF or CAPTCHA detected") -> None:
        """Marks the site as blocked for 24 hours to prevent spam or IP ban."""
        blocked_until = datetime.utcnow() + timedelta(hours=self.blocked_cooldown_hours)
        self.state["blocked_until"] = blocked_until.isoformat()
        self._save_state()
        logger.error(f"[RATE LIMITER] Marked {self.site_id} BLOCKED until {blocked_until.isoformat()} ({reason})")

    def check_and_wait(self, bypass_gap: bool = False) -> None:
        """Checks limits and pauses execution to honour min_gap_sec and max_req_per_hour."""
        if self.is_blocked():
            raise RuntimeError(f"{self.site_id} is temporarily blocked in 24h cooldown")

        now = time.time()
        last_req = self.state.get("last_request_time", 0.0)

        # 1. Enforce min gap (unless bypass requested in testing mode)
        if not bypass_gap:
            elapsed = now - last_req
            if elapsed < self.min_gap_sec:
                sleep_duration = self.min_gap_sec - elapsed
                logger.info(f"[RATE LIMITER] Enforcing {self.min_gap_sec}s politeness gap on {self.site_id} (sleeping {sleep_duration:.1f}s)")
                time.sleep(sleep_duration)

        # 2. Enforce hourly crawl budget
        now = time.time()
        hour_ago = now - 3600.0
        recent = [t for t in self.state.get("hourly_requests", []) if t > hour_ago]
        if len(recent) >= self.max_req_per_hour and not bypass_gap:
            oldest = recent[0]
            wait_time = (oldest + 3600.0) - now + 1.0
            if wait_time > 0:
                logger.warning(f"[RATE LIMITER] Max {self.max_req_per_hour} req/hr reached on {self.site_id}. Waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                recent = [t for t in self.state.get("hourly_requests", []) if t > time.time() - 3600.0]

        # 3. Record request
        now = time.time()
        recent.append(now)
        self.state["hourly_requests"] = recent
        self.state["last_request_time"] = now
        self.state["total_requests"] = self.state.get("total_requests", 0) + 1
        self._save_state()
