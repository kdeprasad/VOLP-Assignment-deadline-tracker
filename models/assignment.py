"""
Data model for assignments scraped from VOLP Classroom.

Uses Python dataclasses for clean, structured representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AssignmentStatus(Enum):
    """Possible states of an assignment relative to its deadline."""

    SUBMITTED = "Submitted"
    PENDING = "Pending"
    OVERDUE = "Overdue"
    UNKNOWN = "Unknown"


@dataclass
class Assignment:
    """Represents a single assignment extracted from a VOLP course.

    Attributes:
        course_name:  Name of the course this assignment belongs to.
        title:        Assignment title / label.
        deadline:     Deadline as a datetime object (None if not parseable).
        submitted:    Whether the student has already submitted.
        url:          Direct URL to the assignment page.
        status:       Computed status based on deadline & submission state.
    """

    course_name: str
    title: str
    deadline: Optional[datetime] = None
    submitted: bool = False
    url: str = ""
    status: AssignmentStatus = field(init=False, default=AssignmentStatus.UNKNOWN)

    def __post_init__(self) -> None:
        """Automatically compute status after initialisation."""
        self.status = self.compute_status()

    # ------------------------------------------------------------------
    # Status logic
    # ------------------------------------------------------------------

    def compute_status(self) -> AssignmentStatus:
        """Determine assignment status based on submission state and deadline.

        Rules (from project_requirements.md §5):
            * Submitted  → already submitted
            * Pending    → not submitted AND deadline is in the future
            * Overdue    → not submitted AND current time > deadline
            * Unknown    → deadline could not be determined
        """
        if self.submitted:
            return AssignmentStatus.SUBMITTED

        if self.deadline is None:
            return AssignmentStatus.UNKNOWN

        if datetime.now() > self.deadline:
            return AssignmentStatus.OVERDUE

        return AssignmentStatus.PENDING

    def refresh_status(self) -> None:
        """Re-evaluate status (useful when time passes between scrape and display)."""
        self.status = self.compute_status()

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def deadline_display(self) -> str:
        """Human-friendly deadline string for the GUI table."""
        if self.deadline is None:
            return "—"
        return self.deadline.strftime("%d %b %Y, %H:%M")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Assignment(course={self.course_name!r}, title={self.title!r}, "
            f"deadline={self.deadline_display!r}, status={self.status.value!r})"
        )
