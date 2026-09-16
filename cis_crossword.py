"""Daily crossword game for the CompuServe simulator (December 1988 setting).

A small rotation of pre-built 7x7 crossword puzzles, one per weekday, all
clued for 1988: movies, music, tech, sports, TV, news, and variety.

Layout (7x7, no blocks):
  * Across: rows 1, 4, 7 are 7-letter theme words  (clue numbers 1, 8, 16)
  * Down:   each column has a 3-letter word in rows 1-3 (numbers 1-7) and a
    3-letter word in rows 5-7 (numbers 9-15).  Each down word crosses
    exactly one across word.

Public API:
  puzzle_for_day(day=None) -> puzzle dict (deterministic per weekday)
  grid_rows(puzzle) -> list of 7 solution strings
  slots(puzzle) -> list of (direction, number, answer, clue, cells)
  check_answer(puzzle, number, direction, guess) -> bool
  new_state(puzzle) -> fresh play state dict
  fill_slot(state, puzzle, number, direction, guess) -> bool
  is_solved(state, puzzle) -> bool
  render_grid(puzzle, state) -> str
  render_clues(puzzle, state=None) -> str
  play(app) -> interactive terminal loop (wired in by the coordinator)
"""

from datetime import date

TITLE = "DAILY CROSSWORD"

# ---------------------------------------------------------------------------
# Puzzle data: one per weekday (Monday index 0 .. Sunday index 6).
# across: {1: (answer, clue), 8: (answer, clue), 16: (answer, clue)}
# down:   {1..7: (answer, clue)}   (rows 1-3, keyed by row-1 letter)
#         {9..15: (answer, clue)}  (rows 5-7, keyed by row-7 letter)
# ---------------------------------------------------------------------------

