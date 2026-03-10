"""
Tkinter GUI dashboard for the VOLP Assignment Deadline Tracker.

Displays assignments in a colour-coded TreeView table:
    Green  → Submitted
    Yellow → Pending
    Red    → Overdue
    Grey   → Unknown

Provides a Refresh button to re-run the scraper.
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List

from models.assignment import Assignment, AssignmentStatus

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Colour palette
# ------------------------------------------------------------------
_COLOURS = {
    AssignmentStatus.SUBMITTED: "#2ecc71",   # green
    AssignmentStatus.PENDING:   "#f1c40f",   # yellow
    AssignmentStatus.OVERDUE:   "#e74c3c",   # red
    AssignmentStatus.UNKNOWN:   "#95a5a6",   # grey
}

_BG_COLOURS = {
    AssignmentStatus.SUBMITTED: "#d5f5e3",
    AssignmentStatus.PENDING:   "#fef9e7",
    AssignmentStatus.OVERDUE:   "#fadbd8",
    AssignmentStatus.UNKNOWN:   "#eaecee",
}


class DashboardApp:
    """Main Tkinter application window."""

    COLUMNS = ("course", "assignment", "deadline", "status")
    HEADINGS = ("Course", "Assignment", "Deadline", "Status")
    COLUMN_WIDTHS = (200, 280, 180, 110)

    def __init__(
        self,
        refresh_callback: Callable[[], List[Assignment]] | None = None,
    ) -> None:
        self._refresh_callback = refresh_callback

        # ---- Root window ----
        self.root = tk.Tk()
        self.root.title("VOLP Assignment Deadline Tracker")
        self.root.geometry("820x520")
        self.root.minsize(700, 400)
        self.root.configure(bg="#2c3e50")

        self._build_ui()
        self._configure_tags()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ---- Header frame ----
        header = tk.Frame(self.root, bg="#2c3e50", pady=10)
        header.pack(fill=tk.X)

        title_label = tk.Label(
            header,
            text="📋  VOLP Assignment Tracker",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        )
        title_label.pack(side=tk.LEFT, padx=16)

        refresh_btn = tk.Button(
            header,
            text="🔄  Refresh",
            font=("Segoe UI", 11),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._on_refresh,
        )
        refresh_btn.pack(side=tk.RIGHT, padx=16)

        # ---- Table frame ----
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Tracker.Treeview",
            font=("Segoe UI", 11),
            rowheight=30,
            borderwidth=0,
        )
        style.configure(
            "Tracker.Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background="#34495e",
            foreground="white",
        )
        style.map(
            "Tracker.Treeview",
            background=[("selected", "#3498db")],
            foreground=[("selected", "white")],
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.COLUMNS,
            show="headings",
            yscrollcommand=scrollbar.set,
            style="Tracker.Treeview",
        )
        scrollbar.config(command=self.tree.yview)

        for col, heading, width in zip(self.COLUMNS, self.HEADINGS, self.COLUMN_WIDTHS):
            self.tree.heading(col, text=heading, anchor=tk.W)
            self.tree.column(col, width=width, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ---- Status bar ----
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="#2c3e50",
            fg="#bdc3c7",
            anchor=tk.W,
            padx=16,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _configure_tags(self) -> None:
        """Register colour tags for each assignment status."""
        for status, bg in _BG_COLOURS.items():
            fg = "#000000"
            self.tree.tag_configure(status.value, background=bg, foreground=fg)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def populate(self, assignments: List[Assignment]) -> None:
        """Clear the table and insert *assignments*."""
        self.tree.delete(*self.tree.get_children())

        for a in assignments:
            a.refresh_status()  # re-evaluate in case time has passed
            self.tree.insert(
                "",
                tk.END,
                values=(a.course_name, a.title, a.deadline_display, a.status.value),
                tags=(a.status.value,),
            )

        self.status_var.set(f"{len(assignments)} assignment(s) loaded.")
        logger.info("Dashboard populated with %d assignment(s).", len(assignments))

    def run(self) -> None:
        """Enter the Tkinter main loop."""
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_refresh(self) -> None:
        """Called when the Refresh button is clicked."""
        if self._refresh_callback is None:
            messagebox.showinfo("Info", "No refresh callback configured.")
            return

        self.status_var.set("Refreshing assignments…")
        self.root.update_idletasks()

        try:
            assignments = self._refresh_callback()
            self.populate(assignments)
        except Exception as exc:
            logger.error("Refresh failed: %s", exc)
            messagebox.showerror("Error", f"Failed to refresh:\n{exc}")
            self.status_var.set("Refresh failed.")
