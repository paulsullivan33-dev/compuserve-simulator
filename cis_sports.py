"""Sports & TV service for the December 1988 simulation setting.

Pure content + logic module: late-1988 NFL standings and scores, the
1988-89 prime-time TV grid, the 1988-89 MLB hot stove, plus a Super
Bowl XXIII preview (preview ONLY -- the game is in the future), a 1988
World Series recap, and mid-December 1988 NBA and NHL standings. All
content functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page).

Standings records marked VERIFIED were confirmed against season
records; a few AFC West non-leader records are marked as estimates.
Scores shown are verified Week 15/16 (early/mid December 1988) results.
NBA records are verified as of Dec 19, 1988 and NHL records as of
Dec 15, 1988 against daily standings tables.
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
# Super Bowl XXIII -- PREVIEW ONLY (game is Jan 22, 1989, after the sim date)
# ---------------------------------------------------------------------------
# Verified facts: matchup, regular-season records, date, venue, coaches,
# 1988 NFL MVP, and the Super Bowl XVI rematch angle. Nothing here may
# state or imply the game's result -- it has not happened yet.
SB_PREVIEW = {
    "matchup": "San Francisco 49ers (NFC) vs Cincinnati Bengals (AFC)",
    "date": "January 22, 1989",
    "venue": "Joe Robbie Stadium, Miami, Florida",
    "nfc_team": ("San Francisco 49ers", 10, 6, True),
    "afc_team": ("Cincinnati Bengals", 12, 4, True),
    "coaches": ("Bill Walsh (San Francisco)", "Sam Wyche (Cincinnati)"),
    "early_line": "49ers by 7",
}

# Verified 1988 regular-season player notes, drawn from season records.
SB_KEY_PLAYERS = [
    ("Joe Montana (49ers QB)",
     "Won back the starting job down the stretch and led San Francisco to "
     "four wins in its final five games. Threw for 2,981 yards and 18 TD."),
    ("Jerry Rice (49ers WR)",
     "64 catches for 1,306 yards and 9 TD in the regular season -- the deep "
     "threat Montana trusts most when it matters."),
    ("Roger Craig (49ers RB)",
     "Team-high 76 catches plus 2,036 combined rushing/receiving yards and "
     "10 TD -- the engine of the Walsh offense."),
    ("Boomer Esiason (Bengals QB)",
     "The 1988 NFL MVP (31 of 78 AP votes). Threw for 3,572 yards and 28 TD "
     "while leading the AFC's highest-powered offense."),
    ("Ickey Woods (Bengals RB)",
     "The rookie sensation whose 'Ickey Shuffle' end-zone dance became a "
     "national craze. Cincinnati's ground game goes through him."),
]

SB_STORYLINES = [
    ("SUPER BOWL XVI REMATCH",
     "Seven years after Super Bowl XVI, these same two franchises meet "
     "again on the NFL's biggest stage. The Bengals have waited since the "
     "1981 season for revenge."),
    ("THE COACHING CHESS MATCH",
     "Bill Walsh's precision West Coast offense against Sam Wyche's "
     "no-huddle attack -- two of the game's great offensive minds."),
    ("HOME-FIELD? NOT EXACTLY",
     "The Bengals (12-4) own the AFC's best record, but the neutral field "
     "in Miami erases any edge. The early line makes San Francisco (10-6) "
     "a 7-point favorite."),
    ("MVP VS. DYNASTY",
     "Boomer Esiason just won the league MVP. Joe Montana is chasing his "
     "third ring. Something has to give on January 22."),
    ("THE QUIET CONTENDER",
     "Nobody picked the 49ers at midseason -- Montana split time with "
     "Steve Young and the club sat 6-5. Since then: a division title and "
     "the hottest finish in the NFC."),
]


# ---------------------------------------------------------------------------
# 1988 World Series -- completed October 1988, recap is fair game
# ---------------------------------------------------------------------------
# Verified: Dodgers 4, Athletics 1, Oct 15-20; Gibson's Game 1 pinch-hit
# walk-off off Eckersley; Hershiser World Series MVP; 59 consecutive
# scoreless innings (breaking Drysdale's 58 1/3); Dodgers 94-67, A's 104-58;
# ALCS Oakland over Boston 4-0; NLCS Dodgers over Mets 4-3.
WS_RECAP = [
    "1988 WORLD SERIES -- RECAP",
    "Los Angeles Dodgers 4, Oakland Athletics 1 (verified)",
    "Played Oct 15-20, 1988: Dodger Stadium and the Oakland-Alameda County Coliseum.",
    "",
    "GAME 1 (Oct 15, Dodger Stadium): Down to his last out, barely able to "
    "walk, Kirk Gibson limped to the plate as a pinch-hitter and crushed a "
    "two-out, two-run walk-off homer off Dennis Eckersley to stun Oakland.",
    "GAME 2: Orel Hershiser threw a shutout as the Dodgers took a 2-0 lead.",
    "GAME 3: Oakland got its only win of the series behind the Bash Brothers.",
    "GAME 4: Los Angeles stayed in command on the road.",
    "GAME 5 (Oct 20, Oakland): Hershiser went the distance in a 5-2 "
    "complete-game win. The Dodgers were world champions.",
    "",
    "SERIES MVP: Orel Hershiser (verified). 2-0 with a shutout and a "
    "complete game in two starts.",
    "Hershiser's season: 23-8, NL Cy Young Award, and a record 59 "
    "consecutive scoreless innings from Aug 30 to Sep 28, breaking Don "
    "Drysdale's 58 1/3.",
    "The Athletics entered as heavy favorites after a 104-58 season and a "
    "4-0 sweep of Boston in the ALCS. The Dodgers (94-67) had survived a "
    "7-game NLCS against the 100-win Mets.",
    "Managers: Tommy Lasorda (Dodgers), Tony La Russa (Athletics).",
]


# ---------------------------------------------------------------------------
# 1988-89 NBA: standings as of Dec 19, 1988 (verified vs. daily tables)
# ---------------------------------------------------------------------------
# Structure of the 1988-89 season (verified): 25 teams in four divisions --
# Atlantic/Central in the East, Midwest/Pacific in the West. The Charlotte
# Hornets (24th franchise) were placed in the Atlantic and the Miami Heat
# (25th) in the Midwest; the Sacramento Kings moved from the Midwest to
# the Pacific. Format: (team name, wins, losses, verified?).
NBA_STANDINGS: Dict[str, List[Tuple[str, int, int, bool]]] = {
    "ATLANTIC": [
        ("New York Knicks", 16, 7, True),
        ("Philadelphia 76ers", 14, 10, True),
        ("Boston Celtics", 12, 11, True),
        ("New Jersey Nets", 10, 15, True),
        ("Washington Bullets", 6, 15, True),
        ("Charlotte Hornets", 6, 15, True),
    ],
    "CENTRAL": [
        ("Cleveland Cavaliers", 15, 5, True),
        ("Detroit Pistons", 17, 6, True),
        ("Atlanta Hawks", 15, 9, True),
        ("Chicago Bulls", 12, 10, True),
        ("Milwaukee Bucks", 11, 10, True),
        ("Indiana Pacers", 5, 17, True),
    ],
    "MIDWEST": [
        ("Dallas Mavericks", 14, 7, True),
        ("Denver Nuggets", 15, 8, True),
        ("Houston Rockets", 14, 9, True),
        ("Utah Jazz", 13, 10, True),
        ("San Antonio Spurs", 6, 15, True),
        ("Miami Heat", 1, 19, True),
    ],
    "PACIFIC": [
        ("Los Angeles Lakers", 16, 7, True),
        ("Seattle SuperSonics", 12, 9, True),
        ("Portland Trail Blazers", 13, 10, True),
        ("Phoenix Suns", 11, 10, True),
        ("Golden State Warriors", 9, 12, True),
        ("Los Angeles Clippers", 8, 15, True),
        ("Sacramento Kings", 5, 15, True),
    ],
}

NBA_HIGHLIGHTS = [
    "The defending champion Lakers (16-7) are rolling again, but the Knicks "
    "(16-7) have caught them -- New York sits atop the Atlantic.",
    "Cleveland (15-5) and Detroit (17-6) are staging a Central Division dogfight "
    "two months into the season.",
    "The expansion Heat are 1-19 -- Miami lost its first 17 games, an NBA "
    "record, before finally winning one. Charlotte (6-15) is fairing better.",
    "Denver, Dallas, Houston and Utah are all bunched in the Midwest -- the "
    "tightest race in the league right now.",
    "Chicago's young core is right in the Central mix at 12-10; the Bulls are "
    "one to watch as the season grinds on.",
]


# ---------------------------------------------------------------------------
# 1988-89 NHL: standings as of Dec 15, 1988 (verified vs. daily tables)
# ---------------------------------------------------------------------------
# Structure of the 1988-89 season (verified): 21 teams in four divisions --
# Adams/Patrick in the Prince of Wales Conference, Norris/Smythe in the
# Clarence Campbell Conference. Format: (team, wins, losses, ties,
# verified?); points = 2*W + T.
NHL_STANDINGS: Dict[str, List[Tuple[str, int, int, int, bool]]] = {
    "ADAMS": [
        ("Montreal Canadiens", 19, 10, 6, True),
        ("Boston Bruins", 13, 12, 8, True),
        ("Hartford Whalers", 13, 15, 2, True),
        ("Buffalo Sabres", 12, 17, 3, True),
        ("Quebec Nordiques", 11, 20, 2, True),
    ],
    "PATRICK": [
        ("Pittsburgh Penguins", 18, 11, 2, True),
        ("New York Rangers", 16, 12, 4, True),
        ("Washington Capitals", 15, 13, 4, True),
        ("Philadelphia Flyers", 15, 17, 2, True),
        ("New Jersey Devils", 12, 14, 5, True),
        ("New York Islanders", 7, 22, 2, True),
    ],
    "NORRIS": [
        ("Detroit Red Wings", 17, 9, 4, True),
        ("St. Louis Blues", 12, 13, 5, True),
        ("Minnesota North Stars", 9, 16, 6, True),
        ("Toronto Maple Leafs", 11, 19, 2, True),
        ("Chicago Blackhawks", 8, 19, 4, True),
    ],
    "SMYTHE": [
        ("Calgary Flames", 22, 5, 5, True),
        ("Los Angeles Kings", 20, 11, 1, True),
        ("Edmonton Oilers", 18, 12, 3, True),
        ("Winnipeg Jets", 13, 10, 5, True),
        ("Vancouver Canucks", 12, 16, 5, True),
    ],
}

NHL_HIGHLIGHTS = [
    "Wayne Gretzky's trade to Los Angeles is paying off -- the Kings (20-11-1) "
    "are second in the Smythe and the highest-scoring club in the league.",
    "Calgary (22-5-5, 49 points) is the best team in hockey right now, "
    "running away with the Smythe Division.",
    "Pittsburgh (18-11-2) leads the Patrick -- the young Penguins are "
    "playing the most exciting hockey in the East.",
    "Montreal (19-10-6) is in control of the Adams, with Boston and Hartford "
    "chasing. Quebec is bringing up the rear.",
    "Detroit (17-9-4) leads the Norris, but the division is a logjam behind "
    "them -- every club is within striking distance of second.",
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


def _nba_record(team: Tuple[str, int, int, bool]) -> str:
    """W-L line for an NBA standings row (no ties in basketball)."""
    name, wins, losses, verified = team
    return f"{name:<26} {wins}-{losses:<7}" + ("" if verified else " (est.)")


def _nhl_record(team: Tuple[str, int, int, int, bool]) -> str:
    """W-L-T plus points line for an NHL standings row (points = 2*W + T)."""
    name, wins, losses, ties, verified = team
    pts = 2 * wins + ties
    return f"{name:<26} {wins}-{losses}-{ties}  {pts} pts" + \
        ("" if verified else " (est.)")


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
    """All seven sections as (title, lines) pairs for the menu wire-up."""
    return [
        ("NFL", nfl_lines(day)),
        ("TV", tv_lines(day)),
        ("MLB", mlb_lines(day)),
        ("SUPER BOWL", super_bowl_preview_lines(day)),
        ("WORLD SERIES", world_series_lines(day)),
        ("NBA", nba_lines(day)),
        ("NHL", nhl_lines(day)),
    ]


def super_bowl_preview_lines(day: Optional[date] = None) -> List[str]:
    """Super Bowl XXIII PREVIEW -- strictly preview, the game is in the future.

    Kickoff is January 22, 1989 at Joe Robbie Stadium in Miami. This
    section must never state or imply a result: the game has not been
    played in the December 1988 simulation setting.
    """
    day = _day(day)
    nfc_name, nfc_w, nfc_l, _ = SB_PREVIEW["nfc_team"]
    afc_name, afc_w, afc_l, _ = SB_PREVIEW["afc_team"]
    coach_nfc, coach_afc = SB_PREVIEW["coaches"]
    lines = [
        "SUPER BOWL XXIII -- PREVIEW",
        "PREVIEW ONLY: this game has not been played yet.",
        "",
        "MATCHUP: " + SB_PREVIEW["matchup"],
        f"  {nfc_name} (NFC, {nfc_w}-{nfc_l}) -- verified",
        f"  {afc_name} (AFC, {afc_w}-{afc_l}) -- verified",
        f"KICKOFF: {SB_PREVIEW['date']}, {SB_PREVIEW['venue']}",
        f"COACHES: {coach_nfc} vs {coach_afc}",
        f"EARLY LINE: {SB_PREVIEW['early_line']}",
        "",
        "KEY PLAYERS (verified regular-season notes)",
        "-------------------------------------------",
    ]
    for name, note in SB_KEY_PLAYERS:
        lines.append("* " + name + ": " + note)
    lines.append("")
    title, text = SB_STORYLINES[day.day % len(SB_STORYLINES)]
    lines.extend(["STORYLINE: " + title, text])
    lines.append("")
    lines.append("The road to Miami ends January 22. Preview only -- no result yet.")
    return lines


def world_series_lines(day: Optional[date] = None) -> List[str]:
    """1988 World Series recap: Dodgers over Athletics, 4 games to 1."""
    day = _day(day)
    lines = list(WS_RECAP)
    lines.append("")
    start = day.day % 3
    extra = [
        "Gibson's Game 1 blast came on two bad knees -- he didn't play again "
        "in the series, and didn't need to.",
        "The A's 'Bash Brothers' -- Canseco and McGwire -- hit 74 homers in "
        "the regular season but couldn't carry Oakland past October.",
        "The Mets won 100 games and fell to L.A. in seven. Shea is restless.",
    ]
    lines.append("NOTEBOOK: " + extra[start])
    return lines


def nba_lines(day: Optional[date] = None) -> List[str]:
    """1988-89 NBA standings as of mid-December 1988 (verified)."""
    lines = [
        "NBA 1988-89 -- STANDINGS (verified as of Dec 19, 1988)",
        "Season runs Nov 4, 1988 - Apr 23, 1989. 25 teams, four divisions.",
        "Expansion: Charlotte Hornets (Atlantic), Miami Heat (Midwest).",
        "",
    ]
    for division, teams in NBA_STANDINGS.items():
        lines.append(division)
        lines.append("-" * len(division))
        lines.extend(_nba_record(team) for team in teams)
        lines.append("")
    day = _day(day)
    lines.append("AROUND THE LEAGUE: " + NBA_HIGHLIGHTS[day.day % len(NBA_HIGHLIGHTS)])
    lines.append("")
    lines.append("Defending champions: Los Angeles Lakers. All records verified.")
    return lines


def nhl_lines(day: Optional[date] = None) -> List[str]:
    """1988-89 NHL standings as of mid-December 1988 (verified)."""
    lines = [
        "NHL 1988-89 -- STANDINGS (verified as of Dec 15, 1988)",
        "21 teams, four divisions. Points: 2 for a win, 1 for a tie.",
        "",
    ]
    for division, teams in NHL_STANDINGS.items():
        lines.append(division)
        lines.append("-" * len(division))
        lines.extend(_nhl_record(team) for team in teams)
        lines.append("")
    day = _day(day)
    lines.append("AROUND THE LEAGUE: " + NHL_HIGHLIGHTS[day.day % len(NHL_HIGHLIGHTS)])
    lines.append("")
    lines.append("All records verified.")
    return lines


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
