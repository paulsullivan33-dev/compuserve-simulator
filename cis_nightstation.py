"""NIGHT SHIFT: EARTH STATION -- a 1988 satellite-uplink text adventure.

You are the overnight operator at a remote CompuServe-affiliated C-band
earth station. A thunderstorm has knocked out the satellite uplink, and the
6 AM news-wire feed must be on the air before the slot passes. Restore
power, realign the dish, load the feed cartridge, and transmit.

Distinct from the classic in-game ADVENTURE (computer-room premise): this
is a second, standalone adventure with its own map, parser, and puzzles.

Engine design: NightStationGame holds all state; .command(text) returns an
output string, so tests and scripts can drive it non-interactively.
play(app) wraps it in the interactive read_input loop.
"""
from cis_session import read_input as input

TITLE = "NIGHT SHIFT: EARTH STATION"
RECORDS_KEY = "nightstation_records"
HISCORE_KEY = "nightstation_hiscores"
MAX_MOVES = 81          # 5-minute ticks from 23:15 to the 06:00 feed slot
START_MINUTE = 23 * 60 + 15

DIRECTIONS = {
    "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
    "NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST",
    "U": "UP", "D": "DOWN",
    "NORTH": "NORTH", "SOUTH": "SOUTH", "EAST": "EAST", "WEST": "WEST",
    "NORTHEAST": "NORTHEAST", "NORTHWEST": "NORTHWEST",
    "SOUTHEAST": "SOUTHEAST", "SOUTHWEST": "SOUTHWEST",
    "UP": "UP", "DOWN": "DOWN",
}

