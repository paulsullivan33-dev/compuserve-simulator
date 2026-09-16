"""Time-capsule mode: experience the service as of a date you choose.

Prototype scope: date selection at login, a per-session simulation date, and
deterministic seeding derived from that date. The FEATURED_DATES list has
curated per-date content packs (archival headlines, era-specific
announcements, CB topics, market notes, on-this-day context) loaded from
timecapsule_packs.json -- see CONTENT_PACK_STATUS.
"""
from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

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

CONTENT_PACK_STATUS = "loaded"

_PACK_SECTIONS = ("date", "label", "headlines", "announcements", "cb_topics",
                  "market_notes", "on_this_day")
_STORY_FIELDS = ("id", "category", "title", "summary", "published", "source")


def _load_packs() -> dict:
    """Load and validate the curated content packs for the featured dates."""
    path = Path(__file__).resolve().with_name("timecapsule_packs.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    packs = data.get("packs", {})
    missing = [when.isoformat() for when, _ in FEATURED_DATES
               if when.isoformat() not in packs]
    if missing:
        raise RuntimeError(f"Time-capsule packs missing for dates: {missing}")
    for key, pack in packs.items():
        if not set(_PACK_SECTIONS).issubset(pack):
            raise RuntimeError(f"Time-capsule pack {key} is missing sections.")
        date.fromisoformat(pack["date"])  # validates the ISO date string
        if not 8 <= len(pack["headlines"]) <= 12:
            raise RuntimeError(f"Time-capsule pack {key}: need 8-12 headlines.")
        if not 2 <= len(pack["announcements"]) <= 4:
            raise RuntimeError(f"Time-capsule pack {key}: need 2-4 announcements.")
        if not 4 <= len(pack["cb_topics"]) <= 6:
            raise RuntimeError(f"Time-capsule pack {key}: need 4-6 CB topics.")
        if not 0 <= len(pack["market_notes"]) <= 4:
            raise RuntimeError(f"Time-capsule pack {key}: need 0-4 market notes.")
        if not 2 <= len(pack["on_this_day"]) <= 3:
            raise RuntimeError(f"Time-capsule pack {key}: need 2-3 on-this-day items.")
        for story in pack["headlines"]:
            if not set(_STORY_FIELDS).issubset(story):
                raise RuntimeError(f"Time-capsule pack {key}: story missing fields.")
    return packs


# Curated content packs for the featured dates. Loaded at import like the
# other historical JSON content (see cis_timeline); validation raises
# immediately if a pack is malformed so bad data cannot reach the screen.
PACKS: dict = _load_packs()


def pack_for(value: Any) -> Optional[dict]:
    """Return the content pack for ``value`` (a date) or None."""
    if value is None:
        return None
    key = value.isoformat() if hasattr(value, "isoformat") else str(value)
    return PACKS.get(key)


def pack_headlines(pack: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    """Archival headlines in the article shape the news screen consumes."""
    return [dict(story) for story in pack.get("headlines", [])]


def cb_conversation(pack: Mapping[str, Any], randomizer, handles: Sequence[str]):
    """Build a small (sender, line) CB exchange from a pack's CB topics.

    ``handles`` is passed in so this dependency-free module does not need to
    import cis_dynamic's handle table.
    """
    topics = list(pack.get("cb_topics", []))
    if not topics or not handles:
        return []
    picks = randomizer.sample(topics, min(2, len(topics)))
    lines = []
    used = set()
    for topic in picks:
        available = [h for h in handles if h not in used] or list(handles)
        handle = randomizer.choice(available)
        used.add(handle)
        lines.append((handle, topic))
    return lines


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
