"""CLASSIC GAMES ARCADE -- four 1988-authentic playable games.

HUNT THE WUMPUS: the 20-room dodecahedron cave, 5 arrows, pits and bats.
HAMURABI: a 10-year reign over grain, land, and people.
SUPER STAR TREK: a compact 8x8-galaxy quadrant campaign.
BLACKJACK: fictional-chip shoe blackjack against the dealer.

Engine design: each game is a small logic class with all state in the
object and randomness injected through a random.Random instance, so the
core math is fully testable without I/O. The play_*() functions wrap the
engines in interactive read_input loops, following the nightstation /
crossword convention. Per-member records persist through app.cis_dynamic
under RECORDS_KEY ("arcade_records").

All content here is original. Nothing references anything after
December 1988. Blackjack chips are fictional arcade tokens, not money.
"""
from cis_session import read_input as input

TITLE = "CLASSIC GAMES ARCADE"
RECORDS_KEY = "arcade_records"

GAME_LABELS = {
    "wumpus": "HUNT THE WUMPUS",
    "hamurabi": "HAMURABI",
    "startrek": "SUPER STAR TREK",
    "blackjack": "BLACKJACK",
}


# ---------------------------------------------------------------------------
# Records (mirrors the nightstation cis_dynamic pattern)
# ---------------------------------------------------------------------------

def _blank_record():
    return {"plays": 0, "wins": 0, "best": 0, "best_note": ""}


def _score_store(app):
    dyn = getattr(app, "cis_dynamic", None) if app is not None else None
    if dyn is None:
        return None, None
    try:
        return dyn.load_state(app), dyn
    except Exception:
        return None, None


def record_play(app, user_id, game_key, won, best=None, best_note=""):
    """Persist one finished game of the arcade. Idempotent per call."""
    state, dyn = _score_store(app)
    if state is None:
        return "Arcade log: offline -- no archive."
    records = state.setdefault(RECORDS_KEY, {})
    mine = records.setdefault(user_id, {})
    entry = mine.setdefault(game_key, _blank_record())
    entry["plays"] += 1
    if won:
        entry["wins"] += 1
    if best is not None and best > entry.get("best", 0):
        entry["best"] = best
        entry["best_note"] = best_note
    try:
        dyn.save_state(app, state)
    except Exception:
        pass
    return (f"ARCADE LOG: {GAME_LABELS[game_key]} -- {entry['wins']} wins in "
            f"{entry['plays']} games.")


def arcade_records_lines(state, user_id):
    """Display lines for the coordinator's PLAYER RECORDS screen."""
    mine = (state or {}).get(RECORDS_KEY, {}).get(user_id, {})
    lines = []
    order = ("wumpus", "hamurabi", "startrek", "blackjack")
    labels = {
        "wumpus": "WUMPUS",
        "hamurabi": "HAMURABI",
        "startrek": "STAR TREK",
        "blackjack": "BLACKJACK",
    }
    notes = {
        "wumpus": ("WINS", "wins", "best arrows left"),
        "hamurabi": ("REIGNS", "wins", "best score"),
        "startrek": ("VICTORIES", "wins", "best klingons down"),
        "blackjack": ("HANDS", "plays", "best chip stack"),
    }
    for key in order:
        entry = mine.get(key, _blank_record())
        tag, count_field, best_desc = notes[key]
        if key == "blackjack":
            count = entry["plays"]
        else:
            count = entry["wins"] if count_field == "wins" else entry["plays"]
        best = entry["best"]
        best_text = f"{best} {best_desc}" if best else "---"
        lines.append(f"ARCADE {labels[key]:<8} {tag} {count:<4} BEST {best_text}")
    return lines


# ===========================================================================
# 1. HUNT THE WUMPUS
# ===========================================================================

# The classic 20-room dodecahedron cave graph.
TUNNELS = {
    1: (2, 5, 8), 2: (1, 3, 10), 3: (2, 4, 12), 4: (3, 5, 14),
    5: (1, 4, 6), 6: (5, 7, 15), 7: (6, 8, 17), 8: (1, 7, 9),
    9: (8, 10, 18), 10: (2, 9, 11), 11: (10, 12, 19), 12: (3, 11, 13),
    13: (12, 14, 20), 14: (4, 13, 15), 15: (6, 14, 16), 16: (15, 17, 20),
    17: (7, 16, 18), 18: (9, 17, 19), 19: (11, 18, 20), 20: (13, 16, 19),
}

WUMPUS_ARROWS = 5


