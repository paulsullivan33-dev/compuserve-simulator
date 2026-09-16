"""1988 Year in Review news special for the December 1988 simulation setting.

Pure content + logic module: wire-service retrospective coverage of the
year's defining stories -- the November 8 presidential election, the
December 7 Armenia earthquake, developing coverage of Pan Am Flight 103
(Dec 21+ only), and best-of-1988 roundups (movies, music, sports, tech).
All content functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page).

Facts marked VERIFIED were confirmed against published 1988 records;
items marked with "(by most accounts)" are widely reported but not
independently confirmed for this module. Tragic events are presented in
a sober wire-service tone with no sensationalism. Nothing in this
module references anything after December 1988.

Date gating: the Pan Am Flight 103 developing story appears ONLY on
simulation days December 21 and later. On earlier December dates it is
entirely absent (no teaser, no section, no mention). The Armenia
earthquake wire copy appears only on December 7 and later, since the
quake struck on December 7.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple


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
# Verified: Bush/Quayle 426 electoral votes, Dukakis/Bentsen 111
# (one West Virginia elector voted Bentsen for president); popular vote
# 53.4% to 45.6%; election held November 8, 1988; Democrats retained
# control of both houses of Congress.
ELECTION_RESULT = {
    "date": "November 8, 1988",
    "winner": "George H. W. Bush",
    "winner_mate": "Dan Quayle",
    "loser": "Michael Dukakis",
    "loser_mate": "Lloyd Bentsen",
    "electoral_winner": 426,
    "electoral_loser": 111,
    "popular_pct": "53.4% to 45.6%",
}


def election_lines(day: Optional[date] = None) -> List[str]:
    """Wire retrospective of the November 1988 presidential election."""
    _ = _day(day)  # Election was November 8; no gating needed.
    r = ELECTION_RESULT
    return [
        "ELECTION '88 -- BUSH WINS THE WHITE HOUSE",
        f"Voters went to the polls {r['date']}, and the verdict",
        "was decisive:",
        "",
        f"  {r['winner']} (R) / {r['winner_mate']}",
        f"    {r['electoral_winner']} electoral votes",
        f"  {r['loser']} (D) / {r['loser_mate']}",
        f"    {r['electoral_loser']} electoral votes",
        f"  Popular vote: Bush {r['popular_pct']}",
        "",
        "The sitting vice president becomes the first incumbent vice",
        "president since Martin Van Buren in 1836 to win election as",
        "president. Democrats, however, retained control of both the",
        "House and the Senate.",
        "",
        "President-elect Bush takes the oath of office in January.",
        "In his acceptance speech in Houston, Bush pledged to be",
        "'president of all the people' and spoke of his hope for",
        "'a kinder, gentler nation.'",
    ]


def disaster_lines(day: Optional[date] = None) -> List[str]:
    """Wire copy on the December 7, 1988 Armenia earthquake.

    Returns an empty list before December 7 (the quake had not
    happened yet on those simulation days).
    """
    d = _day(day)
    if d < date(1988, 12, 7):
        return []
    return [
        "ARMENIA EARTHQUAKE -- SPITAK, DECEMBER 7, 1988",
        "(VERIFIED FACTS)",
        "",
        "At 11:41 a.m. local time, a powerful earthquake struck",
        "northern Armenia, then part of the Soviet Union. The epicenter",
        "was near the town of Spitak; the quake measured about",
        "magnitude 6.8. Minutes later, a magnitude 5.8 aftershock",
        "toppled structures weakened by the first shock.",
        "",
        "Spitak was nearly leveled. Leninakan and Kirovakan suffered",
        "catastrophic damage. Soviet authorities reported more than",
        "25,000 people killed and up to 130,000 injured.",
        "",
        "Rescue teams from across the Soviet Union and from more than",
        "a hundred countries converged on the region. The relief",
        "effort continues this month, with winter compounding the",
        "misery of survivors in temporary shelters.",
        "",
        "Soviet leader Mikhail Gorbachev cut short a foreign trip to",
        "survey the devastation personally.",
    ]


def panam_lines(day: Optional[date] = None) -> List[str]:
    """Developing coverage of Pan Am Flight 103 -- Dec 21+ ONLY.

    Returns an empty list on simulation dates before December 21.
    On December 21 and later, presented as developing/breaking news:
    cause under investigation, numbers as reported, no post-1988
    attributions.
    """
    d = _day(day)
    if d < date(1988, 12, 21):
        return []
    header = [
        "*** DEVELOPING STORY ***",
        "PAN AM FLIGHT 103 DOWN OVER SCOTLAND",
        "(VERIFIED FACTS)",
        "",
        "Pan Am Flight 103, a Boeing 747 bound from London Heathrow",
        "for New York, broke apart in flight on the evening of",
        "December 21 and came down over the town of Lockerbie,",
        "Scotland. All 259 passengers and crew aboard were killed.",
        "Falling wreckage struck homes in Lockerbie, killing 11",
        "residents on the ground -- 270 lives lost in all.",
        "",
        "About 190 of those aboard were American citizens, many of",
        "them college students returning home for the holidays.",
        "",
        "The cause is under investigation. Debris is spread over a",
        "wide area and recovery teams are working through the night.",
    ]
    if d >= date(1988, 12, 22):
        header.extend([
            "",
            "December 22 update: investigators say the aircraft broke",
            "up at cruising altitude. Aviation officials warn that",
            "the inquiry will take many months.",
        ])
    return header


# ---------------------------------------------------------------------------
# Best of 1988 (facts noted where verified; hedged where not)
# ---------------------------------------------------------------------------
# Verified: Rain Man was the top domestic box-office film of 1988.
# No Best Picture winner is named: that award is presented after the
# December 1988 simulation window, so only "contender" language is used.
MOVIES_1988: List[Tuple[str, str]] = [
    ("Rain Man", "the year's top-grossing release; a Best Picture contender"),
    ("Who Framed Roger Rabbit",
     "live action and animation blended to rave reviews"),
    ("Coming to America",
     "Eddie Murphy's royal comedy, among the year's hits"),
    ("Die Hard", "the action surprise that made Bruce Willis a movie star"),
    ("Big", "Tom Hanks charms as the boy in a grown man's body"),
    ("Twins", "Schwarzenegger and DeVito, an unlikely box-office pair"),
    ("Mississippi Burning", "among the year's most-discussed dramas"),
    ("Rain Man / Roger Rabbit / Die Hard",
     "most-cited in year-end polls"),
]

# Billboard's year-end Hot 100 for 1988 is widely reported as led by
# George Michael's "Faith"; the rest are presented as among the year's
# biggest songs. Award shows held after the simulation window are not
# mentioned.
MUSIC_1988: List[Tuple[str, str]] = [
    ("Faith -- George Michael",
     "by most accounts, the year's biggest single"),
    ("Sweet Child o' Mine -- Guns N' Roses", "the summer's rock anthem"),
    ("Roll With It -- Steve Winwood",
     "among the year's most-played singles"),
    ("Man in the Mirror -- Michael Jackson",
     "among the year's most-played singles"),
    ("Got My Mind Set on You -- George Harrison",
     "a comeback hit of the year"),
    ("One Moment in Time -- Whitney Houston",
     "the Seoul Olympic summer anthem"),
    ("Faith -- George Michael (album)",
     "among the year's top-selling albums"),
    ("Tracy Chapman -- Tracy Chapman",
     "the quiet debut that critics kept naming"),
    ("Appetite for Destruction -- Guns N' Roses",
     "broke through big in 1988"),
    ("Bad -- Michael Jackson",
     "continued its chart run through the year"),
]

# Verified: Dodgers beat the Athletics 4-1 in the October 1988 World
# Series (Kirk Gibson's Game 1 home run); Seoul hosted the 1988 Summer
# Olympics; Calgary hosted the 1988 Winter Olympics; Mike Tyson knocked
# out Michael Spinks in 91 seconds in June 1988.
SPORTS_1988: List[str] = [
    "BASEBALL: Los Angeles Dodgers 4, Oakland Athletics 1. Kirk Gibson's",
    "  Game 1 walk-off homer set the tone for an October upset. (VERIFIED)",
    "SUMMER OLYMPICS (Seoul): Carl Lewis's 100-meter gold after Ben",
    "  Johnson's disqualification; Florence Griffith Joyner and Janet",
    "  Evans among the American stars. (VERIFIED)",
    "WINTER OLYMPICS (Calgary, Feb. 1988): the 'Battle of the Brians'",
    "  in figure skating; the Jamaican bobsled team charmed the world.",
    "  (VERIFIED)",
    "BOXING: Mike Tyson knocked out Michael Spinks in 91 seconds in",
    "  June, unifying the heavyweight crown. (VERIFIED)",
    "NFL: the regular season just ended December 18; the playoffs begin",
    "  December 31. See the Sports & TV menu for full coverage.",
]

# Verified: NeXT Computer introduced October 12, 1988; IBM AS/400
# launched June 1988; TAT-8, the first transatlantic fiber-optic
# cable, entered service in December 1988; the Morris worm spread
# across ARPANET in November 1988. Macintosh IIx (September 1988)
# is widely reported but hedged here.
TECH_1988: List[str] = [
    "Steve Jobs unveiled the NeXT Computer in October, his first",
    "  machine since leaving Apple -- a black cube with a magneto-",
    "  optical drive and object-oriented NeXTSTEP software. (VERIFIED)",
    "IBM's AS/400 midrange line, launched in June, became one of the",
    "  company's fastest-selling systems ever. (VERIFIED)",
    "TAT-8, the first transatlantic fiber-optic telephone cable,",
    "  entered service this month, carrying 40,000 calls at once.",
    "  (VERIFIED)",
    "The Morris worm spread across the ARPANET in November, the",
    "  first major Internet security incident. (VERIFIED)",
    "Apple's Macintosh IIx, introduced in September, is among the",
    "  year's notable workstation upgrades (by most accounts).",
]


def bestof_lines(day: Optional[date] = None) -> List[str]:
    """Best-of-1988 roundups: movies, music, sports, tech."""
    _ = _day(day)  # Retrospective of the full year; no gating.
    lines = [
        "BEST OF 1988 -- THE YEAR IN CULTURE",
        "",
        "MOVIES",
        "------",
    ]
    for title, note in MOVIES_1988:
        lines.append(f"  {title} -- {note}")
    lines.extend(["", "MUSIC", "-----"])
    for title, note in MUSIC_1988:
        lines.append(f"  {title} -- {note}")
    lines.extend(["", "SPORTS", "------"])
    lines.extend(
        ("  " + s if not s.startswith("  ") else s) for s in SPORTS_1988
    )
    lines.extend(["", "TECHNOLOGY", "----------"])
    lines.extend("  " + s if not s.startswith("  ") else s for s in TECH_1988)
    lines.extend([
        "",
        "Figures marked VERIFIED were confirmed against 1988 records;",
        "items marked 'by most accounts' are widely reported.",
    ])
    return lines


# ---------------------------------------------------------------------------
# Menu / service entry points
# ---------------------------------------------------------------------------
def yearend_menu_lines(
    day: Optional[date] = None,
) -> List[Tuple[str, List[str]]]:
    """All year-end sections as (title, lines) pairs for the menu wire-up.

    Date-gated sections (Pan Am before Dec 21, Armenia before Dec 7)
    are omitted entirely on earlier simulation days.
    """
    d = _day(day)
    sections: List[Tuple[str, List[str]]] = [
        ("Election '88", election_lines(d)),
        ("Armenia Earthquake", disaster_lines(d)),
        ("Pan Am Flight 103", panam_lines(d)),
        ("Best of 1988", bestof_lines(d)),
    ]
    return [(title, lines) for title, lines in sections if lines]


def yearend_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return year-end sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return yearend_menu_lines()


def yearend_menu(app, day: Optional[date] = None) -> None:
    """Interactive '1988 Year in Review' submenu.

    Follows the sports_menu() convention: numbered sections, text_page
    for each, M to return. All interactive output goes through
    ``app.ansi_scroll``.
    """
    d = _day(day)
    sections = yearend_menu_lines(d)
    while True:
        app.clear()
        app.header_bar("news")
        app.ansi_scroll("1988 YEAR IN REVIEW", 0.01)
        app.ansi_scroll("------------------", 0.01)
        for index, (title, _lines) in enumerate(sections, 1):
            app.ansi_scroll(f"{index}  {title}", 0.01)
        app.ansi_scroll("M  Back", 0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(sections):
            title, lines = sections[int(choice) - 1]
            app.text_page("news", title.upper(), lines)
        else:
            app.ansi_scroll("Enter a number from the list, or M.", 0.01)


if __name__ == "__main__":
    for title, lines in yearend_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
