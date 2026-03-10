# Project Development Roadmap

---

# Phase 1 Project Setup

Goal

Create base project and environment.

Tasks

Create folder structure

Initialize Python virtual environment

Install dependencies

pip install selenium webdriver-manager

Create Chrome driver initializer.

Driver must run Chrome in headless mode.

---

# Phase 2 Robust Selenium Driver

Goal

Create reusable Selenium driver configured for SPA scraping.

Tasks

Implement Chrome options for headless execution.

Add driver factory function.

Add utilities for:

explicit waits
safe element selection
retry logic

Create helper functions:

wait_for_element
wait_for_clickable
safe_find_elements

These functions must prevent stale element exceptions.

---

# Phase 3 Login Automation

Goal

Automate login to VOLP classroom.

Steps

Open login page.

Enter username.

Enter password.

Submit login form.

Wait until My Courses page loads.

Validation condition:

presence of course container.

---

# Phase 4 Course Scraping

Goal

Extract all courses.

Tasks

Locate course card container.

Extract:

course name
course link

Navigate into each course.

Store results as structured objects.

---

# Phase 5 Assignment Scraping

Goal

Extract assignments from every course.

Steps

Open course overview.

Navigate to course content.

Detect whether assignments appear:

directly
inside sections

For each assignment:

open assignment page

extract:

title
deadline
submission status

Return structured list of assignments.

---

# Phase 6 Deadline Evaluation

Goal

Calculate assignment state.

Tasks

Convert deadline string to datetime.

Compare with system time.

Assign status:

Submitted
Pending
Overdue

---

# Phase 7 GUI Dashboard

Goal

Display assignments in a desktop interface.

Tasks

Create Tkinter window.

Add TreeView table.

Display assignment rows.

Add color indicators:

green submitted
yellow pending
red overdue

Add refresh button to rerun scraper.

---

# Phase 8 Integration

Goal

Connect scraper with GUI.

Steps

Run scraper

Collect assignments list

Feed results into GUI table

Render dashboard

---

# Phase 9 Stability Improvements

Goal

Make automation resilient.

Tasks

Add retry wrapper for Selenium actions.

Handle stale element exceptions.

Re-fetch elements after Vue re-render.

Add logging for debugging failures.
