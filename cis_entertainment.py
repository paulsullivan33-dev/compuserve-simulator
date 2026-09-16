"""Entertainment service for the December 1988 simulation setting.

Pure content + logic module: the Billboard Hot 100 for December 1988,
movie reviews for films in theaters that month, and previews of the
Jan 2, 1989 college bowl games (written as previews -- never results).
All content functions accept an optional ``day`` parameter defaulting
to ``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page).

FACT CARE: only the #1 slots we are sure of are asserted (Chicago's
"Look Away" early in the month, Poison's "Every Rose Has Its Thorn"
Christmas week); everything else is presented as "also charting" with
no false position numbers. No content is dated after December 1988.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Billboard Hot 100 -- December 1988
# ---------------------------------------------------------------------------
# #1 slots we are confident about:
#   * "Look Away" -- Chicago -- #1 around the Dec 10 chart week
#   * "Every Rose Has Its Thorn" -- Poison -- #1 Christmas week 1988
# Everything else is listed as "also charting" in no asserted order.
NUMBER_ONE_BY_WEEK: Dict[int, Tuple[str, str]] = {
    # Simulation-day cutoff (day of December) -> (artist, title)
    17: ("Chicago", "Look Away"),
    32: ("Poison", "Every Rose Has Its Thorn"),
}

ALSO_CHARTING: List[Tuple[str, str]] = [
    ("Bobby Brown", "My Prerogative"),
    ("Debbie Gibson", "Rush Hour"),
    ("George Michael", "Kissing a Fool"),
    ("Anita Baker", "Giving You the Best That I Got"),
    ("Beach Boys", "Kokomo"),
    ("Will to Power", "Baby I Love Your Way / Freebird Medley"),
    ("Boy Meets Girl", "Waiting for a Star to Fall"),
    ("Richard Marx", "Endless Summer Nights"),
    ("Milli Vanilli", "Girl You Know It's True"),
    ("Duran Duran", "I Don't Want Your Love"),
    ("Eddie Money", "Walk On Water"),
    ("Kylie Minogue", "The Loco-Motion"),
    ("Escape Club", "Wild, Wild West"),
    ("Bon Jovi", "Bad Medicine"),
    ("Taylor Dayne", "I'll Always Love You"),
    ("Poison", "Fallen Angel"),
    ("Winger", "Seventeen"),
    ("Information Society", "Walking Away"),
]

CHART_NOTES = [
    "Chicago's power ballad sits atop the chart early in the month.",
    "Poison's acoustic ballad climbs to #1 for Christmas week -- the band's first chart-topper.",
    "Bobby Brown's 'My Prerogative' is the hottest climber on the chart.",
]


# ---------------------------------------------------------------------------
# Movie reviews -- films in theaters December 1988
# ---------------------------------------------------------------------------
# Each entry: (title, release date, star rating /5, review blurb).
# Only films released on or before December 1988 appear here.
MOVIE_REVIEWS: List[Tuple[str, str, str, str]] = [
    (
        "RAIN MAN",
        "Released Dec 16, 1988",
        "****",
        "Dustin Hoffman disappears into Raymond, an autistic savant, on a "
        "cross-country road trip with his hustler brother (Tom Cruise, "
        "excellent). Barry Levinson's road movie is funny, then quietly "
        "devastating. Oscar buzz is already building.",
    ),
    (
        "TWINS",
        "Released Dec 9, 1988",
        "***1/2",
        "Arnold Schwarzenegger and Danny DeVito as unlikely twins -- the "
        "casting gag is the whole movie, and it works. Ivan Reitman keeps "
        "it light, and Arnold's comic timing surprises everyone.",
    ),
    (
        "THE NAKED GUN",
        "Released Dec 2, 1988",
        "****",
        "Leslie Nielsen's deadpan Lt. Frank Drebin anchors a "
        "joke-a-minute spoof of police procedurals from the Airplane! "
        "team. Not every gag lands, but the ones that do are classics.",
    ),
    (
        "SCROOGED",
        "Released Nov 23, 1988",
        "***1/2",
        "Bill Murray updates Dickens as a cynical TV executive haunted on "
        "Christmas Eve. Darker than the trailers suggest, but Murray's "
        "redemption speech is worth the price of admission.",
    ),
    (
        "WORKING GIRL",
        "Released Dec 21, 1988",
        "***1/2",
        "Melanie Griffith's Staten Island secretary outsmarts the "
        "Manhattan merger crowd. Mike Nichols' comedy has brains, heart, "
        "and a terrific Harrison Ford. A holiday crowd-pleaser.",
    ),
    (
        "DIE HARD",
        "Released Jul 15, 1988 (summer holdover)",
        "****",
        "Bruce Willis's wisecracking NY cop takes on terrorists in an LA "
        "skyscraper -- the action movie every other action movie is now "
        "trying to copy. Still playing select second-run houses.",
    ),
    (
        "WHO FRAMED ROGER RABBIT",
        "Released Jun 22, 1988 (summer holdover)",
        "****1/2",
        "Robert Zemeckis blends toons and live action like nothing before "
        "it. Bob Hoskins plays it straight opposite a rabbit, and somehow "
        "it all works. A technical marvel and a genuinely good noir.",
    ),
]

MOVIE_NOTE = (
    "Ratings: ****1/2 = must see, **** = excellent, ***1/2 = very good, "
    "*** = good. From the CompuServe Online Magazine film desk."
)


# ---------------------------------------------------------------------------
# Bowl game previews -- 1988 season, played Jan 2, 1989
# ---------------------------------------------------------------------------
# These are PREVIEWS only (written in the December 1988 setting). No
# scores, no winners asserted -- just matchups, stakes, and storylines.
# Format: (bowl, matchup, location, date, storyline).
BOWL_PREVIEWS: List[Tuple[str, str, str, str, str]] = [
    (
        "FIESTA BOWL",
        "#1 Notre Dame vs #3 West Virginia",
        "Tempe, Arizona",
        "Jan 2 (NBC)",
        "The big one. Two unbeaten teams -- Lou Holtz's Irish (11-0) and "
        "Don Nehlen's Mountaineers (11-0) -- meet with the national title "
        "essentially on the line. Major Harris vs. the Irish defense is "
        "the matchup everyone will be watching.",
    ),
    (
        "ORANGE BOWL",
        "#2 Miami vs #6 Nebraska",
        "Miami, Florida",
        "Jan 2 (NBC)",
        "The Hurricanes (10-1) defend their home turf against Tom "
        "Osborne's Cornhuskers (11-1) in the nightcap. Miami needs help "
        "in Tempe to repeat as champions, but first it has to handle "
        "Nebraska's punishing ground game.",
    ),
    (
        "SUGAR BOWL",
        "#4 Florida State vs #7 Auburn",
        "New Orleans, Louisiana",
        "Jan 2 (ABC)",
        "Bobby Bowden's Seminoles (10-1) and Pat Dye's Tigers (10-1) "
        "square off in the Superdome. Auburn's defense against FSU's "
        "speed -- a classic SEC-vs.-independent slugfest to close out "
        "New Year's Day.",
    ),
    (
        "ROSE BOWL",
        "#11 Michigan vs #5 USC",
        "Pasadena, California",
        "Jan 2 (NBC)",
        "Bo Schembechler's Wolverines (8-2-1) face Larry Smith's Trojans "
        "(10-1) in the granddaddy of them all. USC's Rodney Peete leads "
        "an offense built for the big stage; Michigan brings its usual "
        "bruising ground game.",
    ),
    (
        "COTTON BOWL",
        "#9 UCLA vs #8 Arkansas",
        "Dallas, Texas",
        "Jan 2 (CBS)",
        "Terry Donahue's Bruins (10-1) and Ken Hatfield's Razorbacks "
        "(10-1) meet at the Cotton Bowl. Arkansas's flexbone wishbone "
        "against UCLA's Troy Aikman-led passing attack -- a fascinating "
        "style clash to open the New Year.",
    ),
]

BOWL_INTRO = (
    "All five major bowls kick off on Monday, January 2, 1989. "
    "Rankings are the final regular-season polls. Settle in -- "
    "the national championship picture gets decided in one afternoon."
)


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


def _number_one(day: date) -> Tuple[str, str]:
    """Return the asserted #1 (artist, title) for this simulation day."""
    for cutoff, entry in sorted(NUMBER_ONE_BY_WEEK.items()):
        if day.day < cutoff:
            return entry
    return list(NUMBER_ONE_BY_WEEK.values())[-1]


