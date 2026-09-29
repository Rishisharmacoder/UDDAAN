"""Test suite for rate limiter and block cooldown."""
import os
import time
from scrapers.base.rate_limiter import RateLimiter, STATE_DIR


def test_rate_limiter_block_cooldown():
    # Ensure fresh state for test
    state_file = os.path.join(STATE_DIR, "test_site_blocked_rate.json")
    if os.path.exists(state_file):
        os.remove(state_file)

    limiter = RateLimiter("test_site_blocked", min_gap_sec=0.01, blocked_cooldown_hours=24)
    assert limiter.is_blocked() is False

    limiter.mark_blocked(reason="Test 403 trigger")
    assert limiter.is_blocked() is True

    # Attempting to check_and_wait while blocked must raise RuntimeError
    try:
        limiter.check_and_wait()
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "temporarily blocked" in str(e)

    # Clean up test artifact
    if os.path.exists(state_file):
        os.remove(state_file)


def test_rate_limiter_requests_tracked():
    state_file = os.path.join(STATE_DIR, "test_site_counter_rate.json")
    if os.path.exists(state_file):
        os.remove(state_file)

    limiter = RateLimiter("test_site_counter", min_gap_sec=0.01, max_req_per_hour=5)
    initial_total = limiter.state.get("total_requests", 0)

    limiter.check_and_wait(bypass_gap=True)
    assert limiter.state.get("total_requests", 0) == initial_total + 1

    if os.path.exists(state_file):
        os.remove(state_file)
