"""
Date / time utilities for parsing deadline strings from VOLP Classroom.

VOLP may present deadlines in various formats.  This module tries multiple
patterns so the scraper can handle whichever one is on the page.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Common date/time formats observed on VOLP Classroom
# ------------------------------------------------------------------
_DATE_FORMATS: list[str] = [
    "%d %b %Y, %H:%M",       # 20 Mar 2026, 14:30
    "%d %b %Y %H:%M",        # 20 Mar 2026 14:30
    "%d %B %Y, %H:%M",       # 20 March 2026, 14:30
    "%d %B %Y %H:%M",        # 20 March 2026 14:30
    "%d %b %Y",              # 20 Mar 2026
    "%d %B %Y",              # 20 March 2026
    "%Y-%m-%d %H:%M:%S",     # 2026-03-20 14:30:00
    "%Y-%m-%d %H:%M",        # 2026-03-20 14:30
    "%Y-%m-%d",              # 2026-03-20
    "%d/%m/%Y %H:%M",        # 20/03/2026 14:30
    "%d/%m/%Y",              # 20/03/2026
    "%m/%d/%Y %H:%M",        # 03/20/2026 14:30
    "%m/%d/%Y",              # 03/20/2026
    "%b %d, %Y %H:%M",       # Mar 20, 2026 14:30
    "%b %d, %Y",             # Mar 20, 2026
    "%B %d, %Y %H:%M",       # March 20, 2026 14:30
    "%B %d, %Y",             # March 20, 2026
    "%d-%m-%Y %H:%M",        # 20-03-2026 14:30
    "%d-%m-%Y",              # 20-03-2026
]


def parse_deadline(raw: str | None) -> Optional[datetime]:
    """Try to parse a raw deadline string into a ``datetime``.

    Args:
        raw: The raw text extracted from the assignment page.

    Returns:
        A ``datetime`` if parsing succeeds, otherwise ``None``.
    """
    if not raw:
        return None

    # Normalise whitespace and strip surrounding noise
    cleaned = _clean_raw_date(raw)

    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    logger.warning("Could not parse deadline string: %r", raw)
    return None


def _clean_raw_date(raw: str) -> str:
    """Strip common prefixes / suffixes and normalise whitespace."""
    text = raw.strip()

    # Remove common leading labels ("Deadline:", "Due:", etc.)
    text = re.sub(r"(?i)^(deadline|due(\s*date)?)\s*[:]\s*", "", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
