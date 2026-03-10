"""
Course extraction from the VOLP My Courses page.

Locates all visible course cards, extracts course names and links,
and provides navigation into individual courses.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from utils.wait_utils import (
    safe_find_elements,
    safe_get_text,
    safe_get_attribute,
    wait_for_page_load,
    retry_click,
    safe_find_element,
    wait_for_element,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Locators (stable selectors; will be refined after DOM inspection)
# ------------------------------------------------------------------
COURSE_CARDS = (By.CSS_SELECTOR, "[class*='course-card'], [class*='card']")
COURSE_NAME_INSIDE_CARD = (By.CSS_SELECTOR, "h3, h4, [class*='title'], [class*='name']")
VIEW_COURSE_BUTTON = (By.XPATH, ".//button[contains(text(),'View Course')] | .//a[contains(text(),'View Course')]")

# Fallback: all anchor-like elements inside a card
CARD_LINK_FALLBACK = (By.CSS_SELECTOR, "a[href*='course']")


@dataclass
class CourseInfo:
    """Lightweight container for a course's metadata."""
    name: str
    url: str


def get_all_courses(driver: WebDriver) -> List[CourseInfo]:
    """Extract course metadata from the My Courses page.

    Returns:
        A list of ``CourseInfo`` objects (name + URL).
    """
    logger.info("Extracting courses from My Courses page.")
    wait_for_page_load(driver)

    cards = safe_find_elements(driver, COURSE_CARDS)
    if not cards:
        logger.warning("No course cards found on the page.")
        return []

    courses: list[CourseInfo] = []
    for card in cards:
        name = _extract_course_name(card)
        url = _extract_course_url(card, driver)
        if name:
            courses.append(CourseInfo(name=name, url=url))
            logger.debug("Found course: %s → %s", name, url)

    logger.info("Total courses found: %d", len(courses))
    return courses


def navigate_to_course(driver: WebDriver, course: CourseInfo) -> bool:
    """Navigate into a single course's overview page.

    Tries the stored URL first; falls back to clicking the card.

    Returns:
        ``True`` if navigation succeeded.
    """
    if course.url:
        logger.info("Navigating to course via URL: %s", course.url)
        driver.get(course.url)
        wait_for_page_load(driver)
        return True

    logger.warning("No URL for course %r — cannot navigate.", course.name)
    return False


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _extract_course_name(card) -> str:
    """Pull the course name out of a card element."""
    try:
        title_el = card.find_element(*COURSE_NAME_INSIDE_CARD)
        return safe_get_text(title_el)
    except Exception:
        return safe_get_text(card)


def _extract_course_url(card, driver: WebDriver) -> str:
    """Find the course URL from a card element."""
    try:
        link = card.find_element(*CARD_LINK_FALLBACK)
        return safe_get_attribute(link, "href")
    except Exception:
        return ""