ROOMS = {
    "parking": {
        "name": "GRAVEL PARKING LOT",
        "desc": ("A gravel lot beside the station, lit by one buzzing sodium lamp. "
                 "Your Chevy pickup is the only vehicle here. The generator shack "
                 "hums darkly to the north; the station lobby glows dimly east."),
        "exits": {"EAST": "lobby", "NORTH": "generator"},
    },
    "lobby": {
        "name": "STATION LOBBY",
        "desc": ("A small reception lobby with wood-paneled walls and a framed "
                 "photo of the big dish on dedication day, 1983. The reception "
                 "desk holds a sign-in log and a telephone directory."),
        "exits": {"WEST": "parking", "NORTH": "operations", "EAST": "cafeteria", "SOUTH": "garage"},
    },
    "garage": {
        "name": "GARAGE",
        "desc": ("A two-bay garage smelling of motor oil. A riding mower and stacked "
                 "tires line the walls. A red gas can sits by the workbench, "
                 "stenciled PROPERTY OF EARTH STATION 7."),
        "exits": {"NORTH": "lobby"},
    },
    "cafeteria": {
        "name": "BREAK ROOM",
        "desc": ("A break room with a humming vending machine, a Formica table, "
                 "and a wall pegboard hung with spare keys and tools. A Mr. Coffee "
                 "drips beside a stack of TV Guide issues."),
        "exits": {"WEST": "lobby", "NORTH": "bunkroom"},
    },
    "bunkroom": {
        "name": "NIGHT BUNKROOM",
        "desc": ("A narrow bunkroom where the night crew catches naps between "
                 "feed windows. An Army-surplus cot is shoved against the wall, "
                 "its blanket trailing on the floor. Something metallic glints "
                 "beneath the cot."),
        "exits": {"SOUTH": "cafeteria"},
    },
    "operations": {
        "name": "OPERATIONS DESK",
        "desc": ("The operations desk faces a wall of dark monitors. A dot-matrix "
                 "printer sits silent, and a black desk telephone waits by the "
                 "shift log binder. A steel door leads west, stenciled MAINTENANCE."),
        "exits": {"SOUTH": "lobby", "EAST": "control", "WEST": "maintenance"},
    },
    "maintenance": {
        "name": "MAINTENANCE SHOP",
        "desc": ("A cluttered shop of spare waveguide parts, coiled coax, and a "
                 "greasy workbench. A heavy alignment crank for the dish azimuth "
                 "motors hangs on the far wall."),
        "exits": {"EAST": "operations"},
    },
    "control": {
        "name": "UPLINK CONTROL ROOM",
        "desc": ("The uplink control room: racks of glowing equipment, a master "
                 "console with a dark CRT, and a wall clock stopped at the moment "
                 "the storm hit. A locked door east is marked STATION MANAGER. "
                 "A roof hatch leads up."),
        "exits": {"WEST": "operations", "SOUTH": "transmitter", "EAST": "office", "UP": "roof"},
    },
    "office": {
        "name": "STATION MANAGER OFFICE",
        "desc": ("A cramped office with a metal desk, a filing cabinet, and a "
                 "wall calendar from the Columbus Dispatch. On the desk, in a "
                 "padded mailer, sits a labeled feed cartridge for tonight's "
                 "news-wire uplink."),
        "exits": {"WEST": "control"},
    },
    "roof": {
        "name": "CONTROL ROOM ROOF",
        "desc": ("A flat tar-paper roof. From here you can see the big C-band dish "
                 "looming against the clearing sky, its face tipped wrong after "
                 "the storm's gust front."),
        "exits": {"DOWN": "control"},
    },
    "transmitter": {
        "name": "TRANSMITTER HALL",
        "desc": ("A long hall of transmitter cabinets, their pilot lamps dark. "
                 "One cabinet's service panel is screwed shut; its stencil reads "
                 "UPLINK EXCITER -- 5 AMP FUSE. A carrier lamp above it is dark."),
        "exits": {"NORTH": "control", "EAST": "dishpad"},
    },
    "dishpad": {
        "name": "DISH ANTENNA PAD",
        "desc": ("A concrete pad at the foot of the 7-meter dish. Guy wires sing "
                 "in the night wind. A caged ladder climbs the pedestal to the "
                 "azimuth platform above."),
        "exits": {"WEST": "transmitter", "NORTH": "tower"},
    },
    "tower": {
        "name": "DISH AZIMUTH PLATFORM",
        "desc": ("A steel platform halfway up the dish pedestal, swaying faintly. "
                 "The azimuth drive housing is open, its crank socket waiting. "
                 "Beyond the railing, the county lights glitter."),
        "exits": {"SOUTH": "dishpad", "NORTH": "relay"},
    },
    "relay": {
        "name": "MICROWAVE RELAY HUT",
        "desc": ("A cinderblock relay hut at the edge of the field. A rack-mounted "
                 "receiver hisses static through a small speaker; its signal "
                 "meter needle lies flat against the left peg."),
        "exits": {"SOUTH": "tower"},
    },
    "generator": {
        "name": "GENERATOR SHACK",
        "desc": ("A corrugated shack housing the station's diesel generator. The "
                 "fuel gauge reads near empty and the starter panel is dark. It "
                 "smells of diesel and rain."),
        "exits": {"SOUTH": "storage", "NORTH": "parking"},
    },
    "storage": {
        "name": "PARTS STORAGE",
        "desc": ("A windowless parts room stacked with crates of vacuum tubes, "
                 "spare fuses, and modulator boards. The storm killed the lights; "
                 "it is pitch dark in here."),
        "dark": True,
        "exits": {"NORTH": "generator", "EAST": "loading"},
    },
    "loading": {
        "name": "LOADING DOCK",
        "desc": ("A concrete loading dock with a roll-up door. Pallets of paper "
                 "for the teletype machines wait under a tarp, and a clipboard "
                 "hangs by the door with tonight's delivery manifest."),
        "exits": {"WEST": "storage"},
    },
}

ROOM_ITEMS = {
    "lobby": ["FLASHLIGHT"],
    "garage": ["GAS CAN"],
    "cafeteria": ["SCREWDRIVER", "STEEL KEY"],
    "bunkroom": ["BRASS KEY"],
    "operations": ["SHIFT LOG"],
    "maintenance": ["ALIGN CRANK"],
    "office": ["FEED CARTRIDGE"],
    "storage": ["FUSE"],
}

