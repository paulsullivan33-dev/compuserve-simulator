"""Sports & TV service for the December 1988 simulation setting.

Pure content + logic module: late-1988 NFL standings and scores, the
1988-89 prime-time TV grid, and the 1988-89 MLB hot stove. All content
functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page).

Standings records marked VERIFIED were confirmed against season
records; a few AFC West non-leader records are marked as estimates.
Scores shown are verified Week 15/16 (early/mid December 1988) results.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1988 NFL season: final regular-season standings
# ---------------------------------------------------------------------------
# Format: (team name, wins, losses, ties, verified?)
# verified=True means the record was checked against published 1988 season
# records; verified=False means an estimate (clearly labeled in output).
NFL_STANDINGS: Dict[str, List[Tuple[str, int, int, int, bool]]] = {
    "AFC EAST": [
        ("Buffalo Bills", 12, 4, 0, True),
        ("Indianapolis Colts", 9, 7, 0, True),
        ("New England Patriots", 9, 7, 0, True),
        ("New York Jets", 8, 7, 1, True),
        ("Miami Dolphins", 6, 10, 0, True),
    ],
    "AFC CENTRAL": [
        ("Cincinnati Bengals", 12, 4, 0, True),
        ("Cleveland Browns", 10, 6, 0, True),
        ("Houston Oilers", 10, 6, 0, True),
        ("Pittsburgh Steelers", 5, 11, 0, True),
    ],
    "AFC WEST": [
        ("Seattle Seahawks", 9, 7, 0, True),
        ("Denver Broncos", 8, 8, 0, False),
        ("Los Angeles Raiders", 7, 9, 0, False),
        ("San Diego Chargers", 6, 10, 0, False),
        ("Kansas City Chiefs", 4, 11, 1, False),
    ],
    "NFC EAST": [
        ("Philadelphia Eagles", 10, 6, 0, True),
        ("New York Giants", 10, 6, 0, True),
        ("Washington Redskins", 7, 9, 0, True),
        ("Phoenix Cardinals", 7, 9, 0, True),
        ("Dallas Cowboys", 3, 13, 0, True),
    ],
    "NFC CENTRAL": [
        ("Chicago Bears", 12, 4, 0, True),
        ("Minnesota Vikings", 11, 5, 0, True),
        ("Tampa Bay Buccaneers", 5, 11, 0, True),
        ("Detroit Lions", 4, 12, 0, True),
        ("Green Bay Packers", 4, 12, 0, True),
    ],
    "NFC WEST": [
        ("San Francisco 49ers", 10, 6, 0, True),
        ("Los Angeles Rams", 10, 6, 0, True),
        ("New Orleans Saints", 10, 6, 0, True),
        ("Atlanta Falcons", 5, 11, 0, True),
    ],
}

# Verified late-season 1988 results: (week, visitor, visitor_score,
# home, home_score, date string).
NFL_SCORES: List[Tuple[str, str, int, str, int, str]] = [
    ("Week 16", "Philadelphia Eagles", 23, "Dallas Cowboys", 7, "Dec 18"),
    ("Week 16", "Los Angeles Rams", 38, "San Francisco 49ers", 16, "Dec 18"),
    ("Week 16", "Cleveland Browns", 28, "Houston Oilers", 23, "Dec 18"),
    ("Week 16", "Indianapolis Colts", 17, "Buffalo Bills", 14, "Dec 18"),
    ("Week 16", "New Orleans Saints", 10, "Atlanta Falcons", 9, "Dec 18"),
    ("Week 16", "Pittsburgh Steelers", 40, "Miami Dolphins", 24, "Dec 18"),
    ("Week 16", "Seattle Seahawks", 43, "Los Angeles Raiders", 37, "Dec 18"),
    ("Week 15", "Philadelphia Eagles", 23, "Phoenix Cardinals", 17, "Dec 10"),
    ("Week 14", "Washington Redskins", 20, "Philadelphia Eagles", 19, "Dec 4"),
]

# Rotating "this week" highlights, chosen deterministically by calendar day.
NFL_HIGHLIGHTS: List[Tuple[str, str]] = [
    ("WEST COAST SHOWDOWN",
     "The Rams routed the 49ers 38-16 in the Dec 18 finale at Candlestick, "
     "forcing a three-way 10-6 logjam atop the NFC West. San Francisco still "
     "takes the division crown on tiebreakers."),
    ("SEATTLE'S FIRST CROWN",
     "The Seahawks outgunned the Raiders 43-37 in a Week 16 shootout to win "
     "their first AFC West title -- at just 9-7. The Kingdome is playoff-bound."),
    ("FOG BOWL LOOMS",
     "Buddy Ryan's Eagles (10-6) travel to Soldier Field to face the Bears "
     "(12-4) in the divisional round on New Year's Eve. Bundle up, Philly."),
    ("BENGALS ON TOP",
     "Cincinnati (12-4) wrapped up the AFC's best record and home-field "
     "advantage. Boomer Esiason's crew hosts the Seahawks in the divisional "
     "playoffs on Dec 31."),
    ("BUFFALO'S WINDOW",
     "The Bills (12-4) claimed the AFC East back in November and host a "
     "divisional playoff game -- but that Week 16 loss to the Colts cost "
     "them home-field advantage."),
    ("ROAD TO MIAMI",
     "The divisional playoffs kick off Dec 31. The road ends at Joe Robbie "
     "Stadium in Miami on January 22 -- Super Bowl XXIII."),
]


# ---------------------------------------------------------------------------
# 1988-89 prime-time TV grid (weeknight, Eastern/Pacific)
# ---------------------------------------------------------------------------
# Placements follow the fall 1988 network schedules. Notes:
#  - The 1988 writers' strike pushed most premieres to late October/November,
#    so December is "late fall" -- Moonlighting and thirtysomething anchor
#    ABC Tuesdays, Murphy Brown is settling in on CBS Mondays.
#  - Night Court moved to NBC Wednesdays at 9 for the 1988-89 season.
TV_GRID: Dict[str, Dict[str, str]] = {
    "SUNDAY": {
        "ABC": "Mission: Impossible / ABC Sunday Night Movie",
        "CBS": "60 Minutes / Murder, She Wrote / CBS Sunday Movie",
        "FOX": "21 Jump Street / America's Most Wanted / Married...with Children",
        "NBC": "Magical World of Disney / Family Ties / Day by Day / NBC Sunday Movie",
    },
    "MONDAY": {
        "ABC": "MacGyver / Monday Night Football",
        "CBS": "Newhart / Murphy Brown / Designing Women",
        "FOX": "Local programming",
        "NBC": "ALF / The Hogan Family / NBC Monday Night Movie",
    },
    "TUESDAY": {
        "ABC": "Who's the Boss? / Roseanne / Moonlighting / thirtysomething",
        "CBS": "CBS Tuesday Night Movie",
        "FOX": "Local programming",
        "NBC": "Matlock / In the Heat of the Night / Midnight Caller",
    },
    "WEDNESDAY": {
        "ABC": "Growing Pains / Head of the Class / ABC Wednesday Night Movie",
        "CBS": "The Equalizer / Wiseguy",
        "FOX": "Local programming",
        "NBC": "Unsolved Mysteries / Night Court / Tattingers",
    },
    "THURSDAY": {
        "ABC": "Knightwatch / Dynasty",
        "CBS": "48 Hours / Knots Landing",
        "FOX": "Local programming",
        "NBC": "The Cosby Show / A Different World / Cheers / Dear John / L.A. Law",
    },
    "FRIDAY": {
        "ABC": "Perfect Strangers / Full House / Mr. Belvedere / 20/20",
        "CBS": "Beauty and the Beast / Dallas / Falcon Crest",
        "FOX": "COPS / The Reporters",
        "NBC": "Sonny Spoon / Miami Vice",
    },
    "SATURDAY": {
        "ABC": "ABC Saturday Night Movie",
        "CBS": "Dirty Dancing / Raising Miranda / Simon & Simon",
        "FOX": "The Reporters / Beyond Tomorrow",
        "NBC": "227 / Amen / The Golden Girls / Empty Nest / Hunter",
    },
}

# Nielsen season-to-date bragging rights (1988-89 season rankings).
TV_TOP_TEN = [
    ("The Cosby Show", "NBC", 1),
    ("Roseanne", "ABC", 2),
    ("A Different World", "NBC", 3),
    ("Cheers", "NBC", 4),
    ("60 Minutes", "CBS", 5),
    ("The Golden Girls", "NBC", 6),
    ("Who's the Boss?", "ABC", 7),
    ("Murder, She Wrote", "CBS", 8),
    ("Empty Nest", "NBC", 9),
    ("Anything but Love", "ABC", 10),
]

TV_HIGHLIGHTS = [
    "Roseanne is the season's breakout -- the #2 show in America in its first year.",
    "NBC owns Thursday: Cosby, A Different World, Cheers, Dear John, L.A. Law -- must-see TV before it had a name.",
    "Murphy Brown is the new kid on CBS Mondays and critics are already buzzing.",
    "Moonlighting returned to ABC Tuesdays after the strike-delayed fall -- the Moonlighting curse is the water-cooler topic.",
    "The Golden Girls anchor NBC Saturdays at 9 -- still top 10 in year four.",
]


# ---------------------------------------------------------------------------
# 1988-89 MLB hot stove (kept generic-but-labeled; no fabricated signings)
# ---------------------------------------------------------------------------
MLB_STORIES = [
    "The Dodgers shocked baseball in October, beating Oakland 4 games to 1 "
    "for the World Series crown.",
    "Kirk Gibson's pinch-hit, walk-off homer off Dennis Eckersley in Game 1 "
    "-- on one good leg -- is already the stuff of legend.",
    "Orel Hershiser was untouchable: a record 59 straight scoreless innings "
    "down the stretch, then World Series MVP honors.",
    "The Winter Meetings are the talk of the hot stove league -- phones are "
    "ringing, but GMs are playing their cards close.",
    "Oakland's Bash Brothers -- Canseco and McGwire -- combined for 74 "
    "homers. Nobody wants to face that lineup in '89.",
    "The Mets won 100 games and watched it all slip away in the NLCS. "
    "Shea Stadium is restless.",
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


def _record(team: Tuple[str, int, int, int, bool]) -> str:
    name, wins, losses, ties, verified = team
    record = f"{wins}-{losses}" if ties == 0 else f"{wins}-{losses}-{ties}"
    return f"{name:<26} {record:<8}" + ("" if verified else " (est.)")


# ---------------------------------------------------------------------------
# Content sections (each returns a list of display lines)
# ---------------------------------------------------------------------------
def nfl_lines(day: Optional[date] = None) -> List[str]:
    """NFL late-1988 standings, verified scores, and the day's highlight."""
    lines = [
        "NFL 1988 -- FINAL REGULAR SEASON",
        "Regular season ended Dec 18. Playoffs begin Dec 31.",
        "",
    ]
    for division, teams in NFL_STANDINGS.items():
        lines.append(division)
        lines.append("-" * len(division))
        lines.extend(_record(team) for team in teams)
        lines.append("")
    lines.append("LATE-SEASON SCORES (verified)")
    lines.append("----------------------------")
    for week, visitor, vscore, home, hscore, when in NFL_SCORES:
        lines.append(f"{week} ({when}): {visitor} {vscore}, {home} {hscore}")
    lines.append("")
    day = _day(day)
    title, text = NFL_HIGHLIGHTS[day.day % len(NFL_HIGHLIGHTS)]
    lines.extend(["THIS WEEK: " + title, text])
    lines.append("")
    lines.append("Division winners: Bills, Bengals, Seahawks, Bears, Eagles, 49ers.")
    lines.append("Records marked (est.) are unofficial.")
    return lines


