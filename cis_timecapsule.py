"""Time-capsule mode: experience the service as of a date you choose.

Prototype scope: date selection at login, a per-session simulation date, and
deterministic seeding derived from that date. The FEATURED_DATES list exists so
the destination screen has somewhere to point; curated per-date content packs
(archival headlines, era-specific announcements) are stubbed for later --
see CONTENT_PACK_STATUS.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta

# The CompuServe era this simulator covers.
MIN_DATE = date(1979, 1, 1)
MAX_DATE = date(1998, 12, 31)

# Curated jump points. Each entry is (date, short label shown on the menu).
# Content packs are NOT YET IMPLEMENTED: choosing one sets the simulation date
# and everything date-driven (briefing, period news, CB ambience, markets)
# responds to it, but there is no hand-written archival content per date yet.
FEATURED_DATES = (
    (date(1981, 8, 12), "IBM PC announced"),
    (date(1984, 1, 24), "Apple Macintosh debuts"),
    (date(1986, 1, 28), "Challenger"),
    (date(1987, 10, 19), "Black Monday market crash"),
    (date(1989, 11, 9), "Berlin Wall falls"),
    (date(1991, 8, 6), "First website goes live at CERN"),
)

CONTENT_PACK_STATUS = "stub"


def in_range(value: date) -> bool:
    """True when ``value`` falls inside the supported CompuServe era."""
    return MIN_DATE <= value <= MAX_DATE


def parse_user_date(text: str) -> date:
    """Parse an MM/DD/YYYY entry, enforcing the supported era.

    Raises ValueError with a user-facing message on any problem.
    """
    try:
        picked = datetime.strptime(text.strip(), "%m/%d/%Y").date()
    except (ValueError, TypeError):
        raise ValueError("Enter the date as MM/DD/YYYY, for example 06/12/1985.")
    if not in_range(picked):
        raise ValueError(
            f"Dates must fall between {MIN_DATE:%m/%d/%Y} and {MAX_DATE:%m/%d/%Y}."
        )
    return picked


def parse_stored_date(text) -> date | None:
    """Parse an ISO date from a member profile; None when missing/invalid."""
    if not text:
        return None
    try:
        picked = datetime.strptime(str(text), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    return picked if in_range(picked) else None


def surprise_date(seed_text: str = "") -> date:
    """Pick a random date in range. Stable per seed_text (e.g. user + day)."""
    chooser = random.Random(f"time-capsule-surprise:{seed_text}")
    span = (MAX_DATE - MIN_DATE).days
    return MIN_DATE + timedelta(days=chooser.randrange(span + 1))


def describe(value: date | None) -> str:
    """Human label for a simulation date; 'the present day' when None."""
    return "the present day" if value is None else value.strftime("%A, %B %d, %Y")
