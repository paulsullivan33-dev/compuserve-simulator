"""Books & Magazines service for the December 1988 simulation setting.

Pure content + logic module: December 1988 hardcover bestsellers
(fiction and nonfiction), December 1988 magazine issues with plausible
cover-story blurbs, and short staff reviews of 1988 books. All content
functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page).

FACT CARE: only the rankings we are sure of are asserted (Tom Clancy's
"The Cardinal of the Kremlin" is presented as the month's #1 fiction
bestseller and Stephen Hawking's "A Brief History of Time" as the
month's #1 nonfiction bestseller, per the service brief); every other
title is offered as "among the month's bestselling titles" with no
false position numbers. No content is dated after December 1988.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Hardcover Fiction -- December 1988
# ---------------------------------------------------------------------------
# Confident: "The Cardinal of the Kremlin" (Tom Clancy, Knopf, August 1988)
# sat atop the fiction list in late 1988. Everything else is presented
# hedged, as "among the month's bestselling titles."
FICTION_NUMBER_ONE = ("Tom Clancy", "The Cardinal of the Kremlin")

ALSO_FICTION_BESTSELLERS: List[Tuple[str, str]] = [
    ("Anne Rice", "The Queen of the Damned"),
    ("James A. Michener", "Alaska"),
    ("Sidney Sheldon", "The Sands of Time"),
    ("Salman Rushdie", "The Satanic Verses"),
    ("Gabriel Garcia Marquez", "Love in the Time of Cholera"),
    ("Stephen King", "The Tommyknockers"),
    ("Tom Clancy", "Red Storm Rising"),
    ("Danielle Steel", "Zoya"),
]

# Deterministic weekly "editor's pick" -- rotates through the hedged
# fiction list by day of month so the front page changes week to week.
EDITOR_PICKS: List[Tuple[str, str]] = [
    ("Anne Rice", "The Queen of the Damned"),
    ("James A. Michener", "Alaska"),
    ("Sidney Sheldon", "The Sands of Time"),
    ("Salman Rushdie", "The Satanic Verses"),
    ("Gabriel Garcia Marquez", "Love in the Time of Cholera"),
]


# ---------------------------------------------------------------------------
# Hardcover Nonfiction -- December 1988
# ---------------------------------------------------------------------------
# Confident: Stephen Hawking's "A Brief History of Time" (Bantam, 1988)
# was the dominant nonfiction bestseller of 1988. Everything else hedged.
NONFICTION_NUMBER_ONE = ("Stephen Hawking", "A Brief History of Time")

ALSO_NONFICTION_BESTSELLERS: List[Tuple[str, str]] = [
    ("Donald J. Trump with Tony Schwartz", "Trump: The Art of the Deal"),
    ("William Manchester", "The Last Lion: Alone"),
    ("George Burns", "Gracie: A Love Story"),
    ("Shirley MacLaine", "It's All in the Playing"),
    ("Bernie Siegel", "Love, Medicine & Miracles"),
    ("Robert C. Atkins", "Dr. Atkins' Health Revolution"),
    ("Bill Cosby", "Fatherhood"),
]


# ---------------------------------------------------------------------------
# December 1988 magazines (plausible cover stories, hedged where needed)
# ---------------------------------------------------------------------------
# Each entry: (publication, issue date line, cover-story blurb).
MAGAZINES: List[Tuple[str, str, str]] = [
    (
        "TIME",
        "December 1988",
        "Cover: 'The Year in Review' -- 1988's people, crises and comebacks, "
        "with a preview of the Person of the Year choice.",
    ),
    (
        "Newsweek",
        "December 1988",
        "Cover: 'America's Classrooms' -- the school reform report card, "
        "plus the year-end issues roundtable.",
    ),
    (
        "PC Magazine",
        "December 1988",
        "Cover story: '386 Power' -- a roundup of 25 386-based PCs and "
        "clones tested, with benchmarks for business buyers.",
    ),
    (
        "BYTE",
        "December 1988",
        "Cover: 'The New UNIX Workstations' -- Sun, Apollo and DEC fight "
        "for the engineer's desktop, plus a 386SX lab report.",
    ),
    (
        "Scientific American",
        "December 1988",
        "Cover: 'The Space Telescope' -- a look ahead to the Hubble "
        "launch and what it will show astronomers.",
    ),
    (
        "National Geographic",
        "December 1988",
        "Cover: 'The Coral Kingdom' -- photographing the Great Barrier "
        "Reef, plus a map supplement of the Pacific.",
    ),
    (
        "Popular Science",
        "December 1988",
        "Cover: 'The Best of What's New' -- the year's top 100 innovations "
        "in gadgets, computers and home tech.",
    ),
    (
        "Reader's Digest",
        "December 1988",
        "Holiday issue: 'The True Spirit of Christmas' -- reader stories "
        "and 'Laughter, the Best Medicine.'",
    ),
    (
        "TV Guide",
        "December 1988",
        "Fall season winners and losers: which new shows earned a full "
        "season and which are already gone.",
    ),
    (
        "Sports Illustrated",
        "December 1988",
        "NFL playoff picture special -- plus the winter sports preview "
        "as the ski season opens.",
    ),
]


# ---------------------------------------------------------------------------
# From the Review Desk -- short staff reviews of 1988 books
# ---------------------------------------------------------------------------
# Each entry: (handle, book title, author, review lines).
REVIEWS: List[Tuple[str, str, str, List[str]]] = [
    (
        "PageTurner",
        "The Satanic Verses",
        "Salman Rushdie",
        [
            "A dizzying, magical-realist dream of exile and faith -- "
            "difficult in places, dazzling in others. The opening fall "
            "from the sky is one of the year's great beginnings.",
            "Not a beach read. But the book everyone will be arguing "
            "about at the water cooler this winter.",
        ],
    ),
    (
        "Bookworm88",
        "A Brief History of Time",
        "Stephen Hawking",
        [
            "Black holes, the Big Bang and the nature of time, explained "
            "in prose a bright teenager can follow. Cambridge's most "
            "famous physicist makes cosmology feel personal.",
            "The year's essential science book -- the copy on everyone's "
            "shelf, whether they've finished it or not.",
        ],
    ),
    (
        "NovelIdea",
        "The Queen of the Damned",
        "Anne Rice",
        [
            "The third Vampire Chronicle goes big: rock-star Lestat wakes "
            "the ancient queen and the whole vampire court trembles. "
            "Rice's lushest, loudest entry yet.",
            "Fans of 'Interview with the Vampire' won't want to miss it; "
            "newcomers should start with Lestat's own story first.",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _day(day: Optional[date]) -> date:
    """Resolve the simulation day, defaulting to the session-aware one."""
    if day is not None:
        return day
    try:
        from cis_dynamic import simulation_day
        return simulation_day()
    except Exception:
        return date(1988, 12, 15)


# ---------------------------------------------------------------------------
# Content sections (each returns a list of display lines)
# ---------------------------------------------------------------------------
def fiction_lines(day: Optional[date]) -> List[str]:
    """Hardcover fiction bestsellers for December 1988."""
    d = _day(day)
    author, title = FICTION_NUMBER_ONE
    lines = [
        "HARDCOVER FICTION BESTSELLERS -- DECEMBER 1988",
        f"No. 1: \"{title}\" by {author}",
        "      Jack Ryan is back -- this time inside the Kremlin itself.",
        "",
        "Also among the month's bestselling fiction titles:",
    ]
    for book_author, book_title in ALSO_FICTION_BESTSELLERS:
        lines.append(f"  * \"{book_title}\" -- {book_author}")
    lines.append("")
    pick_author, pick_title = EDITOR_PICKS[d.day % len(EDITOR_PICKS)]
    lines.append(
        f"Editor's pick this week: \"{pick_title}\" by {pick_author}."
    )
    lines.append("Compiled from bookseller reports across the CIS network.")
    return lines


def nonfiction_lines(day: Optional[date]) -> List[str]:
    """Hardcover nonfiction bestsellers for December 1988."""
    _day(day)
    author, title = NONFICTION_NUMBER_ONE
    lines = [
        "HARDCOVER NONFICTION BESTSELLERS -- DECEMBER 1988",
        f"No. 1: \"{title}\" by {author}",
        "      Black holes, the Big Bang and the nature of time -- "
        "the year's science phenomenon.",
        "",
        "Also among the month's bestselling nonfiction titles:",
    ]
    for book_author, book_title in ALSO_NONFICTION_BESTSELLERS:
        lines.append(f"  * \"{book_title}\" -- {book_author}")
    lines.append("")
    lines.append("Compiled from bookseller reports across the CIS network.")
    return lines


def magazines_lines(day: Optional[date]) -> List[str]:
    """December 1988 magazine issues on the newsstand."""
    _day(day)
    lines = [
        "THIS MONTH'S MAGAZINES -- DECEMBER 1988 ISSUES",
        "On the newsstand now:",
        "",
    ]
    for publication, issue, blurb in MAGAZINES:
        lines.append(f"{publication} -- {issue}")
        lines.append(f"  {blurb}")
        lines.append("")
    lines.append(
        "Full text of selected features is available in the Magazine "
        "Back-Issue Library."
    )
    return lines


def reviews_lines(day: Optional[date]) -> List[str]:
    """Short staff reviews of notable 1988 books."""
    _day(day)
    lines = [
        "FROM THE REVIEW DESK",
        "CIS staff critics on notable books of 1988:",
        "",
    ]
    for handle, title, author, review in REVIEWS:
        lines.append(f"\"{title}\" by {author} -- reviewed by {handle}")
        for paragraph in review:
            lines.append(f"  {paragraph}")
        lines.append("")
    lines.append("Have a book to recommend? Leave a note in the CIS Book Club.")
    return lines


def books_menu_lines(day: Optional[date] = None) -> List[Tuple[str, List[str]]]:
    """All four sections as (title, lines) pairs for the menu wire-up."""
    return [
        ("Hardcover Fiction Bestsellers", fiction_lines(day)),
        ("Hardcover Nonfiction Bestsellers", nonfiction_lines(day)),
        ("This Month's Magazines", magazines_lines(day)),
        ("From the Review Desk", reviews_lines(day)),
    ]


def books_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return Books & Magazines sections.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return books_menu_lines()


# ---------------------------------------------------------------------------
# File library seed entries -- magazine back issues (December 1988)
# ---------------------------------------------------------------------------
# (file name, library date, magazine, issue line, description, feature text)
_BACK_ISSUES = [
    (
        "TIME-DEC88.TXT",
        "12/15/88",
        "TIME",
        "TIME -- December 1988",
        "TIME's December 1988 issue: the year-end review edition with the "
        "Person of the Year preview and a 1988 retrospective.",
        "TIME, DECEMBER 1988\n==================\n\nThe Year in Review --\n"
        "1988's people, crises and comebacks, plus a preview of the "
        "Person of the Year choice.\n",
    ),
    (
        "NEWSWEEK-DEC88.TXT",
        "12/12/88",
        "Newsweek",
        "Newsweek -- December 1988",
        "Newsweek's December 1988 issue: 'America's Classrooms' school "
        "reform report card and the year-end issues roundtable.",
        "NEWSWEEK, DECEMBER 1988\n=======================\n\nAmerica's "
        "Classrooms -- the school reform report card.\n",
    ),
    (
        "PCMAG-DEC88.TXT",
        "12/10/88",
        "PC Magazine",
        "PC Magazine -- December 1988",
        "PC Magazine's December 1988 issue: '386 Power' -- a roundup of 25 "
        "386-based PCs and clones tested, with business benchmarks.",
        "PC MAGAZINE, DECEMBER 1988\n==========================\n\n386 "
        "Power -- 25 386 PCs and clones tested and benchmarked.\n",
    ),
    (
        "BYTE-DEC88.TXT",
        "12/08/88",
        "BYTE",
        "BYTE -- December 1988",
        "BYTE's December 1988 issue: the new UNIX workstations face off -- "
        "Sun, Apollo and DEC -- plus a 386SX lab report.",
        "BYTE, DECEMBER 1988\n===================\n\nThe New UNIX "
        "Workstations -- Sun, Apollo and DEC fight for the engineer's "
        "desktop.\n",
    ),
    (
        "SCIAM-DEC88.TXT",
        "12/05/88",
        "Scientific American",
        "Scientific American -- December 1988",
        "Scientific American's December 1988 issue: 'The Space Telescope' "
        "-- a look ahead to the Hubble launch and what it will reveal.",
        "SCIENTIFIC AMERICAN, DECEMBER 1988\n================================"
        "===\n\nThe Space Telescope -- what the Hubble launch will show "
        "astronomers.\n",
    ),
    (
        "NATGEO-DEC88.TXT",
        "12/03/88",
        "National Geographic",
        "National Geographic -- December 1988",
        "National Geographic's December 1988 issue: 'The Coral Kingdom' "
        "-- photographing the Great Barrier Reef.",
        "NATIONAL GEOGRAPHIC, DECEMBER 1988\n================================"
        "====\n\nThe Coral Kingdom -- photographing the Great Barrier Reef.\n",
    ),
    (
        "POPSCI-DEC88.TXT",
        "12/01/88",
        "Popular Science",
        "Popular Science -- December 1988",
        "Popular Science's December 1988 issue: 'The Best of What's New' "
        "-- the year's top 100 innovations in gadgets and home tech.",
        "POPULAR SCIENCE, DECEMBER 1988\n============================\n\n"
        "The Best of What's New -- the year's top 100 innovations.\n",
    ),
    (
        "TVGUIDE-DEC88.TXT",
        "12/06/88",
        "TV Guide",
        "TV Guide -- December 1988",
        "TV Guide's December 1988 issue: fall season winners and losers "
        "-- which new shows earned full seasons and which are gone.",
        "TV GUIDE, DECEMBER 1988\n=======================\n\nFall season "
        "winners and losers -- who survived the ratings.\n",
    ),
]


def seed_files() -> List[Dict[str, object]]:
    """Return magazine back-issue file entries for the file library.

    Each dict matches the computer_communities.json ``files`` entry shape
    (content_id, library, name, description, date, version, system,
    instructions, history, reviews, content). The coordinator merges these
    into the file library.
    """
    entries: List[Dict[str, object]] = []
    for filename, lib_date, magazine, issue, description, text in _BACK_ISSUES:
        entries.append(
            {
                "content_id": f"community-file:{filename}",
                "library": "dos_library",
                "name": filename,
                "description": description,
                "date": lib_date,
                "version": "1.0",
                "system": "Plain ASCII text -- any terminal or PC",
                "instructions": "ASCII text file. Download and read with any text viewer or editor. Original simulation content.",
                "history": ["1.0: Archived from the December 1988 newsstand."],
                "reviews": [],
                "content": text + "\n" + "Filed under " + issue + ".\n",
            }
        )
    return entries


if __name__ == "__main__":
    for title, lines in books_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