class WumpusGame:
    """Scriptable HUNT THE WUMPUS engine.

    Room numbers 1-20. rng is a random.Random used for hazard placement,
    bat teleports, arrow ricochets, and wumpus movement -- pass a seeded
    instance for deterministic tests.
    """

    def __init__(self, rng=None, app=None, user_id=None):
        import random as _random
        self.rng = rng if rng is not None else _random.Random()
        self.app = app
        self.user_id = user_id or (getattr(app, "current_user_id", None)
                            if app is not None else None) or "GUEST"
        self.player = 1
        self.wumpus = None
        self.pits = set()
        self.bats = set()
        self.arrows = WUMPUS_ARROWS
        self.moves = 0
        self.alive = True
        self.won = False
        self.wumpus_awake = False
        self._recorded = False
        self.record_line = ""

    # -- setup --------------------------------------------------------
    def reset(self):
        """Place hazards: wumpus, 2 pits, 2 bat colonies, none in room 1."""
        rooms = list(range(2, 21))
        self.rng.shuffle(rooms)
        adjacent = set(TUNNELS[1])
        wumpus_room = next(r for r in rooms if r not in adjacent)
        rest = [r for r in rooms if r != wumpus_room]
        self.wumpus = wumpus_room
        self.pits = set(rest[:2])
        self.bats = set(rest[2:4])
        self.player = 1
        self.arrows = WUMPUS_ARROWS
        self.moves = 0
        self.alive = True
        self.won = False
        self.wumpus_awake = False
        self._recorded = False

    # -- queries --------------------------------------------------------
    def warnings(self, room=None):
        """Hazard warnings the player senses from a room."""
        room = room if room is not None else self.player
        near = set(TUNNELS[room])
        near2 = set()
        for n in near:
            near2.update(TUNNELS[n])
        near2.discard(room)
        warns = []
        if self.wumpus in near or self.wumpus in near2:
            warns.append("I SMELL A WUMPUS!")
        if near & self.pits:
            warns.append("I FEEL A DRAFT!")
        if near & self.bats:
            warns.append("BATS NEARBY!")
        return warns

    # -- actions --------------------------------------------------------
    def move_to(self, room):
        """Move into an adjacent room. Returns a result code."""
        if not self.alive or self.won:
            return "OVER"
        if room not in TUNNELS[self.player]:
            return "NO_TUNNEL"
        self.player = room
        self.moves += 1
        if room == self.wumpus and not self.won:
            if self.wumpus_awake:
                return self._wumpus_stirs()
            self.alive = False
            return "EATEN"
        if room in self.pits:
            self.alive = False
            return "PIT"
        if room in self.bats:
            return self._bat_carry()
        return "MOVED"

    def _bat_carry(self):
        dest = self.rng.choice([r for r in range(1, 21) if r != self.player])
        self.player = dest
        if dest == self.wumpus:
            self.alive = False
            return "EATEN"
        if dest in self.pits:
            self.alive = False
            return "PIT"
        if dest in self.bats:
            return self._bat_carry()
        return "BATS"

    def _wumpus_stirs(self):
        """Wumpus may flee to a neighboring room when startled."""
        options = [n for n in TUNNELS[self.wumpus]]
        self.wumpus = self.rng.choice(options)
        if self.wumpus == self.player:
            self.alive = False
            return "EATEN"
        return "FLED"

    def fire(self, path):
        """Fire an arrow along up to 5 room numbers. Returns a result code."""
        if not self.alive or self.won:
            return "OVER"
        if self.arrows <= 0:
            return "NO_ARROWS"
        self.arrows -= 1
        room = self.player
        rooms = [int(r) for r in path[:5]]
        for nxt in rooms:
            if nxt not in TUNNELS[room]:
                nxt = self.rng.choice(TUNNELS[room])
            room = nxt
            if room == self.wumpus:
                self.won = True
                self._finish(True)
                return "KILL"
            if room == self.player:
                self.alive = False
                self._finish(False)
                return "SUICIDE"
        # Miss: the wumpus usually wakes and moves.
        if self.rng.random() < 0.75:
            self.wumpus_awake = True
            result = self._wumpus_stirs()
            if result == "EATEN":
                self._finish(False)
                return "EATEN"
            return "MISS_MOVED"
        self.wumpus_awake = True
        return "MISS"

    # -- records ----------------------------------------------------------
    def _finish(self, won):
        if self._recorded:
            return
        self._recorded = True
        self.record_line = record_play(self.app, self.user_id, "wumpus", won,
                                       best=self.arrows if won else None,
                                       best_note="arrows left")

    def quit(self):
        self.alive = False
        self._finish(False)


def wumpus_intro():
    return (
        "HUNT THE WUMPUS\n"
        "The Wumpus lives in a cave of 20 rooms. Each room has 3 tunnels.\n"
        "Hazards: 2 bottomless pits, 2 colonies of super bats, and the Wumpus.\n\n"
        "Warnings you can sense:\n"
        "  I SMELL A WUMPUS  -- the Wumpus is 1 or 2 rooms away\n"
        "  I FEEL A DRAFT    -- a pit is in an adjacent room\n"
        "  BATS NEARBY       -- bats are in an adjacent room\n\n"
        "Commands: M <room> to move, S <r1> <r2> ... to shoot a crooked arrow\n"
        "(up to 5 rooms), H for help, Q to quit.\n"
        f"You carry {WUMPUS_ARROWS} arrows. Good hunting."
    )