PUZZLES = [
    {
        "weekday": "Monday",
        "theme": "At the movies: 1988",
        "across": {
            1: ("RAINMAN", "'88 Best Picture starring Dustin Hoffman"),
            8: ("DIEHARD", "Bruce Willis '88 action hit"),
            16: ("WORKING", "'___ Girl' (1988 Melanie Griffith film)"),
        },
        "down": {
            1: ("ROM", "PC's built-in memory"),
            2: ("AMP", "Rock stack component"),
            3: ("IRS", "Tax agency"),
            4: ("NET", "Tennis court divider"),
            5: ("MUD", "Off-road goo"),
            6: ("AXE", "Lumberjack's tool"),
            7: ("NUT", "Bolt's partner"),
            9: ("JAW", "Yap trap"),
            10: ("TWO", "Pair"),
            11: ("CAR", "Garage occupant"),
            12: ("ARK", "Noah's vessel"),
            13: ("FBI", "G-men's org."),
            14: ("SUN", "Daytime star"),
            15: ("MEG", "Byte prefix"),
        },
    },
    {
        "weekday": "Tuesday",
        "theme": "1988 in music",
        "across": {
            1: ("MADONNA", "'Like a Virgin' singer"),
            8: ("CHAPMAN", "Tracy ___, 'Fast Car' singer"),
            16: ("WHITNEY", "'I Wanna Dance with Somebody' singer"),
        },
        "down": {
            1: ("MAC", "Apple's 1984 debut"),
            2: ("AXE", "Guitarist's guitar, slangily"),
            3: ("DOG", "Man's best friend"),
            4: ("OLD", "Not new"),
            5: ("NET", "Fisherman's gear"),
            6: ("NAG", "Pester"),
            7: ("AMP", "Concert speaker"),
            9: ("SAW", "Carpenter's tool"),
            10: ("ASH", "Cigarette remnant"),
            11: ("SKI", "Schuss"),
            12: ("HAT", "Cap"),
            13: ("SUN", "It rises in the east"),
            14: ("JOE", "Cup of ___"),
            15: ("SKY", "Blue yonder"),
        },
    },
    {
        "weekday": "Wednesday",
        "theme": "Home computing",
        "across": {
            1: ("PRINTER", "Dot-matrix output device"),
            8: ("MONITOR", "CRT display"),
            16: ("ANTENNA", "Rabbit ears"),
        },
        "down": {
            1: ("POP", "Top 40 sound"),
            2: ("ROM", "It holds the BIOS"),
            3: ("IRS", "1040 org."),
            4: ("NET", "Trawl"),
            5: ("TEE", "Golfer's prop"),
            6: ("EGG", "Omelet ingredient"),
            7: ("RAP", "Hip-hop's genre"),
            9: ("CIA", "Spy agency"),
            10: ("RUN", "Jog"),
            11: ("JET", "747, e.g."),
            12: ("TIE", "Windsor, e.g."),
            13: ("VAN", "Band's transport"),
            14: ("SUN", "Sol"),
            15: ("SEA", "Ocean"),
        },
    },
    {
        "weekday": "Thursday",
        "theme": "1988 in sports",
        "across": {
            1: ("DODGERS", "'88 World Series champs"),
            8: ("GRETZKY", "The Great One, traded to L.A. in '88"),
            16: ("CANSECO", "'88 AL MVP with 40/40"),
        },
        "down": {
            1: ("DOS", "PC's OS"),
            2: ("OAK", "Mighty tree"),
            3: ("DOG", "Hot ___"),
            4: ("GOP", "Elephant party"),
            5: ("EGG", "Scramble ingredient"),
            6: ("ROM", "Game cartridge's chip"),
            7: ("SKI", "Slalom need"),
            9: ("DNC", "Donkey party's committee"),
            10: ("USA", "Olympic team"),
            11: ("VAN", "Team bus"),
            12: ("IRS", "W-2 watcher"),
            13: ("TIE", "Deadlock"),
            14: ("MAC", "Big ___ (hamburger)"),
            15: ("ZOO", "Animal park"),
        },
    },
    {
        "weekday": "Friday",
        "theme": "1988 on TV",
        "across": {
            1: ("GROWING", "'___ Pains' (Alan Thicke sitcom)"),
            8: ("STROKES", "'Diff'rent ___'"),
            16: ("MARRIED", "'___ ... with Children'"),
        },
        "down": {
            1: ("GYM", "Workout spot"),
            2: ("RUN", "Sprint"),
            3: ("OAR", "Rowboat propeller"),
            4: ("WEB", "Spider's snare"),
            5: ("IBM", "Big Blue"),
            6: ("NET", "Volleyball divider"),
            7: ("GIG", "Band's booking"),
            9: ("ROM", "Nonvolatile memory"),
            10: ("CIA", "Langley org."),
            11: ("CAR", "Freeway cruiser"),
            12: ("VCR", "VHS deck"),
            13: ("SKI", "Bunny slope need"),
            14: ("TIE", "Necktie"),
            15: ("MUD", "Pigpen fill"),
        },
    },
    {
        "weekday": "Saturday",
        "theme": "1988 in the news",
        "across": {
            1: ("DUKAKIS", "'88 Democratic nominee"),
            8: ("CALGARY", "'88 Winter Olympics city"),
            16: ("DROUGHT", "'88 Midwest scourge"),
        },
        "down": {
            1: ("DOS", "Boot disk's OS"),
            2: ("USA", "Stars and Stripes, for short"),
            3: ("KID", "Young goat"),
            4: ("AMP", "It goes to eleven, in 'Spinal Tap'"),
            5: ("KIN", "Family"),
            6: ("IRS", "April 15 org."),
            7: ("SUN", "Center of the solar system"),
            9: ("MUD", "Muddy ground"),
            10: ("VCR", "Betamax's rival"),
            11: ("BOO", "Haunt's shout"),
            12: ("CPU", "Computer's brain"),
            13: ("DOG", "Snoopy, e.g."),
            14: ("ASH", "Volcano's fallout"),
            15: ("NET", "Goalie's mesh"),
        },
    },
    {
        "weekday": "Sunday",
        "theme": "Sunday variety",
        "across": {
            1: ("SHUTTLE", "Discovery or Atlantis"),
            8: ("MUPPETS", "Kermit's crew"),
            16: ("LIBERTY", "Statue of ___"),
        },
        "down": {
            1: ("SEA", "Briny expanse"),
            2: ("HAT", "Fedora, e.g."),
            3: ("USA", "Uncle Sam's land"),
            4: ("TEE", "Shirt type"),
            5: ("TIE", "Cravat"),
            6: ("LOG", "Fireplace fuel"),
            7: ("EGG", "Easter hunt item"),
            9: ("EEL", "Sushi bar order"),
            10: ("SKI", "Aspen activity"),
            11: ("WEB", "Charlotte's medium"),
            12: ("PIE", "Apple dessert"),
            13: ("VCR", "Video recorder"),
            14: ("BAT", "Louisville Slugger"),
            15: ("SKY", "Pilot's milieu"),
        },
    },
]

# Slot numbering fixed by the layout (see module docstring).
_ACROSS_NUMBERS = (1, 8, 16)
_DOWN_TOP_NUMBERS = tuple(range(1, 8))      # rows 1-3, one per column
_DOWN_BOTTOM_NUMBERS = tuple(range(9, 16))  # rows 5-7, one per column


