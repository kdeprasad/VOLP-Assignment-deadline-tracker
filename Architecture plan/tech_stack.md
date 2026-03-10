# Tech Stack

## Programming Language

Python 3.10+

---

# Browser Automation

## Selenium

Used to automate browser actions including:

login
navigation
data extraction

---

## Chrome WebDriver

Browser controlled by Selenium.

ChromeDriver will be automatically installed using:

webdriver-manager

---

# Headless Chrome

Automation must run Chrome in headless mode so that the browser runs in the background.

Required Chrome options:

--headless=new
--disable-gpu
--no-sandbox
--disable-dev-shm-usage
--window-size=1920,1080

These prevent rendering issues in headless environments.

---

# GUI

## Tkinter

Used to build a lightweight desktop interface.

Components used:

TreeView table
scrollbar
refresh button

Tkinter chosen because:

built into Python
simple UI requirements
no extra dependencies

---

# Data Handling

## Python Standard Library

datetime
for deadline comparison

dataclasses
for structured assignment objects

---

# Project Structure

project/

main.py

scraper/
login.py
courses.py
assignments.py
driver.py

models/
assignment.py

gui/
dashboard.py

utils/
wait_utils.py
date_utils.py

requirements.txt

---

# Key Python Libraries

selenium
webdriver-manager

Optional future additions:

pandas
sqlite3
pyinstaller