def play_wumpus(app, user_id):
    game = WumpusGame(app=app, user_id=user_id)
    game.reset()
    print(wumpus_intro())
    print()
    while game.alive and not game.won:
        print(f"You are in room {game.player}. Tunnels to {', '.join(map(str, TUNNELS[game.player]))}.")
        for warn in game.warnings():
            print(warn)
        print(f"Arrows: {game.arrows}  Moves: {game.moves}")
        try:
            raw = input("wumpus> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = "Q"
        if not raw:
            continue
        parts = raw.split()
        verb = parts[0]
        if verb in ("Q", "QUIT", "M"):
            game.quit()
            print("You crawl out of the cave, empty-handed.")
            break
        if verb == "H":
            print(wumpus_intro())
            continue
        if verb == "M" or verb == "MOVE":
            if len(parts) < 2 or not parts[1].isdigit():
                print("Move where? M <room number>")
                continue
            result = game.move_to(int(parts[1]))
            if result == "NO_TUNNEL":
                print("No tunnel leads there from this room.")
            elif result == "EATEN":
                print("...Oops! Bumped a WUMPUS!")
            elif result == "PIT":
                print("YYYYIIIIEEEE... fell into a pit!")
            elif result == "BATS":
                print("ZAP -- Super Bat snatch! They drop you in another room.")
                print(f"You are in room {game.player}.")
            elif result == "FLED":
                print("You startled the Wumpus -- it fled to another room!")
            continue
        if verb in ("S", "SHOOT"):
            rooms = [p for p in parts[1:] if p.isdigit()]
            if not rooms:
                print("Shoot where? S <room> [<room> ...]  (up to 5 rooms)")
                continue
            result = game.fire([int(r) for r in rooms])
            if result == "KILL":
                print("A-HA! You got the Wumpus!")
            elif result == "SUICIDE":
                print("Ouch! Arrow got you!")
            elif result == "MISS_MOVED":
                print("Missed. You woke the Wumpus -- it has moved!")
            elif result == "MISS":
                print("Missed.")
            elif result == "EATEN":
                print("The Wumpus fled into YOUR room. ...Oops!")
            elif result == "NO_ARROWS":
                print("You are out of arrows!")
            continue
        print("I don't understand. M <room>, S <rooms>, H, or Q.")
    if game.won:
        print(f"WUMPUS SLAIN in {game.moves} moves with {game.arrows} arrows to spare!")
    if not game._recorded:
        game._finish(game.won)
    print(game.record_line)


# ===========================================================================
# 2. HAMURABI
# ===========================================================================

HAMURABI_YEARS = 10
HAMURABI_START = {"population": 100, "grain": 2800, "land": 1000}


class HamurabiGame:
    """Scriptable HAMURABI engine.

    One year is resolved by play_year(actions) where actions is a dict
    with keys buy, sell, feed, plant (all ints). Returns a report dict.
    rng is injected for deterministic tests.
    """

    def __init__(self, rng=None, app=None, user_id=None):
        import random as _random
        self.rng = rng if rng is not None else _random.Random()
        self.app = app
        self.user_id = user_id or (getattr(app, "current_user_id", None)
                            if app is not None else None) or "GUEST"
        self.year = 0
        self.population = HAMURABI_START["population"]
        self.grain = HAMURABI_START["grain"]
        self.land = HAMURABI_START["land"]
        self.total_dead = 0
        self.total_born = 0
        self.impeached = False
        self.over = False
        self._recorded = False
        self.record_line = ""
        self.price = self.land_price()

    def land_price(self):
        return 17 + self.rng.randint(1, 10)

    def validate(self, buy, sell, feed, plant):
        """Return an error string, or None if the year's actions are legal."""
        if buy < 0 or sell < 0 or feed < 0 or plant < 0:
            return "Negative numbers are not allowed, O great one."
        if buy > 0 and sell > 0:
            return "Buy or sell, not both."
        if sell > self.land:
            return f"You own only {self.land} acres."
        cost = buy * self.price
        if cost > self.grain:
            return f"You have only {self.grain} bushels; {buy} acres cost {cost}."
        grain_after_land = self.grain - cost + sell * self.price
        if feed > grain_after_land:
            return f"You have only {grain_after_land} bushels to feed with."
        grain_after_feed = grain_after_land - feed
        if plant > self.land + buy - sell:
            return f"You own only {self.land + buy - sell} acres to plant."
        if plant > 10 * self.population:
            return f"Each citizen can tend 10 acres: at most {10 * self.population}."
        if plant // 2 > grain_after_feed:
            return "Planting takes seed grain: 1 bushel plants 2 acres."
        return None

    def play_year(self, buy=0, sell=0, feed=0, plant=0):
        """Resolve one year. Returns a report dict."""
        error = self.validate(buy, sell, feed, plant)
        if error:
            return {"ok": False, "error": error}
        self.year += 1
        land = self.land + buy - sell
        grain = self.grain - buy * self.price + sell * self.price
        # Feed the people: 20 bushels each.
        grain -= feed
        fed_people = feed // 20
        starved = max(0, self.population - fed_people)
        if starved > 0:
            self.total_dead += starved
            population = self.population - starved
        else:
            population = self.population
        # Plague: 15% chance, halves the survivors.
        plague = self.rng.random() < 0.15
        if plague:
            lost = population // 2
            self.total_dead += lost
            population -= lost
        # Planting costs seed: 1 bushel per 2 acres.
        seed_cost = plant // 2
        grain -= seed_cost
        # Harvest: 1-6 bushels per planted acre.
        yield_per_acre = self.rng.randint(1, 6)
        harvest = plant * yield_per_acre
        grain += harvest
        # Rats: even years, eat 1/C of the stores.
        rats_ate = 0
        if self.year % 2 == 0 and grain > 0:
            rats_ate = grain // self.rng.randint(1, 5)
            grain -= rats_ate
        # Births and immigrants.
        births = self.population // 25 + self.rng.randint(0, 9)
        immigrants = 5
        population += births + immigrants
        self.total_born += births + immigrants
        # Impeachment: starved more than 45% in a single year.
        starve_ratio = (starved / self.population) if self.population else 0
        if starve_ratio > 0.45:
            self.impeached = True
            self.over = True
        self.population = population
        self.grain = grain
        self.land = land
        if self.year >= HAMURABI_YEARS:
            self.over = True
        self.price = self.land_price()
        report = {
            "ok": True, "year": self.year, "starved": starved,
            "plague": plague, "yield": yield_per_acre, "harvest": harvest,
            "rats": rats_ate, "births": births, "immigrants": immigrants,
            "population": self.population, "grain": self.grain,
            "land": self.land, "price": self.price,
            "impeached": self.impeached, "over": self.over,
        }
        if self.over:
            self._finish()
        return report

    def final_score(self):
        """End-of-reign score 0-100, classic style."""
        deaths_ratio = self.total_dead / max(1, self.total_born + 100)
        acres_per_person = self.land / max(1, self.population)
        score = int(100 - deaths_ratio * 200 + acres_per_person * 2)
        return max(0, min(100, score))

    def epitaph(self):
        score = self.final_score()
        if self.impeached:
            return ("You have been impeached and thrown out of office! "
                    "The people rejoice at your downfall.")
        if score >= 80:
            return "A fantastic performance! Charlemagne, Disraeli, and Jefferson combined could not have done better!"
        if score >= 50:
            return "Your performance could have been better, but really wasn't too bad at all."
        return "Your heavy-handed performance smacks of Nero and Ivan IV. The people (remaining) find you an unpleasant ruler."

    def _finish(self):
        if self._recorded:
            return
        self._recorded = True
        won = not self.impeached
        self.record_line = record_play(self.app, self.user_id, "hamurabi", won,
                                       best=self.final_score() if won else None,
                                       best_note="score")


def hamurabi_intro():
    return (
        "HAMURABI\n"
        "Try your hand at governing ancient Sumeria for 10 years.\n"
        "You begin with 100 people, 2800 bushels of grain, 1000 acres of land.\n"
        "Each year: buy/sell land, feed your people (20 bushels each),\n"
        "and plant seed (1 bushel plants 2 acres; each citizen tends 10).\n"
        "Beware rats, plague, and starvation -- starve 45% and you are impeached!")


def _ask_int(prompt, minimum=0):
    while True:
        try:
            raw = input(prompt).strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw in ("Q", "QUIT", "M"):
            return None
        if raw.lstrip("-").isdigit():
            value = int(raw)
            if value >= minimum:
                return value
        print(f"Enter a whole number of {minimum} or more (or Q to quit).")


def play_hamurabi(app, user_id):
    game = HamurabiGame(app=app, user_id=user_id)
    print(hamurabi_intro())
    print()
    while not game.over:
        print(f"--- YEAR {game.year + 1} of {HAMURABI_YEARS} ---")
        print(f"Population: {game.population}  Grain: {game.grain} bushels  "
              f"Land: {game.land} acres  Land price: {game.price} bushels/acre")
        buy = _ask_int("Acres to BUY [0]? ")
        if buy is None:
            print("You abdicate the throne.")
            game._finish()
            return
        sell = 0
        if buy == 0:
            sell = _ask_int("Acres to SELL [0]? ")
            if sell is None:
                print("You abdicate the throne.")
                game._finish()
                return
        feed = _ask_int("Bushels to FEED the people? ")
        if feed is None:
            print("You abdicate the throne.")
            game._finish()
            return
        plant = _ask_int("Acres to PLANT with seed? ")
        if plant is None:
            print("You abdicate the throne.")
            game._finish()
            return
        report = game.play_year(buy=buy, sell=sell, feed=feed, plant=plant)
        if not report["ok"]:
            print(report["error"])
            continue  # validation failed: the year was not resolved, try again
        print()
        if report["starved"]:
            print(f"{report['starved']} citizens starved.")
        if report["plague"]:
            print("A horrible plague struck! Half the people died.")
        print(f"Harvest: {report['yield']} bushels/acre, {report['harvest']} bushels gathered.")
        if report["rats"]:
            print(f"Rats ate {report['rats']} bushels.")
        print(f"{report['births']} children were born; {report['immigrants']} came to the city.")
        print()
    print(f"--- END OF REIGN: year {game.year} ---")
    print(f"Final population: {game.population}, grain: {game.grain}, land: {game.land}.")
    print(f"Score: {game.final_score()} of 100.")
    print(game.epitaph())
    if not game._recorded:
        game._finish()
    print(game.record_line)


# ===========================================================================
# 3. SUPER STAR TREK
# ===========================================================================

TREK_SIZE = 8
TREK_COMMANDS = ("NAV", "SRS", "LRS", "PHA", "TOR", "SHE", "DAM", "COM", "XXX")


class StarTrekGame:
    """Compact SUPER STAR TREK engine at quadrant resolution.

    The galaxy is an 8x8 grid of quadrants. Each quadrant holds klingons,
    optionally a starbase, and stars. Combat, navigation, energy, shields,
    torpedoes, and stardates are all modeled; sectors are abstracted away.
    rng is injected for deterministic tests.
    """

    def __init__(self, rng=None, app=None, user_id=None):
        import random as _random
        self.rng = rng if rng is not None else _random.Random()
        self.app = app
        self.user_id = user_id or (getattr(app, "current_user_id", None)
                            if app is not None else None) or "GUEST"
        self.galaxy = {}
        self.enterprise = (0, 0)
        self.klingons_total = 0
        self.energy = 3000
        self.shields = 0
        self.torpedoes = 10
        self.stardate = 0
        self.deadline = 0
        self.damaged = {}       # system -> stardates of repair remaining
        self.over = False
        self.won = False
        self._recorded = False
        self.record_line = ""

    def new_mission(self, klingons=None):
        size = TREK_SIZE
        total = klingons if klingons is not None else self.rng.randint(12, 20)
        self.klingons_total = total
        bases = max(2, total // 6)
        quads = [(x, y) for x in range(size) for y in range(size)]
        self.rng.shuffle(quads)
        self.galaxy = {q: {"klingons": [], "starbase": False, "stars": 0}
                       for q in quads}
        for i in range(total):
            q = quads[i % len(quads)]
            power = self.rng.randint(100, 300)
            self.galaxy[q]["klingons"].append(power)
        base_quads = self.rng.sample(quads, bases)
        for q in base_quads:
            self.galaxy[q]["starbase"] = True
        for q in quads:
            self.galaxy[q]["stars"] = self.rng.randint(0, 6)
        start = self.rng.choice(quads)
        self.enterprise = start
        self.energy = 3000
        self.shields = 0
        self.torpedoes = 10
        self.stardate = 3000 + self.rng.randint(0, 30)
        self.deadline = self.stardate + 25 + total
        self.damaged = {}
        self.over = False
        self.won = False

    # -- queries --------------------------------------------------------
    def quadrant(self):
        return self.galaxy[self.enterprise]

    def klingons_left(self):
        return sum(len(q["klingons"]) for q in self.galaxy.values())

    def klingons_down(self):
        return self.klingons_total - self.klingons_left()

    def condition(self):
        if self.quadrant()["klingons"]:
            return "RED"
        if self.energy < 1000:
            return "YELLOW"
        return "GREEN"

    def status_lines(self):
        lines = [
            f"Stardate {self.stardate}  (mission ends {self.deadline})",
            f"Quadrant {self.enterprise[0]},{self.enterprise[1]}  Condition {self.condition()}",
            f"Energy {self.energy}  Shields {self.shields}  Torpedoes {self.torpedoes}",
            f"Klingons remaining: {self.klingons_left()} of {self.klingons_total}",
        ]
        if self.damaged:
            lines.append("Damaged: " + ", ".join(
                f"{sys} ({t} sd)" for sys, t in sorted(self.damaged.items())))
        else:
            lines.append("All systems operational.")
        return lines

    # -- scans ------------------------------------------------------------
    def srs(self):
        """Short-range scan: this quadrant and its neighbors."""
        x0, y0 = self.enterprise
        lines = ["--- SHORT RANGE SCAN ---"]
        for dy in (-1, 0, 1):
            row = []
            for dx in (-1, 0, 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < TREK_SIZE and 0 <= y < TREK_SIZE:
                    q = self.galaxy[(x, y)]
                    mark = "E" if (x, y) == self.enterprise else "."
                    if q["klingons"]:
                        mark = "K"
                    elif q["starbase"]:
                        mark = "B"
                    row.append(mark)
                else:
                    row.append(" ")
            lines.append(" ".join(row))
        here = self.quadrant()
        lines.append(f"Klingons here: {len(here['klingons'])}  "
                     f"Starbase: {'YES' if here['starbase'] else 'no'}  "
                     f"Stars: {here['stars']}")
        return lines

    def lrs(self):
        """Long-range scan: 3x3 neighborhood summary."""
        x0, y0 = self.enterprise
        lines = ["--- LONG RANGE SCAN ---"]
        for dy in (-1, 0, 1):
            row = []
            for dx in (-1, 0, 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < TREK_SIZE and 0 <= y < TREK_SIZE:
                    q = self.galaxy[(x, y)]
                    code = len(q["klingons"]) * 100 + (1000 if q["starbase"] else 0) + q["stars"]
                    row.append(f"{code:03d}")
                else:
                    row.append("***")
            lines.append(" ".join(row))
        lines.append("Code: hundreds=Klingons, +1000=starbase, rest=stars.")
        return lines

    # -- systems ------------------------------------------------------------
    def _system_ok(self, system):
        return self.damaged.get(system, 0) <= 0

    def _damage_chance(self, amount):
        if amount <= 0 or self.rng.random() > 0.25:
            return
        system = self.rng.choice(["NAV", "PHA", "TOR", "SHE", "SRS", "LRS"])
        self.damaged[system] = self.rng.randint(1, 3)

    def _repair_tick(self, stardates=1):
        for system in list(self.damaged):
            self.damaged[system] -= stardates
            if self.damaged[system] <= 0:
                del self.damaged[system]

    def _klingon_attack(self):
        """Klingons in the quadrant fire back. Returns log lines."""
        log = []
        for power in list(self.quadrant()["klingons"]):
            if not self.over:
                hit = int(power * (0.5 + self.rng.random() * 0.5))
                absorbed = min(self.shields, hit)
                self.shields -= absorbed
                hull = hit - absorbed
                self.energy -= hull
                self._damage_chance(hull)
                log.append(f"Klingon fires: {hit} units "
                           f"({absorbed} absorbed by shields, {hull} to hull).")
                if self.energy <= 0:
                    self.energy = 0
                    self.over = True
                    log.append("The Enterprise has been destroyed!")
        return log

    def _check_time(self):
        if self.stardate >= self.deadline and not self.over:
            self.over = True
            return ["Time has run out. The Klingon fleet overruns the sector."]
        return []

    # -- commands -----------------------------------------------------------
    def nav(self, x, y):
        """Warp to quadrant (x, y). Returns log lines."""
        log = []
        if not self._system_ok("NAV"):
            return ["Warp engines damaged!"]
        if not (0 <= x < TREK_SIZE and 0 <= y < TREK_SIZE):
            return ["Coordinates out of range (0-7)."]
        dist = abs(x - self.enterprise[0]) + abs(y - self.enterprise[1])
        cost = dist * 40
        if dist == 0:
            return self.dock()
        if cost > self.energy:
            return [f"Insufficient energy for warp {dist} (needs {cost})."]
        self.energy -= cost
        self.enterprise = (x, y)
        self.stardate += 1
        self._repair_tick(1)
        log.append(f"Warp to quadrant {x},{y}. Energy -{cost}.")
        here = self.quadrant()
        if here["klingons"]:
            log.append(f"{len(here['klingons'])} Klingon(s) in this quadrant!")
        log.extend(self._klingon_attack())
        log.extend(self._check_time())
        self._check_victory(log)
        return log

    def dock(self):
        here = self.quadrant()
        if not here["starbase"]:
            return ["No starbase in this quadrant."]
        self.energy = 3000
        self.shields = 0
        self.torpedoes = 10
        self.damaged = {}
        self.stardate += 1
        self._repair_tick(1)
        return ["Docked at starbase: energy, shields, torpedoes restored; "
                "all systems repaired."]

    def phasers(self, amount):
        """Fire phasers; damage splits across klingons here."""
        log = []
        if not self._system_ok("PHA"):
            return ["Phaser banks damaged!"]
        here = self.quadrant()
        if not here["klingons"]:
            return ["No Klingons in this quadrant."]
        if amount <= 0:
            return ["Specify a positive energy amount."]
        if amount > self.energy:
            return [f"Insufficient energy ({self.energy} available)."]
        self.energy -= amount
        units = amount * (0.6 + self.rng.random() * 0.4)
        per = units / len(here["klingons"])
        destroyed = []
        for i, power in enumerate(here["klingons"]):
            hit = int(per * (0.7 + self.rng.random() * 0.6))
            if hit >= power:
                destroyed.append(i)
                log.append(f"Phasers strike for {hit}: Klingon destroyed!")
            else:
                here["klingons"][i] = power - hit
                log.append(f"Phasers strike for {hit}: Klingon damaged "
                           f"(hull {here['klingons'][i]}).")
        for i in sorted(destroyed, reverse=True):
            del here["klingons"][i]
        self.stardate += 1
        self._repair_tick(1)
        log.extend(self._klingon_attack())
        log.extend(self._check_time())
        self._check_victory(log)
        return log

    def torpedo(self, x, y):
        """Fire a photon torpedo at quadrant (x, y). Returns log lines."""
        log = []
        if not self._system_ok("TOR"):
            return ["Torpedo tubes damaged!"]
        if self.torpedoes <= 0:
            return ["No torpedoes remaining!"]
        if not (0 <= x < TREK_SIZE and 0 <= y < TREK_SIZE):
            return ["Coordinates out of range (0-7)."]
        self.torpedoes -= 1
        ex, ey = self.enterprise
        if abs(x - ex) > 1 or abs(y - ey) > 1:
            log.append("Torpedo range is one quadrant -- it fizzles into the void.")
            return log
        target = self.galaxy[(x, y)]
        if not target["klingons"]:
            log.append("Torpedo detonates harmlessly: no Klingons there.")
        elif self.rng.random() < 0.85:
            target["klingons"].pop(0)
            log.append("Direct hit! Klingon destroyed!")
        else:
            log.append("Torpedo missed!")
        self.stardate += 1
        self._repair_tick(1)
        log.extend(self._klingon_attack())
        log.extend(self._check_time())
        self._check_victory(log)
        return log

    def shields_cmd(self, amount):
        """Transfer energy to (+) or from (-) shields."""
        if not self._system_ok("SHE"):
            return ["Shield control damaged!"]
        if amount > 0 and amount > self.energy:
            return [f"Insufficient energy ({self.energy} available)."]
        if amount < 0 and -amount > self.shields:
            return [f"Only {self.shields} units on the shields."]
        self.energy -= amount
        self.shields += amount
        return [f"Shields now {self.shields}; energy {self.energy}."]

    def damage_report(self):
        lines = ["--- DAMAGE CONTROL ---"]
        if not self.damaged:
            lines.append("All systems operational.")
        else:
            for system in sorted(self.damaged):
                lines.append(f"{system}: under repair, {self.damaged[system]} stardate(s) remaining.")
        lines.append(f"Energy {self.energy}  Shields {self.shields}  Torpedoes {self.torpedoes}")
        return lines

    def _check_victory(self, log):
        if not self.over and self.klingons_left() == 0:
            self.won = True
            self.over = True
            log.append("All Klingons destroyed. The sector is safe. MISSION ACCOMPLISHED!")
            self._finish()

    def _finish(self):
        if self._recorded:
            return
        self._recorded = True
        self.record_line = record_play(self.app, self.user_id, "startrek", self.won,
                                       best=self.klingons_down() if self.won else None,
                                       best_note="klingons down")


def trek_intro():
    return (
        "SUPER STAR TREK\n"
        "The Klingon fleet has invaded an 8x8-quadrant sector. You command\n"
        "the starship Enterprise: 3000 energy, 10 torpedoes, deflector shields.\n"
        "Destroy every Klingon before the stardate deadline. Dock at a\n"
        "starbase quadrant (B on the scan) to repair and refuel.\n\n"
        "Commands:\n"
        "  NAV x y   warp to quadrant (dock if already there and a base exists)\n"
        "  SRS       short-range scan        LRS   long-range scan\n"
        "  PHA n     fire n energy of phasers   TOR x y  fire torpedo\n"
        "  SHE n     raise (+) / lower (-) shields by n energy\n"
        "  DAM       damage report           COM   status report\n"
        "  XXX       resign command          H     this help")


def play_startrek(app, user_id):
    game = StarTrekGame(app=app, user_id=user_id)
    game.new_mission()
    print(trek_intro())
    print()
    print(f"{game.klingons_total} Klingons detected. Mission ends at stardate {game.deadline}.")
    print()
    while not game.over:
        for line in game.status_lines():
            print(line)
        try:
            raw = input("trek> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = "XXX"
        if not raw:
            continue
        parts = raw.split()
        verb = parts[0]
        args = parts[1:]
        if verb == "XXX":
            print("You resign your command. The fleet mourns.")
            game._finish()
            break
        if verb == "H":
            print(trek_intro())
            continue
        if verb == "SRS":
            for line in game.srs():
                print(line)
            continue
        if verb == "LRS":
            for line in game.lrs():
                print(line)
            continue
        if verb == "DAM":
            for line in game.damage_report():
                print(line)
            continue
        if verb == "COM":
            print("STATUS REPORT:")
            for line in game.status_lines():
                print("  " + line)
            continue
        if verb == "NAV" and len(args) == 2 and all(a.isdigit() for a in args):
            for line in game.nav(int(args[0]), int(args[1])):
                print(line)
            print()
            continue
        if verb == "PHA" and len(args) == 1 and args[0].isdigit():
            for line in game.phasers(int(args[0])):
                print(line)
            print()
            continue
        if verb == "TOR" and len(args) == 2 and all(a.isdigit() for a in args):
            for line in game.torpedo(int(args[0]), int(args[1])):
                print(line)
            print()
            continue
        if verb == "SHE" and len(args) == 1 and args[0].lstrip("+-").isdigit():
            for line in game.shields_cmd(int(args[0])):
                print(line)
            continue
        print("Unknown command. Valid: NAV SRS LRS PHA TOR SHE DAM COM XXX  (H for help)")
    if game.won:
        print(f"VICTORY at stardate {game.stardate}: {game.klingons_down()} Klingons destroyed.")
    elif game.over:
        print("MISSION FAILED.")
    if not game._recorded:
        game._finish()
    print(game.record_line)


# ===========================================================================
# 4. BLACKJACK
# ===========================================================================

BLACKJACK_START_CHIPS = 500
BLACKJACK_PAY = 1.5  # blackjack pays 3:2
SUITS = ("S", "H", "D", "C")
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


def make_shoe(num_decks=4, rng=None):
    """Build and shuffle a multi-deck shoe. Cards are 'RANK+SUIT' strings."""
    import random as _random
    rng = rng if rng is not None else _random.Random()
    shoe = [rank + suit for _ in range(num_decks) for suit in SUITS for rank in RANKS]
    rng.shuffle(shoe)
    return shoe


def card_name(card):
    rank, suit = card[:-1], card[-1]
    suits = {"S": "spades", "H": "hearts", "D": "diamonds", "C": "clubs"}
    ranks = {"A": "Ace", "J": "Jack", "Q": "Queen", "K": "King"}
    return f"{ranks.get(rank, rank)} of {suits[suit]}"


def hand_value(cards):
    """Return (total, soft) where soft means an ace counts as 11."""
    total = 0
    aces = 0
    for card in cards:
        rank = card[:-1]
        if rank == "A":
            aces += 1
            total += 11
        elif rank in ("J", "Q", "K"):
            total += 10
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total, aces > 0


def is_blackjack(cards):
    return len(cards) == 2 and hand_value(cards)[0] == 21


def settle(player_cards, dealer_cards, bet):
    """Settle one hand. Returns (outcome, chip_delta).

    outcome is one of: 'blackjack', 'win', 'lose', 'push', 'bust', 'dealer_bust'.
    """
    player = hand_value(player_cards)[0]
    dealer = hand_value(dealer_cards)[0]
    player_bj = is_blackjack(player_cards)
    dealer_bj = is_blackjack(dealer_cards)
    if player_bj and dealer_bj:
        return "push", 0
    if player_bj:
        return "blackjack", int(bet * BLACKJACK_PAY)
    if dealer_bj:
        return "lose", -bet
    if player > 21:
        return "bust", -bet
    if dealer > 21:
        return "dealer_bust", bet
    if player > dealer:
        return "win", bet
    if player < dealer:
        return "lose", -bet
    return "push", 0


def dealer_play(shoe, dealer_cards):
    """Dealer draws to 17, standing on all 17s. Returns final hand."""
    cards = list(dealer_cards)
    while hand_value(cards)[0] < 17:
        cards.append(shoe.pop())
    return cards


class BlackjackGame:
    """Fictional-chip blackjack against the house dealer."""

    def __init__(self, rng=None, app=None, user_id=None, chips=BLACKJACK_START_CHIPS):
        import random as _random
        self.rng = rng if rng is not None else _random.Random()
        self.app = app
        self.user_id = user_id or (getattr(app, "current_user_id", None)
                            if app is not None else None) or "GUEST"
        self.chips = chips
        self.hands = 0
        self.wins = 0
        self.shoe = make_shoe(4, self.rng)
        self.best = chips
        self._recorded = False
        self.record_line = ""

    def _reshuffle_if_low(self):
        if len(self.shoe) < 20:
            self.shoe = make_shoe(4, self.rng)

    def deal(self):
        self._reshuffle_if_low()
        player = [self.shoe.pop(), self.shoe.pop()]
        dealer = [self.shoe.pop(), self.shoe.pop()]
        return player, dealer

    def play_hand(self, bet, actions):
        """Play one hand non-interactively.

        actions: list of 'H' (hit), 'S' (stand), 'D' (double down, first
        decision only). Returns (player, dealer, outcome, delta).
        """
        player, dealer = self.deal()
        doubled = False
        for i, action in enumerate(actions):
            action = action.upper()
            if action == "D" and i == 0 and len(player) == 2 and self.chips >= bet * 2:
                bet *= 2
                doubled = True
                player.append(self.shoe.pop())
                break
            if action == "H":
                player.append(self.shoe.pop())
                if hand_value(player)[0] > 21:
                    break
            else:  # S or anything else stands
                break
        if hand_value(player)[0] <= 21 and not is_blackjack(player):
            dealer = dealer_play(self.shoe, dealer)
        outcome, delta = settle(player, dealer, bet)
        self.chips += delta
        self.hands += 1
        if delta > 0:
            self.wins += 1
        self.best = max(self.best, self.chips)
        if self.chips <= 0:
            self._finish_session()
        return player, dealer, outcome, delta

    def _finish_session(self):
        if self._recorded:
            return
        self._recorded = True
        self.record_line = record_play(self.app, self.user_id, "blackjack", self.wins > 0,
                                       best=self.best, best_note="chips")

    def quit(self):
        self._finish_session()


def blackjack_intro():
    return (
        "BLACKJACK\n"
        "The dealer's shoe holds four decks. These are ARCADE CHIPS --\n"
        "fictional tokens for the game room only, worth nothing but pride.\n"
        f"You start with {BLACKJACK_START_CHIPS} chips. Blackjack pays 3 to 2.\n"
        "Dealer stands on all 17s.\n\n"
        "Each round: place a BET, then H to hit, S to stand, D to double down.\n"
        "Q quits the table and banks your stack on the arcade record.")


def _show_hand(label, cards, hide_hole=False):
    if hide_hole:
        visible = [card_name(cards[0]), "a face-down card"]
        return f"{label}: {', '.join(visible)}"
    total, soft = hand_value(cards)
    names = ", ".join(card_name(c) for c in cards)
    return f"{label}: {names}  ({total}{' soft' if soft else ''})"


def play_blackjack(app, user_id):
    game = BlackjackGame(app=app, user_id=user_id)
    print(blackjack_intro())
    print()
    while game.chips > 0:
        print(f"You hold {game.chips} chips.  (Hands: {game.hands}, won: {game.wins})")
        try:
            raw = input("Bet how many chips (Q to quit)? ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = "Q"
        if raw in ("Q", "QUIT", "M"):
            break
        if not raw.isdigit() or int(raw) <= 0:
            print("Enter a whole-number bet.")
            continue
        bet = int(raw)
        if bet > game.chips:
            print(f"You hold only {game.chips} chips.")
            continue
        player, dealer = game.deal()
        print(_show_hand("You", player))
        print(_show_hand("Dealer", dealer, hide_hole=True))
        doubled = False
        while True:
            total, _ = hand_value(player)
            if is_blackjack(player) or total > 21:
                break
            prompt = "H)it, S)tand" + (", D)ouble down" if len(player) == 2 and bet * 2 <= game.chips else "") + "? "
            try:
                choice = input(prompt).strip().upper()
            except (EOFError, KeyboardInterrupt):
                print()
                choice = "S"
            if choice == "H":
                player.append(game.shoe.pop())
                print(_show_hand("You", player))
            elif choice == "D" and len(player) == 2 and bet * 2 <= game.chips:
                bet *= 2
                doubled = True
                player.append(game.shoe.pop())
                print(_show_hand("You", player) + "  (doubled)")
                break
            elif choice in ("S", "Q", "M"):
                break
            else:
                print("H, S, or D.")
        player_total, _ = hand_value(player)
        if player_total <= 21 and not is_blackjack(player):
            dealer = dealer_play(game.shoe, dealer)
        outcome, delta = settle(player, dealer, bet)
        game.chips += delta
        game.hands += 1
        if delta > 0:
            game.wins += 1
        game.best = max(game.best, game.chips)
        print(_show_hand("Dealer", dealer))
        messages = {
            "blackjack": f"BLACKJACK! You win {delta} chips.",
            "win": f"You win {delta} chips{' (doubled)' if doubled else ''}.",
            "dealer_bust": f"Dealer busts! You win {delta} chips{' (doubled)' if doubled else ''}.",
            "push": "Push. Your bet is returned.",
            "bust": f"Bust! You lose {bet} chips.",
            "lose": f"Dealer wins. You lose {bet} chips.",
        }
        print(messages[outcome])
        print()
        if game.chips <= 0:
            print("You are out of chips. The dealer wishes you better luck.")
            break
    game.quit()
    print(f"Session over: {game.hands} hands, {game.wins} won, best stack {game.best}.")
    if not game._recorded:
        game._finish_session()
    print(game.record_line)


# ===========================================================================
# Arcade submenu
# ===========================================================================

ARCADE_MENU = (
    ("1", "HUNT THE WUMPUS", "Stalk the beast through 20 rooms with 5 arrows."),
    ("2", "HAMURABI", "Rule Sumeria for 10 years: grain, land, and fate."),
    ("3", "SUPER STAR TREK", "Hunt Klingons across an 8x8-quadrant sector."),
    ("4", "BLACKJACK", "Beat the dealer with fictional arcade chips."),
)


def arcade_menu_text():
    lines = [
        "      ___ CLASSIC GAMES ARCADE ___",
        "  The game room never closes. Insert coin -- just kidding,",
        "  connect time is coin enough already.",
        "",
    ]
    for key, name, blurb in ARCADE_MENU:
        lines.append(f"  {key}  {name}")
        lines.append(f"     {blurb}")
    lines.append("  M  Return to the Games menu")
    return lines


def play(app):
    """Interactive entry point: wired into the games menu by the coordinator."""
    user_id = getattr(app, "current_user_id", None) or "GUEST"
    handlers = {
        "1": play_wumpus,
        "2": play_hamurabi,
        "3": play_startrek,
        "4": play_blackjack,
    }
    while True:
        for line in arcade_menu_text():
            print(line)
        print()
        try:
            choice = input("arcade> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "M"
        if choice in ("M", "Q", "QUIT"):
            return
        if choice in handlers:
            print()
            handlers[choice](app, user_id)
            print()
            continue
        print("Pick 1-4, or M to return.")