def _build(puzzle):
    """Derive the solution grid and slot list from a puzzle's answers."""
    across = puzzle["across"]
    down = puzzle["down"]
    rows = [""] * 7
    rows[0] = across[1][0]
    rows[3] = across[8][0]
    rows[6] = across[16][0]
    rows[1] = "".join(down[n][0][1] for n in _DOWN_TOP_NUMBERS)
    rows[2] = "".join(down[n][0][2] for n in _DOWN_TOP_NUMBERS)
    rows[4] = "".join(down[n][0][0] for n in _DOWN_BOTTOM_NUMBERS)
    rows[5] = "".join(down[n][0][1] for n in _DOWN_BOTTOM_NUMBERS)
    slot_list = []
    for number in _ACROSS_NUMBERS:
        answer, clue = across[number]
        row = {1: 0, 8: 3, 16: 6}[number]
        slot_list.append(("A", number, answer, clue,
                          [(row, c) for c in range(7)]))
    for i, number in enumerate(_DOWN_TOP_NUMBERS):
        answer, clue = down[number]
        slot_list.append(("D", number, answer, clue,
                          [(r, i) for r in range(3)]))
    for i, number in enumerate(_DOWN_BOTTOM_NUMBERS):
        answer, clue = down[number]
        slot_list.append(("D", number, answer, clue,
                          [(r, i) for r in range(4, 7)]))
    puzzle = dict(puzzle)
    puzzle["grid"] = rows
    puzzle["slots"] = slot_list
    return puzzle


# Precompute grids/slots once (pure data, no imports needed).
PUZZLES = [_build(p) for p in PUZZLES]


# ---------------------------------------------------------------------------
# Pure logic
# ---------------------------------------------------------------------------

def puzzle_for_day(day=None):
    """Return the puzzle for a date, deterministically one per weekday.

    ``day`` defaults to the session-aware simulated day (lazy import to
    avoid a circular import with cis_dynamic).
    """
    if day is None:
        try:
            from cis_dynamic import simulation_day
            day = simulation_day()
        except Exception:
            day = date(1988, 12, 15)
    return PUZZLES[day.weekday() % len(PUZZLES)]


def grid_rows(puzzle):
    """The 7 solution rows of the puzzle grid."""
    return list(puzzle["grid"])


def slots(puzzle):
    """All slots as (direction, number, answer, clue, cells) tuples."""
    return list(puzzle["slots"])


def _find_slot(puzzle, number, direction):
    direction = direction.upper()
    for slot in puzzle["slots"]:
        if slot[0] == direction and slot[1] == number:
            return slot
    return None


def check_answer(puzzle, number, direction, guess):
    """True when ``guess`` matches the slot's answer (case-insensitive).

    Returns False for unknown slots, wrong lengths, and wrong answers.
    """
    slot = _find_slot(puzzle, number, direction)
    if slot is None:
        return False
    answer = slot[2]
    cleaned = "".join(ch for ch in str(guess).upper() if ch.isalpha())
    return cleaned == answer and len(cleaned) == len(answer)


def new_state(puzzle):
    """Fresh play state: nothing filled in yet."""
    return {
        "entries": {(s[0], s[1]): [None] * len(s[2]) for s in puzzle["slots"]},
        "moves": 0,
    }


def fill_slot(state, puzzle, number, direction, guess):
    """Record a correct guess in the state; return True when accepted."""
    if not check_answer(puzzle, number, direction, guess):
        return False
    slot = _find_slot(puzzle, number, direction)
    key = (slot[0], slot[1])
    state["entries"][key] = list(slot[2])
    return True


def is_solved(state, puzzle):
    """True when every slot is filled with its correct answer."""
    for direction, number, answer, _clue, _cells in puzzle["slots"]:
        if state["entries"].get((direction, number)) != list(answer):
            return False
    return True


def _cell_display(puzzle, state):
    """Map (row, col) -> (number or None, letter or None)."""
    numbers = {}
    letters = {}
    for direction, number, answer, _clue, cells in puzzle["slots"]:
        r, c = cells[0]
        numbers.setdefault((r, c), number)
        filled = state["entries"].get((direction, number)) or []
        for (rr, cc), ch in zip(cells, filled):
            if ch:
                letters[(rr, cc)] = ch
    return numbers, letters


