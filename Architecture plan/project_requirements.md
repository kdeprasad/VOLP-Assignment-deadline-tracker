# VOLP Classroom Assignment Tracker

## Objective

Build a Python desktop tool that automatically logs into the VOLP Classroom portal and retrieves assignments across all enrolled courses.

The application should extract assignment metadata and show:

* Assignment title
* Course name
* Deadline
* Submission status
* Whether the assignment is overdue

The tool eliminates the need to manually open every course to check deadlines.

---

# Target Website Flow

Login page
https://classroom.volp.in/login

After login redirect
https://classroom.volp.in/learner/my-courses

Each course has **View Course**

Course overview
https://classroom.volp.in/learner-course-overview

Course content
https://classroom.volp.in/learner-course-content

Assignments open in
https://classroom.volp.in/learner-handson-assignment

---

# Functional Requirements

## 1 Login Automation

The system must:

* open login page
* enter username and password
* submit form
* wait until the **My Courses page loads**

Login must be validated by detecting the presence of the course container element.

---

## 2 Course Extraction

From **My Courses page**:

The system must:

* locate all course cards
* extract course names
* click **View Course**
* navigate to course overview

Courses should be stored as structured objects.

---

## 3 Course Navigation

For every course:

1. open course overview
2. navigate to course content page
3. scan page for assignments

Assignments may appear in two formats:

### Direct Assignments

Assignments appear directly in course content.

### Section Assignments

Assignments appear inside sections/modules.

Each assignment must be opened individually.

---

## 4 Assignment Data Extraction

For each assignment collect:

Course name
Assignment title
Deadline
Submission status
Assignment URL

---

## 5 Deadline Evaluation

Assignment status logic:

Submitted → already submitted

Pending → before deadline

Overdue → current time > deadline AND not submitted

---

## 6 GUI Dashboard

Assignments displayed in table format.

Columns:

Course
Assignment
Deadline
Status

Visual indicators:

Green → Submitted
Yellow → Pending
Red → Overdue

Features:

Refresh assignments
Scrollable list

---

# Non Functional Requirements

## Browser

Automation must use:

Google Chrome via Selenium WebDriver

Chrome must run in **headless mode** so the browser does not appear.

---

## Performance

The tool should collect assignments from all courses in under 60 seconds.

---

## Reliability

The automation must be resilient to SPA behavior including:

dynamic classes
lazy loading
Vue component re-rendering
stale DOM elements

---

# Selenium Stability Requirements

The scraper must implement:

Explicit waits (WebDriverWait)

Expected conditions

Retry logic

Safe element extraction

Never use fixed sleep delays.

---

# Selector Strategy

Because Vue apps frequently change CSS classes:

Selectors must prefer:

data attributes
text content
stable hierarchy

Avoid:

generated class names
index-based selectors

---

# Error Handling

The scraper must handle:

login failure
network delay
stale elements
missing assignments

The application must not crash if one course fails to load.

---

# Output Example

Course | Assignment | Deadline | Status
AI | Assignment 1 | 20 Mar | Pending
ML | Project Proposal | 10 Mar | Overdue
DBMS | Lab Report | 18 Mar | Submitted
