"""Human-like interaction simulation and React DOM event triggers."""
import time
import random
from typing import Any
from loguru import logger

try:
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
except ImportError:
    ActionChains = None
    Keys = None


def human_delay(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """Randomized human-like thinking delay to avoid burst heuristics."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def real_click(driver: Any, element: Any) -> None:
    """Moves mouse to element and clicks realistically."""
    try:
        if ActionChains:
            actions = ActionChains(driver)
            actions.move_to_element(element).pause(random.uniform(0.1, 0.4)).click().perform()
            return
    except Exception as e:
        logger.debug(f"ActionChains click failed, falling back: {e}")
    element.click()


def js_click(driver: Any, element: Any) -> None:
    """Invokes native JavaScript click to bypass overlapping invisible overlays."""
    driver.execute_script("arguments[0].click();", element)


def fire_react_event(driver: Any, element: Any, value: str) -> None:
    """Dispatches React-safe input and change events through prototype setter."""
    js = """
    var elem = arguments[0];
    var val = arguments[1];
    var lastValue = elem.value;
    elem.value = val;
    var event = new Event('input', { bubbles: true });
    // React 16+ value tracker hack
    var tracker = elem._valueTracker;
    if (tracker) {
        tracker.setValue(lastValue);
    }
    elem.dispatchEvent(event);
    elem.dispatchEvent(new Event('change', { bubbles: true }));
    """
    driver.execute_script(js, element, value)


def close_overlay(driver: Any) -> None:
    """Sends ESC key to dismiss blocking popups or dropdowns."""
    try:
        if Keys:
            body = driver.find_element("tag name", "body")
            body.send_keys(Keys.ESCAPE)
    except Exception:
        pass