def tv_lines(day: Optional[date] = None) -> List[str]:
    """Prime-time weeknight TV grid for the 1988-89 season."""
    lines = [
        "PRIME-TIME TV GRID -- DECEMBER 1988",
        "All times Eastern/Pacific. Late-fall schedule (post writers' strike).",
        "",
    ]
    for night in ("SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY",
                  "THURSDAY", "FRIDAY", "SATURDAY"):
        lines.append(night)
        lines.append("-" * len(night))
        for network in ("ABC", "CBS", "FOX", "NBC"):
            lines.append(f"  {network:<4} {TV_GRID[night][network]}")
        lines.append("")
    lines.append("TOP 10 THIS SEASON (Nielsen)")
    lines.append("---------------------------")
    for show, network, rank in TV_TOP_TEN:
        lines.append(f"  {rank:>2}. {show} ({network})")
    lines.append("")
    day = _day(day)
    lines.append("TV BUZZ: " + TV_HIGHLIGHTS[day.day % len(TV_HIGHLIGHTS)])
    return lines


def mlb_lines(day: Optional[date] = None) -> List[str]:
    """1988-89 MLB hot stove: Dodgers' October triumph, winter rumors."""
    day = _day(day)
    lines = [
        "MLB HOT STOVE -- WINTER 1988-89",
        "World Series: Dodgers 4, Athletics 1 (October 1988)",
        "",
    ]
    start = day.day % len(MLB_STORIES)
    ordered = MLB_STORIES[start:] + MLB_STORIES[:start]
    for story in ordered:
        lines.append("* " + story)
    lines.append("")
    lines.append("Spring training opens in February. Pitchers and catchers soon.")
    return lines


def sports_menu_lines(day: Optional[date] = None) -> List[Tuple[str, List[str]]]:
    """All three sections as (title, lines) pairs for the menu wire-up."""
    return [
        ("NFL", nfl_lines(day)),
        ("TV", tv_lines(day)),
        ("MLB", mlb_lines(day)),
    ]


def sports_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return Sports & TV sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return sports_menu_lines()


if __name__ == "__main__":
    for title, lines in sports_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
