"""
Robust Selenium helper utilities designed for Vue SPA scraping.

Every interaction with the DOM goes through one of these helpers so that
the scraper gracefully handles:
    * dynamic / generated CSS classes
    * lazy-loaded components
    * stale element references after Vue re-renders
    * slow network responses

All waits use ``WebDriverWait`` + ``ExpectedConditions`` — no fixed
``time.sleep()`` calls.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, List, Optional, TypeVar

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# Exceptions that are acceptable to ignore while polling
_POLL_IGNORED = (
    StaleElementReferenceException,
    NoSuchElementException,
    ElementNotInteractableException,
)

# Default timeout (seconds) for explicit waits
DEFAULT_TIMEOUT: int = 15

# Default number of retries for retry-based helpers
DEFAULT_RETRIES: int = 3

# Short pause between retries (kept minimal — NOT a fixed sleep)
_RETRY_PAUSE: float = 0.5

T = TypeVar("T")


# ------------------------------------------------------------------
# Core wait wrappers
# ------------------------------------------------------------------

def wait_for_element(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    condition: str = "presence",
) -> WebElement:
    """Wait until a single element satisfies the given condition.

    Args:
        driver:    Selenium WebDriver instance.
        locator:   A ``(By.*, value)`` tuple.
        timeout:   Maximum seconds to wait.
        condition: One of ``"presence"`` | ``"visible"`` | ``"clickable"``.

    Returns:
        The located ``WebElement``.

    Raises:
        TimeoutException: If the element is not found within *timeout*.
    """
    ec_map = {
        "presence": EC.presence_of_element_located,
        "visible": EC.visibility_of_element_located,
        "clickable": EC.element_to_be_clickable,
    }
    ec_func = ec_map.get(condition, EC.presence_of_element_located)

    wait = WebDriverWait(driver, timeout, ignored_exceptions=_POLL_IGNORED)
    return wait.until(ec_func(locator))


def wait_for_elements(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> List[WebElement]:
    """Wait until *at least one* element matching *locator* is present.

    Returns:
        A list of all matching ``WebElement`` objects.
    """
    wait = WebDriverWait(driver, timeout, ignored_exceptions=_POLL_IGNORED)
    wait.until(EC.presence_of_element_located(locator))
    return driver.find_elements(*locator)


def wait_for_clickable(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> WebElement:
    """Convenience alias — wait until an element is clickable."""
    return wait_for_element(driver, locator, timeout=timeout, condition="clickable")


def wait_for_page_load(
    driver: WebDriver,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> None:
    """Wait until ``document.readyState`` equals ``'complete'``.

    This catches full page navigations (not necessarily XHR-driven
    Vue route changes).
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_for_url_contains(
    driver: WebDriver,
    fragment: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """Wait until the current URL contains *fragment*."""
    return WebDriverWait(driver, timeout).until(EC.url_contains(fragment))


def wait_for_staleness(
    driver: WebDriver,
    element: WebElement,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """Wait until *element* becomes stale (detached from the DOM).

    Useful to confirm Vue has re-rendered before fetching fresh elements.
    """
    return WebDriverWait(driver, timeout).until(EC.staleness_of(element))


# ------------------------------------------------------------------
# Safe finders  (re-fetch to avoid stale references)
# ------------------------------------------------------------------

def safe_find_element(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> Optional[WebElement]:
    """Find a single element with built-in retry on stale/missing errors.

    Returns ``None`` instead of raising if all retries are exhausted.
    """
    for attempt in range(1, retries + 1):
        try:
            return wait_for_element(driver, locator, timeout=timeout)
        except (TimeoutException, *_POLL_IGNORED) as exc:
            logger.debug(
                "safe_find_element attempt %d/%d failed for %s: %s",
                attempt, retries, locator, exc,
            )
            if attempt < retries:
                time.sleep(_RETRY_PAUSE)
    logger.warning("safe_find_element exhausted retries for %s", locator)
    return None


def safe_find_elements(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> List[WebElement]:
    """Find multiple elements with retry logic.

    Returns an empty list if nothing is found after all retries.
    """
    for attempt in range(1, retries + 1):
        try:
            return wait_for_elements(driver, locator, timeout=timeout)
        except (TimeoutException, *_POLL_IGNORED) as exc:
            logger.debug(
                "safe_find_elements attempt %d/%d failed for %s: %s",
                attempt, retries, locator, exc,
            )
            if attempt < retries:
                time.sleep(_RETRY_PAUSE)
    logger.warning("safe_find_elements exhausted retries for %s", locator)
    return []


# ------------------------------------------------------------------
# Retry click
# ------------------------------------------------------------------

def retry_click(
    driver: WebDriver,
    locator: tuple[str, str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> bool:
    """Attempt to click an element, retrying on transient failures.

    Handles ``StaleElementReferenceException``,
    ``ElementClickInterceptedException`` (e.g. Vue overlay), and
    ``ElementNotInteractableException``.

    Returns:
        ``True`` if the click succeeded, ``False`` otherwise.
    """
    for attempt in range(1, retries + 1):
        try:
            element = wait_for_clickable(driver, locator, timeout=timeout)
            element.click()
            return True
        except (
            StaleElementReferenceException,
            ElementClickInterceptedException,
            ElementNotInteractableException,
        ) as exc:
            logger.debug(
                "retry_click attempt %d/%d for %s: %s",
                attempt, retries, locator, exc,
            )
            if attempt < retries:
                time.sleep(_RETRY_PAUSE)
        except TimeoutException:
            logger.warning("retry_click timed out locating %s", locator)
            return False

    logger.warning("retry_click exhausted retries for %s", locator)
    return False


def retry_action(
    action: Callable[[], T],
    *,
    retries: int = DEFAULT_RETRIES,
    accepted_exceptions: tuple = _POLL_IGNORED,
) -> Optional[T]:
    """Generic retry wrapper for any callable.

    Args:
        action:              A zero-argument callable to execute.
        retries:             How many times to try.
        accepted_exceptions: Exception types that trigger a retry.

    Returns:
        The return value of *action*, or ``None`` if all retries fail.
    """
    for attempt in range(1, retries + 1):
        try:
            return action()
        except accepted_exceptions as exc:
            logger.debug(
                "retry_action attempt %d/%d: %s", attempt, retries, exc,
            )
            if attempt < retries:
                time.sleep(_RETRY_PAUSE)
    return None


# ------------------------------------------------------------------
# Text extraction helpers
# ------------------------------------------------------------------

def safe_get_text(element: WebElement) -> str:
    """Extract visible text from *element*, returning ``""`` on error."""
    try:
        return element.text.strip()
    except (StaleElementReferenceException, WebDriverException):
        return ""


def safe_get_attribute(element: WebElement, attr: str) -> str:
    """Extract an attribute value, returning ``""`` on error."""
    try:
        return (element.get_attribute(attr) or "").strip()
    except (StaleElementReferenceException, WebDriverException):
        return ""