# ---------------------------------------------------------------------------
# Content sections (each returns a list of display lines)
# ---------------------------------------------------------------------------
def chart_lines(day: Optional[date] = None) -> List[str]:
    """Billboard Hot 100 snapshot for the simulation week in Dec 1988."""
    day = _day(day)
    artist, title = _number_one(day)
    lines = [
        "BILLBOARD HOT 100 -- DECEMBER 1988",
        f"Chart week of December {day.day}, 1988 (simulated).",
        "",
        f"  #1  {artist} -- \"{title}\"",
        "",
        "ALSO CHARTING THIS MONTH (in no asserted order)",
        "-----------------------------------------------",
    ]
    # Rotate the "also charting" list slightly by week, like the sports
    # highlights do, so repeat visits feel fresh.
    start = (day.day // 7) % len(ALSO_CHARTING)
    ordered = ALSO_CHARTING[start:] + ALSO_CHARTING[:start]
    for a, t in ordered:
        lines.append(f"  *   {a} -- \"{t}\"")
    lines.append("")
    lines.append("CHART NOTE: " + CHART_NOTES[day.day % len(CHART_NOTES)])
    return lines


def movies_lines(day: Optional[date] = None) -> List[str]:
    """Short CompuServe-magazine-style reviews of Dec 1988 releases."""
    day = _day(day)
    lines = [
        "AT THE MOVIES -- DECEMBER 1988",
        MOVIE_NOTE,
        "",
    ]
    # Rotate review order by week so the "lead" review changes.
    start = (day.day // 7) % len(MOVIE_REVIEWS)
    ordered = MOVIE_REVIEWS[start:] + MOVIE_REVIEWS[:start]
    for title, released, stars, blurb in ordered:
        lines.append(title)
        lines.append("-" * len(title))
        lines.append(f"  {released}   {stars}")
        lines.append("  " + blurb)
        lines.append("")
    return lines


def bowls_lines(day: Optional[date] = None) -> List[str]:
    """Previews of the Jan 2, 1989 bowl games (1988 season)."""
    _day(day)  # resolved for signature parity; previews are date-agnostic
    lines = [
        "BOWL GAME PREVIEWS -- 1988 SEASON",
        BOWL_INTRO,
        "",
    ]
    for bowl, matchup, location, when, story in BOWL_PREVIEWS:
        lines.append(bowl)
        lines.append("-" * len(bowl))
        lines.append(f"  {matchup}")
        lines.append(f"  {location} -- {when}")
        lines.append("  " + story)
        lines.append("")
    lines.append("Previews only -- games kick off Jan 2.")
    return lines


def entertainment_menu_lines(day: Optional[date] = None) -> List[Tuple[str, List[str]]]:
    """All three sections as (title, lines) pairs for the menu wire-up."""
    return [
        ("Billboard Hot 100", chart_lines(day)),
        ("Movies", movies_lines(day)),
        ("Bowl Previews", bowls_lines(day)),
    ]


def entertainment_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return Entertainment sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return entertainment_menu_lines()


if __name__ == "__main__":
    for title, lines in entertainment_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
