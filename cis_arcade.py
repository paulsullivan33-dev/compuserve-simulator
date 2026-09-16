"""CLASSIC GAMES ARCADE -- six 1988-authentic playable games.

HUNT THE WUMPUS: the 20-room dodecahedron cave, 5 arrows, pits and bats.
HAMURABI: a 10-year reign over grain, land, and people.
SUPER STAR TREK: a compact 8x8-galaxy quadrant campaign.
BLACKJACK: fictional-chip shoe blackjack against the dealer.
ELIZA: the 1966 computer therapist, a bulletin-board staple.
LUNAR LANDER: the 1970s BASIC classic -- burn fuel, mind gravity.

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
    "eliza": "ELIZA",
    "lander": "LUNAR LANDER",
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


def record_eliza_session(app, user_id):
    """Log one finished ELIZA conversation.

    Increments the per-user ``eliza_sessions`` counter under RECORDS_KEY,
    mirroring the nightstation cis_dynamic pattern.
    """
    state, dyn = _score_store(app)
    if state is None:
        return "Arcade log: offline -- no archive."
    records = state.setdefault(RECORDS_KEY, {})
    mine = records.setdefault(user_id, {})
    entry = mine.setdefault("eliza", _blank_record())
    entry["plays"] += 1
    entry["eliza_sessions"] = entry.get("eliza_sessions", 0) + 1
    try:
        dyn.save_state(app, state)
    except Exception:
        pass
    n = entry["eliza_sessions"]
    return (f"ARCADE LOG: ELIZA -- {n} session{'s' if n != 1 else ''} "
            f"on file.")


def record_lander_result(app, user_id, landed, touchdown_velocity):
    """Log one finished LUNAR LANDER descent.

    Increments the per-user ``lander_landings`` counter on a safe landing
    and tracks ``lander_best_velocity`` (lowest touchdown speed) under
    RECORDS_KEY, mirroring the nightstation cis_dynamic pattern.
    """
    state, dyn = _score_store(app)
    if state is None:
        return "Arcade log: offline -- no archive."
    records = state.setdefault(RECORDS_KEY, {})
    mine = records.setdefault(user_id, {})
    entry = mine.setdefault("lander", _blank_record())
    entry["plays"] += 1
    if landed:
        entry["wins"] += 1
        entry["lander_landings"] = entry.get("lander_landings", 0) + 1
        prev = entry.get("lander_best_velocity")
        if prev is None or touchdown_velocity < prev:
            entry["lander_best_velocity"] = round(touchdown_velocity, 1)
    try:
        dyn.save_state(app, state)
    except Exception:
        pass
    landings = entry.get("lander_landings", 0)
    best = entry.get("lander_best_velocity")
    best_text = f"{best:.1f} ft/s" if best else "---"
    return (f"ARCADE LOG: LUNAR LANDER -- {landings} soft landing"
            f"{'s' if landings != 1 else ''}, best touchdown {best_text}.")


def arcade_records_lines(state, user_id):
    """Display lines for the coordinator's PLAYER RECORDS screen."""
    mine = (state or {}).get(RECORDS_KEY, {}).get(user_id, {})
    lines = []
    order = ("wumpus", "hamurabi", "startrek", "blackjack", "eliza", "lander")
    labels = {
        "wumpus": "WUMPUS",
        "hamurabi": "HAMURABI",
        "startrek": "STAR TREK",
        "blackjack": "BLACKJACK",
        "eliza": "ELIZA",
        "lander": "LANDER",
    }
    notes = {
        "wumpus": ("WINS", "wins", "best arrows left"),
        "hamurabi": ("REIGNS", "wins", "best score"),
        "startrek": ("VICTORIES", "wins", "best klingons down"),
        "blackjack": ("HANDS", "plays", "best chip stack"),
        "eliza": ("SESSIONS", "eliza_sessions", None),
        "lander": ("LANDINGS", "lander_landings", "softest touchdown ft/s"),
    }
    for key in order:
        entry = mine.get(key, _blank_record())
        tag, count_field, best_desc = notes[key]
        count = entry.get(count_field, 0)
        if key == "lander":
            # Lower touchdown velocity is better, so it gets its own key.
            best = entry.get("lander_best_velocity")
            best_text = f"{best:.1f} {best_desc}" if best else "---"
        elif best_desc is None:
            best_text = "---"
        else:
            best = entry.get("best", 0)
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
    app.ansi_scroll(wumpus_intro(), 0.01)
    app.ansi_scroll("", 0.01)
    while game.alive and not game.won:
        app.ansi_scroll(f"You are in room {game.player}. Tunnels to {', '.join(map(str, TUNNELS[game.player]))}.", 0.01)
        for warn in game.warnings():
            app.ansi_scroll(warn, 0.01)
        app.ansi_scroll(f"Arrows: {game.arrows}  Moves: {game.moves}", 0.01)
        try:
            raw = input("wumpus> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            raw = "Q"
        if not raw:
            continue
        parts = raw.split()
        verb = parts[0]
        if verb in ("Q", "QUIT", "M"):
            game.quit()
            app.ansi_scroll("You crawl out of the cave, empty-handed.", 0.01)
            break
        if verb == "H":
            app.ansi_scroll(wumpus_intro(), 0.01)
            continue
        if verb == "M" or verb == "MOVE":
            if len(parts) < 2 or not parts[1].isdigit():
                app.ansi_scroll("Move where? M <room number>", 0.01)
                continue
            result = game.move_to(int(parts[1]))
            if result == "NO_TUNNEL":
                app.ansi_scroll("No tunnel leads there from this room.", 0.01)
            elif result == "EATEN":
                app.ansi_scroll("...Oops! Bumped a WUMPUS!", 0.01)
            elif result == "PIT":
                app.ansi_scroll("YYYYIIIIEEEE... fell into a pit!", 0.01)
            elif result == "BATS":
                app.ansi_scroll("ZAP -- Super Bat snatch! They drop you in another room.", 0.01)
                app.ansi_scroll(f"You are in room {game.player}.", 0.01)
            elif result == "FLED":
                app.ansi_scroll("You startled the Wumpus -- it fled to another room!", 0.01)
            continue
        if verb in ("S", "SHOOT"):
            rooms = [p for p in parts[1:] if p.isdigit()]
            if not rooms:
                app.ansi_scroll("Shoot where? S <room> [<room> ...]  (up to 5 rooms)", 0.01)
                continue
            result = game.fire([int(r) for r in rooms])
            if result == "KILL":
                app.ansi_scroll("A-HA! You got the Wumpus!", 0.01)
            elif result == "SUICIDE":
                app.ansi_scroll("Ouch! Arrow got you!", 0.01)
            elif result == "MISS_MOVED":
                app.ansi_scroll("Missed. You woke the Wumpus -- it has moved!", 0.01)
            elif result == "MISS":
                app.ansi_scroll("Missed.", 0.01)
            elif result == "EATEN":
                app.ansi_scroll("The Wumpus fled into YOUR room. ...Oops!", 0.01)
            elif result == "NO_ARROWS":
                app.ansi_scroll("You are out of arrows!", 0.01)
            continue
        app.ansi_scroll("I don't understand. M <room>, S <rooms>, H, or Q.", 0.01)
    if game.won:
        app.ansi_scroll(f"WUMPUS SLAIN in {game.moves} moves with {game.arrows} arrows to spare!", 0.01)
    if not game._recorded:
        game._finish(game.won)
    app.ansi_scroll(game.record_line, 0.01)


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


def _ask_int(app, prompt, minimum=0):
    while True:
        try:
            raw = input(prompt).strip().upper()
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            return None
        if raw in ("Q", "QUIT", "M"):
            return None
        if raw.lstrip("-").isdigit():
            value = int(raw)
            if value >= minimum:
                return value
        app.ansi_scroll(f"Enter a whole number of {minimum} or more (or Q to quit).", 0.01)


def play_hamurabi(app, user_id):
    game = HamurabiGame(app=app, user_id=user_id)
    app.ansi_scroll(hamurabi_intro(), 0.01)
    app.ansi_scroll("", 0.01)
    while not game.over:
        app.ansi_scroll(f"--- YEAR {game.year + 1} of {HAMURABI_YEARS} ---", 0.01)
        app.ansi_scroll(f"Population: {game.population}  Grain: {game.grain} bushels  "
                        f"Land: {game.land} acres  Land price: {game.price} bushels/acre", 0.01)
        buy = _ask_int(app, "Acres to BUY [0]? ")
        if buy is None:
            app.ansi_scroll("You abdicate the throne.", 0.01)
            game._finish()
            return
        sell = 0
        if buy == 0:
            sell = _ask_int(app, "Acres to SELL [0]? ")
            if sell is None:
                app.ansi_scroll("You abdicate the throne.", 0.01)
                game._finish()
                return
        feed = _ask_int(app, "Bushels to FEED the people? ")
        if feed is None:
            app.ansi_scroll("You abdicate the throne.", 0.01)
            game._finish()
            return
        plant = _ask_int(app, "Acres to PLANT with seed? ")
        if plant is None:
            app.ansi_scroll("You abdicate the throne.", 0.01)
            game._finish()
            return
        report = game.play_year(buy=buy, sell=sell, feed=feed, plant=plant)
        if not report["ok"]:
            app.ansi_scroll(report["error"], 0.01)
            continue  # validation failed: the year was not resolved, try again
        app.ansi_scroll("", 0.01)
        if report["starved"]:
            app.ansi_scroll(f"{report['starved']} citizens starved.", 0.01)
        if report["plague"]:
            app.ansi_scroll("A horrible plague struck! Half the people died.", 0.01)
        app.ansi_scroll(f"Harvest: {report['yield']} bushels/acre, {report['harvest']} bushels gathered.", 0.01)
        if report["rats"]:
            app.ansi_scroll(f"Rats ate {report['rats']} bushels.", 0.01)
        app.ansi_scroll(f"{report['births']} children were born; {report['immigrants']} came to the city.", 0.01)
        app.ansi_scroll("", 0.01)
    app.ansi_scroll(f"--- END OF REIGN: year {game.year} ---", 0.01)
    app.ansi_scroll(f"Final population: {game.population}, grain: {game.grain}, land: {game.land}.", 0.01)
    app.ansi_scroll(f"Score: {game.final_score()} of 100.", 0.01)
    app.ansi_scroll(game.epitaph(), 0.01)
    if not game._recorded:
        game._finish()
    app.ansi_scroll(game.record_line, 0.01)


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
    app.ansi_scroll(trek_intro(), 0.01)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(f"{game.klingons_total} Klingons detected. Mission ends at stardate {game.deadline}.", 0.01)
    app.ansi_scroll("", 0.01)
    while not game.over:
        for line in game.status_lines():
            app.ansi_scroll(line, 0.01)
        try:
            raw = input("trek> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            raw = "XXX"
        if not raw:
            continue
        parts = raw.split()
        verb = parts[0]
        args = parts[1:]
        if verb == "XXX":
            app.ansi_scroll("You resign your command. The fleet mourns.", 0.01)
            game._finish()
            break
        if verb == "H":
            app.ansi_scroll(trek_intro(), 0.01)
            continue
        if verb == "SRS":
            for line in game.srs():
                app.ansi_scroll(line, 0.01)
            continue
        if verb == "LRS":
            for line in game.lrs():
                app.ansi_scroll(line, 0.01)
            continue
        if verb == "DAM":
            for line in game.damage_report():
                app.ansi_scroll(line, 0.01)
            continue
        if verb == "COM":
            app.ansi_scroll("STATUS REPORT:", 0.01)
            for line in game.status_lines():
                app.ansi_scroll("  " + line, 0.01)
            continue
        if verb == "NAV" and len(args) == 2 and all(a.isdigit() for a in args):
            for line in game.nav(int(args[0]), int(args[1])):
                app.ansi_scroll(line, 0.01)
            app.ansi_scroll("", 0.01)
            continue
        if verb == "PHA" and len(args) == 1 and args[0].isdigit():
            for line in game.phasers(int(args[0])):
                app.ansi_scroll(line, 0.01)
            app.ansi_scroll("", 0.01)
            continue
        if verb == "TOR" and len(args) == 2 and all(a.isdigit() for a in args):
            for line in game.torpedo(int(args[0]), int(args[1])):
                app.ansi_scroll(line, 0.01)
            app.ansi_scroll("", 0.01)
            continue
        if verb == "SHE" and len(args) == 1 and args[0].lstrip("+-").isdigit():
            for line in game.shields_cmd(int(args[0])):
                app.ansi_scroll(line, 0.01)
            continue
        app.ansi_scroll("Unknown command. Valid: NAV SRS LRS PHA TOR SHE DAM COM XXX  (H for help)", 0.01)
    if game.won:
        app.ansi_scroll(f"VICTORY at stardate {game.stardate}: {game.klingons_down()} Klingons destroyed.", 0.01)
    elif game.over:
        app.ansi_scroll("MISSION FAILED.", 0.01)
    if not game._recorded:
        game._finish()
    app.ansi_scroll(game.record_line, 0.01)


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
    app.ansi_scroll(blackjack_intro(), 0.01)
    app.ansi_scroll("", 0.01)
    while game.chips > 0:
        app.ansi_scroll(f"You hold {game.chips} chips.  (Hands: {game.hands}, won: {game.wins})", 0.01)
        try:
            raw = input("Bet how many chips (Q to quit)? ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            raw = "Q"
        if raw in ("Q", "QUIT", "M"):
            break
        if not raw.isdigit() or int(raw) <= 0:
            app.ansi_scroll("Enter a whole-number bet.", 0.01)
            continue
        bet = int(raw)
        if bet > game.chips:
            app.ansi_scroll(f"You hold only {game.chips} chips.", 0.01)
            continue
        player, dealer = game.deal()
        app.ansi_scroll(_show_hand("You", player), 0.01)
        app.ansi_scroll(_show_hand("Dealer", dealer, hide_hole=True), 0.01)
        doubled = False
        while True:
            total, _ = hand_value(player)
            if is_blackjack(player) or total > 21:
                break
            prompt = "H)it, S)tand" + (", D)ouble down" if len(player) == 2 and bet * 2 <= game.chips else "") + "? "
            try:
                choice = input(prompt).strip().upper()
            except (EOFError, KeyboardInterrupt):
                app.ansi_scroll("", 0.01)
                choice = "S"
            if choice == "H":
                player.append(game.shoe.pop())
                app.ansi_scroll(_show_hand("You", player), 0.01)
            elif choice == "D" and len(player) == 2 and bet * 2 <= game.chips:
                bet *= 2
                doubled = True
                player.append(game.shoe.pop())
                app.ansi_scroll(_show_hand("You", player) + "  (doubled)", 0.01)
                break
            elif choice in ("S", "Q", "M"):
                break
            else:
                app.ansi_scroll("H, S, or D.", 0.01)
        player_total, _ = hand_value(player)
        if player_total <= 21 and not is_blackjack(player):
            dealer = dealer_play(game.shoe, dealer)
        outcome, delta = settle(player, dealer, bet)
        game.chips += delta
        game.hands += 1
        if delta > 0:
            game.wins += 1
        game.best = max(game.best, game.chips)
        app.ansi_scroll(_show_hand("Dealer", dealer), 0.01)
        messages = {
            "blackjack": f"BLACKJACK! You win {delta} chips.",
            "win": f"You win {delta} chips{' (doubled)' if doubled else ''}.",
            "dealer_bust": f"Dealer busts! You win {delta} chips{' (doubled)' if doubled else ''}.",
            "push": "Push. Your bet is returned.",
            "bust": f"Bust! You lose {bet} chips.",
            "lose": f"Dealer wins. You lose {bet} chips.",
        }
        app.ansi_scroll(messages[outcome], 0.01)
        app.ansi_scroll("", 0.01)
        if game.chips <= 0:
            app.ansi_scroll("You are out of chips. The dealer wishes you better luck.", 0.01)
            break
    game.quit()
    app.ansi_scroll(f"Session over: {game.hands} hands, {game.wins} won, best stack {game.best}.", 0.01)
    if not game._recorded:
        game._finish_session()
    app.ansi_scroll(game.record_line, 0.01)


# ===========================================================================
# 5. ELIZA
# ===========================================================================
#
# The famous computer therapist, born at MIT in 1966 and a fixture of
# bulletin boards through the 1980s. The conversation engine lives in
# cis_eliza; this wrapper handles the BBS-style session around it.

ELIZA_INTRO = (
    "*** ELIZA ***",
    "The famous computer therapist -- born at MIT in 1966,",
    "a fixture of bulletin boards through the 1980s.",
    "Pour out your troubles one line at a time.",
    "Type BYE when you are finished.",
)

ELIZA_GOODBYE = "Goodbye. It has been a pleasure talking with you."


def play_eliza(app, user_id):
    """Chat with ELIZA via the cis_eliza engine. One session, then log it."""
    try:
        import cis_eliza
    except ImportError:
        app.ansi_scroll("ELIZA is resting -- the therapist module is not "
                        "installed.", 0.01)
        return
    app.ansi_scroll("", 0.01)
    for line in ELIZA_INTRO:
        app.ansi_scroll(line, 0.01)
    state = cis_eliza.new_state()
    try:
        while True:
            line = input("> ")
            if cis_eliza.is_quit(line):
                app.ansi_scroll("ELIZA: " + ELIZA_GOODBYE, 0.01)
                break
            reply, state = cis_eliza.respond(line, state)
            app.ansi_scroll("ELIZA: " + reply, 0.01)
    except (EOFError, KeyboardInterrupt):
        app.ansi_scroll("", 0.01)
        app.ansi_scroll("ELIZA: Our time is up for today. Goodbye.", 0.01)
    app.ansi_scroll(record_eliza_session(app, user_id), 0.01)


# ===========================================================================
# 6. LUNAR LANDER
# ===========================================================================
#
# A loving recreation of the 1970s BASIC classic. The LanderGame engine
# holds all physics state (altitude, velocity, fuel) and advances one turn
# per step() call, so the math is fully testable without I/O.

LANDER_GRAVITY = 5.0        # ft/s of downward velocity gained per turn
LANDER_THRUST = 0.25        # ft/s of braking per unit of fuel burned
LANDER_MAX_BURN = 40        # most fuel burnable in one turn
LANDER_SAFE_VELOCITY = 8.0  # touchdown at or below this speed is a landing

# key: (site name, starting altitude ft, starting descent velocity ft/s)
LANDER_SITES = {
    "1": ("MARE TRANQUILLITATIS", 1500.0, 25.0),
    "2": ("COPERNICUS CRATER", 1500.0, 30.0),
}

# key: (difficulty name, starting fuel)
LANDER_DIFFICULTY = {
    "1": ("CADET", 1200.0),
    "2": ("COMMANDER", 1050.0),
}


class LanderGame:
    """Scriptable LUNAR LANDER engine.

    Velocity is ft/s, positive downward. Each step() burns the requested
    fuel, applies gravity and thrust, and moves the module. Returns
    "flying", "landed", or "crashed".
    """

    def __init__(self, altitude=1500.0, velocity=25.0, fuel=1200.0):
        self.altitude = float(altitude)
        self.velocity = float(velocity)
        self.fuel = float(fuel)
        self.turn = 0
        self.landed = False
        self.crashed = False
        self.landing_velocity = None

    def step(self, burn):
        """Apply one turn of thrust. Returns 'flying', 'landed', 'crashed'."""
        if self.landed or self.crashed:
            return "landed" if self.landed else "crashed"
        burn = max(0.0, min(float(burn), LANDER_MAX_BURN, self.fuel))
        self.fuel -= burn
        new_velocity = self.velocity + LANDER_GRAVITY - burn * LANDER_THRUST
        self.altitude -= (self.velocity + new_velocity) / 2.0
        self.velocity = new_velocity
        self.turn += 1
        if self.altitude <= 0.0:
            self.altitude = 0.0
            self.landing_velocity = max(0.0, self.velocity)
            if self.landing_velocity <= LANDER_SAFE_VELOCITY:
                self.landed = True
                return "landed"
            self.crashed = True
            return "crashed"
        return "flying"

    def status_line(self):
        """One 1970s-teletype status line for the current turn."""
        if self.velocity >= 0:
            motion = f"DESCENDING {self.velocity:.0f} FT/S"
        else:
            motion = f"ASCENDING {-self.velocity:.0f} FT/S"
        return (f"T+{self.turn:04d}  ALT {self.altitude:5.0f} FT  "
                f"{motion}  FUEL {self.fuel:4.0f}")


def lander_grade(speed):
    """Flavor text for a safe touchdown, graded by softness."""
    if speed <= 3.0:
        return "FEATHER-SOFT TOUCHDOWN! Mission Control is applauding."
    if speed <= 6.0:
        return "A fine landing -- the Eagle has landed."
    return "A hard landing! You bent the gear, but you walked away."


def _lander_pick(app, prompt, options):
    """Prompt until the player picks a valid option key; None on abort."""
    valid = " OR ".join(sorted(options))
    while True:
        try:
            choice = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if choice in options:
            return choice
        app.ansi_scroll(f"?REDO -- PICK {valid}.", 0.01)


def _lander_read_burn(app):
    """Prompt for a burn rate; None on abort."""
    while True:
        try:
            raw = input(f"BURN RATE (0-{LANDER_MAX_BURN})? ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        try:
            burn = int(raw)
        except ValueError:
            app.ansi_scroll("?REDO -- ENTER A WHOLE NUMBER.", 0.01)
            continue
        if 0 <= burn <= LANDER_MAX_BURN:
            return burn
        app.ansi_scroll(f"?REDO -- 0 TO {LANDER_MAX_BURN}.", 0.01)


def play_lander(app, user_id):
    """Interactive LUNAR LANDER: pick site and difficulty, then fly her down."""
    app.ansi_scroll("", 0.01)
    for line in (
        "*** LUNAR LANDER ***",
        "A loving recreation of the 1970s BASIC classic.",
        "Your lunar module is on final approach. Each turn you",
        "choose a burn rate, and gravity does the rest.",
        f"GRAVITY: {LANDER_GRAVITY:.0f} FT/S PER TURN. EACH UNIT OF FUEL",
        f"BURNS OFF {LANDER_THRUST} FT/S. A BURN OF 20 HOVERS.",
        f"TOUCH DOWN AT {LANDER_SAFE_VELOCITY:.0f} FT/S OR LESS --",
        "OR MAKE A CRATER.",
    ):
        app.ansi_scroll(line, 0.01)
    difficulty = _lander_pick(
        app, "DIFFICULTY -- 1=CADET (FULL TANKS) 2=COMMANDER (TIGHT TANKS)? ",
        LANDER_DIFFICULTY)
    if difficulty is None:
        return
    site = _lander_pick(
        app, "LANDING SITE -- 1=MARE TRANQUILLITATIS 2=COPERNICUS CRATER? ",
        LANDER_SITES)
    if site is None:
        return
    diff_name, fuel = LANDER_DIFFICULTY[difficulty]
    site_name, altitude, velocity = LANDER_SITES[site]
    app.ansi_scroll(f"{diff_name} PILOT -- DESCENDING ON {site_name}.", 0.01)
    app.ansi_scroll("GOOD LUCK. THE CREW IS COUNTING ON YOU.", 0.01)
    game = LanderGame(altitude=altitude, velocity=velocity, fuel=fuel)
    try:
        while True:
            app.ansi_scroll(game.status_line(), 0.01)
            burn = _lander_read_burn(app)
            if burn is None:
                app.ansi_scroll("MISSION ABORTED -- THE MODULE DRIFTS ON.", 0.01)
                return
            if burn > game.fuel:
                app.ansi_scroll(f"ONLY {game.fuel:.0f} FUEL LEFT -- "
                                "BURNING IT ALL.", 0.01)
            outcome = game.step(burn)
            if outcome == "landed":
                speed = game.landing_velocity
                app.ansi_scroll(f"TOUCHDOWN AT {speed:.1f} FT/S!", 0.01)
                app.ansi_scroll(lander_grade(speed), 0.01)
                app.ansi_scroll(record_lander_result(app, user_id, True,
                                                     speed), 0.01)
                return
            if outcome == "crashed":
                speed = game.landing_velocity
                app.ansi_scroll(f"IMPACT AT {speed:.1f} FT/S -- "
                                "YOU MADE A NEW CRATER.", 0.01)
                app.ansi_scroll("THE CREW WILL BE REMEMBERED. "
                                "FLY SAFER NEXT TIME.", 0.01)
                app.ansi_scroll(record_lander_result(app, user_id, False,
                                                     speed), 0.01)
                return
    except (EOFError, KeyboardInterrupt):
        app.ansi_scroll("", 0.01)
        app.ansi_scroll("MISSION ABORTED -- THE MODULE DRIFTS ON.", 0.01)


# ===========================================================================
# Arcade submenu
# ===========================================================================

ARCADE_MENU = (
    ("1", "HUNT THE WUMPUS", "Stalk the beast through 20 rooms with 5 arrows."),
    ("2", "HAMURABI", "Rule Sumeria for 10 years: grain, land, and fate."),
    ("3", "SUPER STAR TREK", "Hunt Klingons across an 8x8-quadrant sector."),
    ("4", "BLACKJACK", "Beat the dealer with fictional arcade chips."),
    ("5", "ELIZA", "The 1966 computer therapist -- a BBS staple. Tell it your troubles."),
    ("6", "LUNAR LANDER", "1970s BASIC classic: burn fuel, mind gravity, land soft."),
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
        "5": play_eliza,
        "6": play_lander,
    }
    while True:
        for line in arcade_menu_text():
            app.ansi_scroll(line, 0.01)
        app.ansi_scroll("", 0.01)
        try:
            choice = input("arcade> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            app.ansi_scroll("", 0.01)
            choice = "M"
        if choice in ("M", "Q", "QUIT"):
            return
        if choice in handlers:
            app.ansi_scroll("", 0.01)
            handlers[choice](app, user_id)
            app.ansi_scroll("", 0.01)
            continue
        app.ansi_scroll("Pick 1-6, or M to return.", 0.01)
