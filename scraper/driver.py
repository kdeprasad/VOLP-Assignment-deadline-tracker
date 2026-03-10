"""
Chrome WebDriver factory for headless SPA scraping.

Configures Chrome with the options listed in tech_stack.md and returns
a ready-to-use ``webdriver.Chrome`` instance.
"""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def create_driver() -> webdriver.Chrome:
    """Create and return a headless Chrome WebDriver.

    Chrome options (from tech_stack.md):
        --headless=new
        --disable-gpu
        --no-sandbox
        --disable-dev-shm-usage
        --window-size=1920,1080

    ChromeDriver is auto-installed via ``webdriver-manager``.
    """
    options = _build_chrome_options()
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(0)  # We rely exclusively on explicit waits

    logger.info("Chrome driver created (headless).")
    return driver


def _build_chrome_options() -> Options:
    """Assemble Chrome options for headless SPA-friendly execution."""
    opts = Options()

    # ---- Required headless flags (tech_stack.md) ----
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")

    # ---- Extra stability flags for Vue SPA ----
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-blink-features=AutomationControlled")

    # Reduce fingerprinting detection
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Accept insecure certs (dev environments)
    opts.accept_insecure_certs = True

    return opts


def quit_driver(driver: webdriver.Chrome) -> None:
    """Safely quit the driver, suppressing exceptions."""
    try:
        driver.quit()
        logger.info("Chrome driver closed.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error closing driver: %s", exc)
