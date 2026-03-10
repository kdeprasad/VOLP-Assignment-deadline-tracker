"""
VOLP Assignment Deadline Tracker — main entry point.

Orchestrates:
    1. Driver creation  (headless Chrome)
    2. Login            (credentials from user / env)
    3. Course scraping
    4. Assignment scraping across all courses
    5. GUI dashboard population

Usage:
    python main.py
"""

from __future__ import annotations

import logging
import os
import sys
from typing import List

from models.assignment import Assignment
from scraper.driver import create_driver, quit_driver
from scraper.login import login
from scraper.courses import get_all_courses, navigate_to_course
from scraper.assignments import scrape_assignments_for_course
from gui.dashboard import DashboardApp

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Credentials (read from environment or prompt)
# ------------------------------------------------------------------

def _get_credentials() -> tuple[str, str]:
    """Return (username, password) from env vars or interactive prompt."""
    username = os.environ.get("VOLP_USERNAME", "")
    password = os.environ.get("VOLP_PASSWORD", "")

    if not username:
        username = input("VOLP Username: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("VOLP Password: ").strip()

    return username, password


# ------------------------------------------------------------------
# Core scraping pipeline
# ------------------------------------------------------------------

def fetch_assignments(username: str = "", password: str = "") -> List[Assignment]:
    """Run the full scrape pipeline and return a list of Assignments.

    This function is designed to be called both from ``main()`` and from
    the GUI's refresh callback.
    """
    if not username or not password:
        username, password = _get_credentials()

    driver = create_driver()
    all_assignments: list[Assignment] = []

    try:
        # ---- Login ----
        success = login(driver, username, password)
        if not success:
            logger.error("Login failed. Aborting scrape.")
            return all_assignments

        # ---- Courses ----
        courses = get_all_courses(driver)
        if not courses:
            logger.warning("No courses found.")
            return all_assignments

        # ---- Assignments per course ----
        for course in courses:
            try:
                navigated = navigate_to_course(driver, course)
                if not navigated:
                    continue
                assignments = scrape_assignments_for_course(driver, course.name)
                all_assignments.extend(assignments)
            except Exception as exc:
                logger.error(
                    "Error scraping course %s: %s", course.name, exc,
                )
                # Continue with the next course — do NOT crash

        logger.info(
            "Scraping complete. Total assignments: %d", len(all_assignments),
        )

    finally:
        quit_driver(driver)

    return all_assignments


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main() -> None:
    """Launch the tracker: scrape → display dashboard."""
    logger.info("=== VOLP Assignment Deadline Tracker ===")

    username, password = _get_credentials()

    # First scrape
    assignments = fetch_assignments(username, password)

    # Build GUI with refresh capability
    def refresh() -> List[Assignment]:
        return fetch_assignments(username, password)

    app = DashboardApp(refresh_callback=refresh)
    app.populate(assignments)
    app.run()


if __name__ == "__main__":
    main()