LOCKED_EXITS = {
    ("operations", "WEST"): {"key": "BRASS KEY", "label": "the maintenance shop door"},
    ("control", "EAST"): {"key": "STEEL KEY", "label": "the manager's office door"},
}

ITEM_DESCRIPTIONS = {
    "FLASHLIGHT": "A heavy steel flashlight. The beam is strong; fresh D-cells.",
    "GAS CAN": "A red five-gallon can, full of diesel. Stenciled PROPERTY OF EARTH STATION 7.",
    "SCREWDRIVER": "A flat-head screwdriver with a taped handle. Good for service panels.",
    "STEEL KEY": "A steel key tagged MANAGER in Dymo tape.",
    "BRASS KEY": "A brass key that was hidden under the bunkroom cot.",
    "SHIFT LOG": ("The shift log. Last entry, in the day operator's hand: STORM FRONT "
                  "MOVING IN. IF THE UPLINK DIES: FUEL THE GENERATOR, RE-SEAT THE "
                  "EXCITER FUSE, CRANK THE DISH BACK TO 97W, LOAD TONIGHT'S FEED "
                  "CARTRIDGE, AND KEY THE TRANSMITTER BEFORE 0600."),
    "ALIGN CRANK": "A heavy crank that mates with the dish azimuth drive socket.",
    "FEED CARTRIDGE": ("A padded mailer holding tonight's news-wire feed cartridge, "
                       "labeled UPI OVERNIGHT PACKAGE -- AIRS 0600."),
    "FUSE": "A 5-amp ceramic fuse, the exact type the exciter panel calls for.",
}