def render_grid(puzzle, state):
    """Render the grid: clue numbers, filled letters, blanks as '.'."""
    numbers, letters = _cell_display(puzzle, state)
    bar = "   +" + "----+" * 7
    lines = [bar]
    for r in range(7):
        cells = []
        for c in range(7):
            num = numbers.get((r, c))
            ch = letters.get((r, c), ".")
            num_s = str(num) if num is not None else ""
            cells.append("%-2s%2s" % (num_s, ch))
        lines.append(" %d |%s|" % (r + 1, "|".join(cells)))
        lines.append(bar)
    return "\n".join(lines)


def render_clues(puzzle, state=None):
    """List across/down clues, marking solved slots when state given."""
    lines = ["ACROSS"]
    for direction, number, answer, clue, _cells in puzzle["slots"]:
        if direction != "A":
            continue
        done = state is not None and state["entries"].get((direction, number)) == list(answer)
        lines.append("  %2d. %s%s" % (number, clue, "  [solved]" if done else ""))
    lines.append("DOWN")
    for direction, number, answer, clue, _cells in puzzle["slots"]:
        if direction != "D":
            continue
        done = state is not None and state["entries"].get((direction, number)) == list(answer)
        lines.append("  %2d. %s%s" % (number, clue, "  [solved]" if done else ""))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive play
# ---------------------------------------------------------------------------

HELP_TEXT = """Commands:
  A<num> <answer>   guess an across entry, e.g.  A1 RAINMAN
  D<num> <answer>   guess a down entry, e.g.  D3 IRS
  GRID              redisplay the grid
  CLUES             redisplay the clue list
  HELP              show this help
  QUIT              leave the puzzle"""


def _parse_command(text):
    """Split raw input into (verb, number, direction, rest)."""
    text = text.strip()
    if not text:
        return ("", None, None, "")
    upper = text.upper()
    for verb in ("QUIT", "GRID", "CLUES", "HELP"):
        if upper == verb or upper.startswith(verb + " "):
            return (verb, None, None, "")
    head, _, rest = text.partition(" ")
    head = head.upper()
    if head[:1] in ("A", "D") and head[1:].isdigit():
        return ("GUESS", int(head[1:]), head[:1], rest.strip())
    return ("", None, None, text)


def play(app):
    """Interactive entry point: wired into the games menu by the coordinator."""
    puzzle = puzzle_for_day()
    state = new_state(puzzle)
    app.ansi_scroll(TITLE, 0.01)
    app.ansi_scroll("%s -- %s" % (puzzle["weekday"], puzzle["theme"]), 0.01)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll("Fill the grid. Each down word crosses one across word.", 0.01)
    app.ansi_scroll("Type HELP for commands.", 0.01)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(render_grid(puzzle, state), 0.01)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(render_clues(puzzle, state), 0.01)
    while True:
        if is_solved(state, puzzle):
            app.ansi_scroll("", 0.01)
            app.ansi_scroll("CONGRATULATIONS! Puzzle solved in %d move%s." % (
                state["moves"], "" if state["moves"] == 1 else "s"), 0.01)
            app.ansi_scroll("Come back tomorrow for a new grid.", 0.01)
            return
        try:
            raw = input("crossword> ")
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            raw = "QUIT"
        verb, number, direction, rest = _parse_command(raw)
        if verb == "QUIT":
            app.ansi_scroll("Puzzle abandoned. The grid will keep.", 0.01)
            return
        if verb == "GRID":
            app.ansi_scroll(render_grid(puzzle, state), 0.01)
            continue
        if verb == "CLUES":
            app.ansi_scroll(render_clues(puzzle, state), 0.01)
            continue
        if verb == "HELP":
            app.ansi_scroll(HELP_TEXT, 0.01)
            continue
        if verb == "GUESS":
            slot = _find_slot(puzzle, number, direction)
            if slot is None:
                app.ansi_scroll("No such entry. Try HELP for the command list.", 0.01)
                continue
            _d, _n, answer, _clue, _cells = slot
            key = (direction, number)
            if state["entries"].get(key) == list(answer):
                app.ansi_scroll("Already solved.", 0.01)
                continue
            if not rest:
                app.ansi_scroll("Give an answer, e.g. %s%d <answer>." % (direction, number), 0.01)
                continue
            state["moves"] += 1
            if fill_slot(state, puzzle, number, direction, rest):
                app.ansi_scroll("Correct!", 0.01)
                app.ansi_scroll(render_grid(puzzle, state), 0.01)
            else:
                cleaned = "".join(ch for ch in rest.upper() if ch.isalpha())
                if len(cleaned) != len(answer):
                    app.ansi_scroll("That entry needs %d letters." % len(answer), 0.01)
                else:
                    app.ansi_scroll("Not quite -- try again.", 0.01)
            continue
        app.ansi_scroll("Hmm? Type HELP for commands.", 0.01)
