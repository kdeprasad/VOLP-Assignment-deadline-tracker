"""
Assignment extraction from VOLP course content pages.

For every course:
    1. Navigates to course content.
    2. Detects assignments (direct or inside sections).
    3. Opens each assignment page.
    4. Extracts title, deadline, submission status.
    5. Returns structured ``Assignment`` objects.
"""

from __future__ import annotations

import logging
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from models.assignment import Assignment
from utils.date_utils import parse_deadline
from utils.wait_utils import (
    safe_find_element,
    safe_find_elements,
    safe_get_text,
    safe_get_attribute,
    wait_for_page_load,
    retry_click,
    wait_for_element,
    retry_action,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Locators (will be refined after inspecting actual VOLP DOM)
# ------------------------------------------------------------------
COURSE_CONTENT_LINK = (
    By.XPATH,
    "//a[contains(text(),'Content')] | //a[contains(text(),'content')] | //a[contains(@href,'course-content')]",
)
ASSIGNMENT_ITEMS = (
    By.XPATH,
    "//*[contains(@class,'assignment')] | //*[contains(@class,'handson')]",
)
SECTION_HEADERS = (
    By.XPATH,
    "//*[contains(@class,'section')] | //*[contains(@class,'module')]",
)

# Inside the assignment detail page
ASSIGNMENT_TITLE = (
    By.CSS_SELECTOR,
    "h1, h2, [class*='title'], [class*='assignment-name']",
)
ASSIGNMENT_DEADLINE = (
    By.XPATH,
    "//*[contains(text(),'Deadline') or contains(text(),'deadline') or contains(text(),'Due')]/..",
)
ASSIGNMENT_STATUS = (
    By.XPATH,
    "//*[contains(text(),'Submitted') or contains(text(),'submitted') or contains(text(),'Pending') or contains(text(),'pending')]",
)


def scrape_assignments_for_course(
    driver: WebDriver,
    course_name: str,
) -> List[Assignment]:
    """Scrape all assignments for one course.

    Assumes the driver is already on the course overview page.

    Args:
        driver:       Active WebDriver positioned on the course page.
        course_name:  Human-readable course name (for the data model).

    Returns:
        A list of ``Assignment`` dataclass instances.
    """
    logger.info("Scraping assignments for course: %s", course_name)
    assignments: list[Assignment] = []

    # ---- Navigate to course content ----
    if not _navigate_to_content(driver):
        logger.warning("Could not reach content page for %s.", course_name)
        return assignments

    # ---- Find assignment links ----
    items = safe_find_elements(driver, ASSIGNMENT_ITEMS, timeout=10)
    if not items:
        logger.info("No assignment elements found for %s.", course_name)
        return assignments

    # Collect links first to avoid stale refs after navigation
    assignment_urls: list[str] = []
    for item in items:
        url = safe_get_attribute(item, "href")
        if not url:
            # Try finding an anchor inside the element
            try:
                link = item.find_element(By.TAG_NAME, "a")
                url = safe_get_attribute(link, "href")
            except Exception:
                pass
        if url:
            assignment_urls.append(url)

    logger.info("Found %d assignment link(s) for %s.", len(assignment_urls), course_name)

    # ---- Visit each assignment page and extract data ----
    for url in assignment_urls:
        assignment = _extract_assignment(driver, url, course_name)
        if assignment:
            assignments.append(assignment)

    return assignments


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _navigate_to_content(driver: WebDriver) -> bool:
    """Click the 'Content' tab/link to reach the course content page."""
    try:
        clicked = retry_click(driver, COURSE_CONTENT_LINK, timeout=10)
        if clicked:
            wait_for_page_load(driver)
            return True
    except Exception as exc:
        logger.debug("Content navigation failed: %s", exc)
    return False


def _extract_assignment(
    driver: WebDriver,
    url: str,
    course_name: str,
) -> Assignment | None:
    """Open an assignment page and scrape its metadata."""
    try:
        driver.get(url)
        wait_for_page_load(driver)

        title = _get_assignment_title(driver)
        deadline_raw = _get_deadline_text(driver)
        submitted = _is_submitted(driver)

        deadline = parse_deadline(deadline_raw)

        return Assignment(
            course_name=course_name,
            title=title or "Untitled Assignment",
            deadline=deadline,
            submitted=submitted,
            url=url,
        )
    except Exception as exc:
        logger.error("Failed to extract assignment from %s: %s", url, exc)
        return None


def _get_assignment_title(driver: WebDriver) -> str:
    el = safe_find_element(driver, ASSIGNMENT_TITLE, timeout=8)
    return safe_get_text(el) if el else ""


def _get_deadline_text(driver: WebDriver) -> str:
    el = safe_find_element(driver, ASSIGNMENT_DEADLINE, timeout=8)
    return safe_get_text(el) if el else ""


def _is_submitted(driver: WebDriver) -> bool:
    """Check if the assignment page shows a 'Submitted' indicator."""
    el = safe_find_element(driver, ASSIGNMENT_STATUS, timeout=5, retries=1)
    if el is None:
        return False
    text = safe_get_text(el).lower()
    return "submitted" in text