class NightStationGame:
    """Scriptable engine for NIGHT SHIFT: EARTH STATION.

    .command(text) -> output string. .over is True when the game has ended
    (won, lost on the clock, or quit). Persistence of records is attempted
    through app.cis_dynamic when an app is supplied; without an app the
    game runs fully in memory.
    """

    def __init__(self, app=None, user_id=None):
        self.app = app
        self.user_id = user_id or (getattr(app, "current_user_id", None) if app is not None else None) or "GUEST"
        self.room = "lobby"
        self.inventory = []
        self.room_items = {room: list(items) for room, items in ROOM_ITEMS.items()}
        self.visited = set()
        self.unlocked = set()
        self.moves = 0
        self.score = 0
        self.powered = False
        self.fueled = False
        self.panel_open = False
        self.fuse_installed = False
        self.dish_aligned = False
        self.cartridge_loaded = False
        self.won = False
        self.lost = False
        self.quit = False
        self.recorded = False
        self.transmit_attempts = 0
        self._record_line = ""

    # -- state helpers -------------------------------------------------
    @property
    def over(self):
        return self.won or self.lost or self.quit

    def clock(self):
        """Current simulated clock as HH:MM string."""
        total = START_MINUTE + self.moves * 5
        return f"{(total // 60) % 24:02d}:{(total % 60):02d}"

    def minutes_left(self):
        return (MAX_MOVES - self.moves) * 5

    def _see(self):
        """True if the current room is visible (dark rooms need flashlight)."""
        return not ROOMS[self.room].get("dark") or "FLASHLIGHT" in self.inventory

    # -- persistence ----------------------------------------------------
    def _score_store(self):
        app = self.app
        dyn = getattr(app, "cis_dynamic", None) if app is not None else None
        if dyn is None:
            return None, None
        try:
            return dyn.load_state(app), dyn
        except Exception:
            return None, None

    def record_result(self):
        """Persist per-user record and station-wide top scores. Idempotent."""
        if self.recorded:
            return self._record_line
        self.recorded = True
        state, dyn = self._score_store()
        if state is None:
            self._record_line = f"STATION LOG: {self.user_id} scored {self.score} (offline -- no archive)."
            return self._record_line
        records = state.setdefault(RECORDS_KEY, {})
        mine = records.setdefault(self.user_id, {"plays": 0, "wins": 0, "best_score": 0, "best_moves": 0})
        mine["plays"] += 1
        if self.won:
            mine["wins"] += 1
            if self.score > mine["best_score"]:
                mine["best_score"] = self.score
                mine["best_moves"] = self.moves
        board = state.setdefault(HISCORE_KEY, [])
        board.append({"user": self.user_id, "score": self.score, "moves": self.moves, "won": self.won})
        board.sort(key=lambda entry: (-entry["score"], entry["moves"]))
        del board[5:]
        state[HISCORE_KEY] = board
        try:
            dyn.save_state(self.app, state)
        except Exception:
            pass
        self._record_line = (f"STATION LOG: {self.user_id} -- {mine['wins']} wins in {mine['plays']} shifts, "
                             f"best {mine['best_score']} pts.")
        return self._record_line

    def records_table(self):
        """High-score table lines, shown at game end."""
        lines = ["", "--- STATION LOG: TOP NIGHT OPERATORS ---"]
        state, _ = self._score_store()
        board = (state or {}).get(HISCORE_KEY, [])
        if not board:
            lines.append("No completed shifts on record yet. Be the first.")
        else:
            for rank, entry in enumerate(board, 1):
                flag = " *" if entry["won"] else ""
                lines.append(f"{rank}. {entry['user']:<16} {entry['score']:>3} PTS  {entry['moves']:>2} MOVES{flag}")
            lines.append("* = feed transmitted on time")
        return lines

    # -- output builders ------------------------------------------------
    def describe(self):
        room = ROOMS[self.room]
        lines = [f"-- {room['name']} --"]
        if not self._see():
            lines.append("It is pitch dark. You cannot see a thing. (You need a light.)")
            return "\n".join(lines)
        lines.append(self._dynamic_desc())
        for item in self.room_items.get(self.room, []):
            lines.append(f"You can see a {item.lower()} here.")
        extra = self._room_extra()
        if extra:
            lines.append(extra)
        return "\n".join(lines)

    def _dynamic_desc(self):
        room_id = self.room
        base = ROOMS[room_id]["desc"]
        if room_id == "control":
            if not self.powered:
                return base + " The console is dead; the CRT shows only your reflection."
            status = []
            status.append("exciter fused" if self.fuse_installed else "exciter fuse MISSING")
            status.append("dish on 97W" if self.dish_aligned else "dish OFF-AZIMUTH")
            status.append("cartridge loaded" if self.cartridge_loaded else "feed cartridge MISSING")
            return base + " The console glows: " + ", ".join(s.upper() for s in status) + "."
        if room_id == "transmitter":
            if self.fuse_installed and self.powered:
                return ("A long hall of transmitter cabinets. The exciter cabinet hums "
                        "softly and its carrier lamp glows a steady green.")
            if self.panel_open:
                return ("A long hall of transmitter cabinets, their pilot lamps dark. "
                        "The exciter service panel hangs open, its fuse socket empty.")
            return base
        if room_id == "generator":
            if self.powered:
                return ("A corrugated shack housing the station's diesel generator. "
                        "The diesel thunders away; the starter panel glows green.")
            if self.fueled:
                return base + " The tank is full, but the generator is silent."
            return base
        if room_id == "roof" and self.dish_aligned:
            return ("A flat tar-paper roof. The big C-band dish faces the Clarke belt "
                    "dead-on, its feedhorn steady against the clearing sky.")
        return base

    def _room_extra(self):
        if self.room == "transmitter" and not self.powered and not self.panel_open:
            return "The exciter cabinet's service panel is screwed shut."
        if self.room == "relay":
            if self.dish_aligned and self.powered:
                return ("The receiver's signal meter now holds steady at mid-scale; "
                        "a faint news-wire teletype chatter leaks from the speaker.")
            return "The receiver hisses static. No usable signal."
        return ""

    # -- main entry ------------------------------------------------------
    def command(self, text):
        """Process one command line; return the output string."""
        if self.over:
            return "The shift is over. (Start a new game to play again.)"
        raw = (text or "").strip()
        if not raw:
            return "Speak up, operator."
        cmd = " ".join(raw.upper().split())

        if cmd in ("QUIT", "Q", "M"):
            self.quit = True
            self.record_result()
            return "You hang up your headset and sign the log: SHIFT INCOMPLETE.\n" + self._record_line

        handler = self._dispatch(cmd)
        if handler is None:
            return "I don't understand."
        self.moves += 1
        if self.moves >= MAX_MOVES and not self.won:
            self.lost = True
            self.record_result()
            return (handler + "\n\nThe wall clock creeps past 0600. Somewhere down the "
                    "wire, a network director cues dead air where your feed should be.\n"
                    "THE 6 AM FEED WINDOW HAS PASSED. SHIFT FAILED.\n" + self._record_line)
        if self.won and not self.recorded:
            self.record_result()
            return handler + "\n" + self._record_line + "\n" + "\n".join(self.records_table())
        if self.lost and not self.recorded:
            self.record_result()
            return handler + "\n" + self._record_line
        return handler

    # -- parser -----------------------------------------------------------
    def _dispatch(self, cmd):
        if cmd in DIRECTIONS or (cmd.startswith("GO ") and cmd[3:].strip() in DIRECTIONS):
            direction = DIRECTIONS[cmd[3:].strip()] if cmd.startswith("GO ") else DIRECTIONS[cmd]
            return self._go(direction)
        if cmd in ("LOOK", "L"):
            return self.describe()
        if cmd in ("INVENTORY", "I"):
            carried = ", ".join(self.inventory).lower() if self.inventory else "nothing"
            return f"You are carrying: {carried}."
        if cmd == "SCORE":
            return (f"SCORE: {self.score} points in {self.moves} moves. "
                    f"The 6 AM feed is at {self.clock()} -- {self.minutes_left()} minutes left.")
        if cmd == "TIME":
            return f"Station clock: {self.clock()}. The feed slot is 06:00."
        if cmd in ("HELP", "H", "?"):
            return self._help()
        if cmd == "MAP":
            return self._map()
        if cmd.startswith("TAKE ") or cmd.startswith("GET "):
            return self._take(cmd.split(" ", 1)[1])
        if cmd.startswith("PICK UP "):
            return self._take(cmd.split(" ", 2)[2])
        if cmd.startswith("DROP "):
            return self._drop(cmd.split(" ", 1)[1])
        if cmd.startswith(("EXAMINE ", "X ", "READ ", "LOOK AT ")):
            noun = cmd.split(" ", 1)[1]
            if noun.startswith("AT "):
                noun = noun[3:]
            return self._examine(noun)
        if cmd.startswith("USE "):
            return self._use(cmd[4:].strip())
        if cmd in ("OPEN DOOR", "UNLOCK DOOR", "OPEN", "UNLOCK"):
            return self._unlock()
        if cmd in ("TRANSMIT", "KEY TRANSMITTER", "START TRANSMISSION"):
            return self._transmit()
        if cmd.startswith("START "):
            return self._start(cmd[6:].strip())
        if cmd.startswith("FILL "):
            return self._fill(cmd[5:].strip())
        if cmd.startswith("INSTALL "):
            return self._install(cmd[8:].strip())
        if cmd.startswith("LOAD "):
            return self._load(cmd[5:].strip())
        if cmd.startswith("DIAL ") or cmd.startswith("CALL ") or cmd == "USE PHONE":
            return self._phone()
        if cmd == "LISTEN":
            return self._listen()
        if cmd.startswith("CLIMB "):
            return self._climb(cmd[6:].strip())
        return None

    def _help(self):
        return ("Commands: N/S/E/W/NE/NW/SE/SW/UP/DOWN (or GO <dir>), LOOK, TAKE <item>, "
                "DROP <item>, INVENTORY, EXAMINE <thing>, USE <thing>, OPEN DOOR, "
                "START <thing>, FILL <thing>, INSTALL <thing>, LOAD <thing>, "
                "TRANSMIT, DIAL, LISTEN, MAP, SCORE, TIME, HELP, QUIT.")

    def _map(self):
        return ("PARKING -E- LOBBY -N- OPERATIONS -E- CONTROL -S- TRANSMITTER -E- DISHPAD\n"
                "   |          | S        | W (locked)      | E (locked)   | N\n"
                "GENERATOR   GARAGE   MAINTENANCE        OFFICE         TOWER -N- RELAY HUT\n"
                "   | S                                                  | S\n"
                "STORAGE -E- LOADING DOCK        LOBBY -E- BREAK ROOM -N- BUNKROOM\n"
                "CONTROL -UP- ROOF (overlooks the dish)")

    # -- movement ----------------------------------------------------------
    def _go(self, direction):
        room = ROOMS[self.room]
        if direction not in room["exits"]:
            return "You can't go that way."
        lock = LOCKED_EXITS.get((self.room, direction))
        if lock and (self.room, direction) not in self.unlocked:
            return f"Locked: {lock['label']}. ({lock['key'].title()} required.)"
        if direction in ("UP", "DOWN") and self.room == "control" and direction == "UP":
            pass  # roof hatch is always open
        self.room = room["exits"][direction]
        if self.room not in self.visited:
            self.visited.add(self.room)
            self.score += 10
            return self.describe() + "\n(+10 discovery)"
        return self.describe()

    def _climb(self, noun):
        if "LADDER" in noun and self.room == "dishpad":
            return self._go("NORTH")
        if "DOWN" in noun and self.room == "tower":
            return self._go("SOUTH")
        return "There is nothing to climb here."

    # -- items --------------------------------------------------------------
    def _find_item(self, noun):
        noun = noun.replace("THE ", "").strip()
        for item in self.inventory:
            if noun == item or noun in item:
                return item, "carried"
        for item in self.room_items.get(self.room, []):
            if noun == item or noun in item:
                return item, "here"
        return None, None

    def _take(self, noun):
        if not self._see():
            return "You can't see a thing in here."
        item, where = self._find_item(noun)
        if item is None:
            return "You do not see that here."
        if where == "carried":
            return f"You already have the {item.lower()}."
        self.room_items[self.room].remove(item)
        self.inventory.append(item)
        return "Taken."

    def _drop(self, noun):
        item, where = self._find_item(noun)
        if where != "carried":
            return "You aren't carrying that."
        self.inventory.remove(item)
        self.room_items.setdefault(self.room, []).append(item)
        return "Dropped."

    def _examine(self, noun):
        noun = noun.replace("THE ", "").strip()
        item, where = self._find_item(noun)
        if item and item in ITEM_DESCRIPTIONS:
            if where == "here" and not self._see():
                return "You can't see a thing in here."
            return ITEM_DESCRIPTIONS[item]
        if self.room == "control" and "CONSOLE" in noun:
            status = []
            status.append("MAIN POWER: ON" if self.powered else "MAIN POWER: OFF")
            status.append("EXCITER FUSE: SEATED" if self.fuse_installed else "EXCITER FUSE: MISSING")
            status.append("DISH: 97W LOCK" if self.dish_aligned else "DISH: OFF-AZIMUTH")
            status.append("CARTRIDGE: LOADED" if self.cartridge_loaded else "CARTRIDGE: MISSING")
            return "The master console reads: " + " / ".join(status) + "."
        if self.room == "transmitter" and "PANEL" in noun:
            if self.fuse_installed:
                return "The exciter panel is closed; the new fuse is seated inside."
            return ("The service panel is screwed shut. Its stencil reads: UPLINK "
                    "EXCITER -- 5 AMP FUSE. A screwdriver would open it.")
        if self.room == "generator" and "GENERATOR" in noun:
            if self.powered:
                return "The diesel thunders away, carrying the station load."
            if self.fueled:
                return "The tank is full. The starter panel waits for someone to START it."
            return "The generator is silent. The fuel gauge reads near empty."
        if self.room == "operations" and "PHONE" in noun:
            return "A black desk telephone. The night manager's number is taped to it."
        if "COT" in noun and self.room == "bunkroom":
            if "BRASS KEY" in self.room_items.get("bunkroom", []):
                return "An Army-surplus cot. Something metallic glints beneath it."
            return "An Army-surplus cot with a thin blanket."
        return "You see nothing special."

    def _unlock(self):
        for (room, direction), lock in LOCKED_EXITS.items():
            if room == self.room and (room, direction) not in self.unlocked:
                if lock["key"] in self.inventory:
                    self.unlocked.add((room, direction))
                    self.score += 10
                    dest = ROOMS[room]["exits"][direction]
                    return (f"The {lock['key'].lower()} turns. {lock['label'].capitalize()} "
                            f"swings open. (+10)")
                return f"You need the {lock['key'].lower()}."
        return "There is nothing to unlock here."

    # -- puzzle verbs ----------------------------------------------------------
    def _use(self, noun):
        noun = noun.replace("THE ", "").strip()
        if "PHONE" in noun:
            return self._phone()
        if "FLASHLIGHT" in noun:
            if "FLASHLIGHT" not in self.inventory:
                return "You don't have a flashlight."
            return "You click the flashlight on. Its beam cuts a clean white cone."
        if "SCREWDRIVER" in noun and self.room == "transmitter":
            if "SCREWDRIVER" not in self.inventory:
                return "You don't have a screwdriver."
            if self.panel_open:
                return "The exciter panel is already open."
            self.panel_open = True
            self.score += 10
            return ("You back the screws out and swing the exciter service panel open. "
                    "The fuse socket inside is empty and scorched. (+10)")
        if "CRANK" in noun and self.room == "tower":
            return self._align()
        if "GAS" in noun and self.room == "generator":
            return self._fill("GENERATOR")
        if "CARTRIDGE" in noun and self.room == "control":
            return self._load("FEED CARTRIDGE")
        if "FUSE" in noun and self.room == "transmitter":
            return self._install("FUSE")
        return f"Nothing happens. (Try EXAMINE {noun}.)"

    def _phone(self):
        if self.room != "operations":
            return "There is no telephone here."
        return ("You dial the night manager's home number. After six rings he answers, "
                "groggy: \"Storm took the uplink? Listen -- fuel the generator, re-seat "
                "the exciter fuse in the transmitter hall, crank the dish back onto the "
                "bird, load tonight's feed cartridge in control, and key the transmitter "
                "before six. You've got this.\" He hangs up.")

    def _listen(self):
        if self.room != "relay":
            return "You hear only the night wind."
        if self.dish_aligned and self.powered:
            return ("Through the static you catch it: the rhythmic chatter of the "
                    "news-wire teletype, faint but locked. The bird is talking to you.")
        return "Only static hisses from the relay receiver. No usable signal."

    def _start(self, noun):
        if "GENERATOR" not in noun:
            return f"You can't start {noun.lower()}."
        if self.room != "generator":
            return "The generator is in the generator shack, north of the parking lot."
        if self.powered:
            return "The generator is already running."
        if not self.fueled:
            return "The starter cranks, coughs, and dies. The tank is empty -- it needs fuel."
        self.powered = True
        self.score += 20
        return ("The diesel catches with a roar. Lights stutter on across the station, "
                "the control console warms up, and somewhere the dish motors wake. (+20)")

    def _fill(self, noun):
        if "GENERATOR" not in noun and "TANK" not in noun:
            return f"You can't fill {noun.lower()}."
        if self.room != "generator":
            return "The generator is in the generator shack."
        if self.fueled:
            return "The tank is already full."
        if "GAS CAN" not in self.inventory:
            return "You have nothing to fuel it with. (The garage had a gas can.)"
        self.fueled = True
        self.inventory.remove("GAS CAN")
        self.score += 10
        return ("You pour the diesel into the generator's tank until it brims. "
                "The empty can clatters aside. (+10)")

    def _install(self, noun):
        if "FUSE" not in noun:
            return f"You can't install {noun.lower()}."
        if self.room != "transmitter":
            return "The exciter is in the transmitter hall."
        if self.fuse_installed:
            return "The fuse is already seated."
        if not self.panel_open:
            return "The exciter service panel is screwed shut. EXAMINE PANEL for a hint."
        if "FUSE" not in self.inventory:
            return "You don't have a fuse. (Parts storage keeps spares.)"
        self.inventory.remove("FUSE")
        self.fuse_installed = True
        self.score += 20
        if self.powered:
            return ("You seat the new fuse. The exciter cabinet hums alive and its "
                    "carrier lamp burns a steady green. (+20)")
        return ("You seat the new fuse in the dark cabinet. It will need main power "
                "before the exciter can wake. (+20)")

    def _align(self):
        if self.room != "tower":
            return "The dish azimuth drive is up on the tower platform."
        if "ALIGN CRANK" not in self.inventory:
            return "You need the alignment crank from the maintenance shop."
        if not self.powered:
            return ("You fit the crank, but the azimuth motors are dead -- no main power. "
                    "The dish won't budge by hand against this wind.")
        if self.dish_aligned:
            return "The dish is already locked on the bird."
        self.dish_aligned = True
        self.score += 25
        return ("You work the crank against the wind, watching the signal meter climb. "
                "It peaks, holds -- the dish locks onto the satellite. (+25)")

    def _load(self, noun):
        if "CARTRIDGE" not in noun:
            return f"You can't load {noun.lower()}."
        if self.room != "control":
            return "The console's cartridge deck is in the control room."
        if self.cartridge_loaded:
            return "A cartridge is already loaded."
        if "FEED CARTRIDGE" not in self.inventory:
            return "You don't have the feed cartridge. (Check the manager's office.)"
        self.inventory.remove("FEED CARTRIDGE")
        self.cartridge_loaded = True
        self.score += 15
        return ("You slide tonight's news-wire cartridge into the console deck. It seats "
                "with a solid clunk; the deck lamp glows amber: STANDBY. (+15)")

    def _transmit(self):
        self.transmit_attempts += 1
        if self.room != "control":
            return "The transmitter keys from the control room console."
        missing = []
        if not self.powered:
            missing.append("main power is off (start the generator)")
        if not self.fuse_installed:
            missing.append("the exciter fuse is missing")
        if not self.dish_aligned:
            missing.append("the dish is off-azimuth")
        if not self.cartridge_loaded:
            missing.append("no feed cartridge loaded")
        if missing:
            return "The console refuses: " + "; ".join(missing) + "."
        self.won = True
        bonus = min(60, MAX_MOVES - self.moves)
        self.score += bonus
        return (f"You key the transmitter. The carrier lamp flares green, the console "
                f"CRT blooms with the UPI overnight package, and at {self.clock()} the "
                f"news-wire feed rides the bird to every affiliate down the line.\n"
                f"TRANSMISSION COMPLETE -- THE 6 AM FEED IS SAVED. Time bonus +{bonus}.")

    # -- intro ------------------------------------------------------------------
    def intro(self):
        return (
            f"{TITLE}\n"
            "Earth Station 7 -- C-band uplink facility -- 23:15, Friday night.\n\n"
            "A thunderstorm has knocked out the satellite uplink. The overnight\n"
            "news-wire feed airs at 06:00, and the slot will not wait. Restore\n"
            "power, get the dish back on the bird, and put the feed on the air.\n\n"
            "Type HELP for commands. Type QUIT to end your shift."
        )


def play(app):
    """Interactive entry point: wired into the games menu by the coordinator."""
    game = NightStationGame(app)
    app.ansi_scroll(game.intro(), 0.01)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(game.describe(), 0.01)
    while not game.over:
        try:
            cmd = input("? ")
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            cmd = "QUIT"
        app.ansi_scroll(game.command(cmd), 0.01)
        app.ansi_scroll("", 0.01)
    for line in game.records_table():
        app.ansi_scroll(line, 0.01)
