"""
Login automation for VOLP Classroom.

Navigates to the login page, enters credentials, submits the form,
and waits until the My Courses page loads (validated by the presence
of the course container element).
"""

from __future__ import annotations

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.wait_utils import (
    wait_for_element,
    wait_for_page_load,
    wait_for_url_contains,
    retry_click,
    safe_find_element,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# URLs
# ------------------------------------------------------------------
LOGIN_URL = "https://classroom.volp.in/login"
POST_LOGIN_URL_FRAGMENT = "learner/my-courses"

# ------------------------------------------------------------------
# Locators — confirmed against live VOLP DOM (Vuetify / Vue SPA)
# ------------------------------------------------------------------
# The login page uses Vuetify components.  IDs like "input-8" are
# dynamic, so we target placeholder text and the custom btn class.

USERNAME_INPUT = (By.CSS_SELECTOR, 'input[placeholder="Email or login"]')
PASSWORD_INPUT = (By.CSS_SELECTOR, 'input[placeholder="******"]')
LOGIN_BUTTON = (By.CSS_SELECTOR, "button.btn-sign-in")

# Fallback: XPath by visible button text
LOGIN_BUTTON_XPATH = (By.XPATH, '//button[contains(., "Sign In")]')

# Indicates successful login — the course container on My Courses
COURSE_CONTAINER = (By.CSS_SELECTOR, "[class*='course-card'], [class*='my-course']")


def login(driver: WebDriver, username: str, password: str) -> bool:
    """Automate login to VOLP Classroom.

    Args:
        driver:   Selenium WebDriver (headless Chrome).
        username: Student username / email.
        password: Student password.

    Returns:
        ``True`` if login succeeded (My Courses page detected),
        ``False`` otherwise.
    """
    logger.info("Navigating to login page: %s", LOGIN_URL)
    driver.get(LOGIN_URL)
    wait_for_page_load(driver)

    # ---- Enter credentials ----
    user_field = safe_find_element(driver, USERNAME_INPUT)
    if user_field is None:
        logger.error("Username field not found.")
        return False

    pass_field = safe_find_element(driver, PASSWORD_INPUT)
    if pass_field is None:
        logger.error("Password field not found.")
        return False

    user_field.clear()
    user_field.send_keys(username)

    pass_field.clear()
    pass_field.send_keys(password)

    # ---- Submit ----
    clicked = retry_click(driver, LOGIN_BUTTON)
    if not clicked:
        # Fallback: try XPath by button text
        logger.info("Primary button selector failed, trying XPath fallback.")
        clicked = retry_click(driver, LOGIN_BUTTON_XPATH)
    if not clicked:
        logger.error("Could not click login button.")
        return False

    # ---- Validate: wait for My Courses page ----
    try:
        wait_for_url_contains(driver, POST_LOGIN_URL_FRAGMENT, timeout=20)
        wait_for_element(driver, COURSE_CONTAINER, timeout=20, condition="visible")
        logger.info("Login successful — My Courses page loaded.")
        return True
    except Exception as exc:
        logger.error("Login validation failed: %s", exc)
        return False
