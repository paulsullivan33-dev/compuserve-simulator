"""Persistent, period-style Online Adventure League."""

import random


CLASSES = {
    "SCOUT": (18, "SEARCH", "Finds extra supplies and avoids traps."),
    "ENGINEER": (22, "REPAIR", "Repairs machinery and restores health."),
    "COURIER": (20, "BARGAIN", "Earns extra gold from completed missions."),
}

QUESTS = {
    "RELAY": {"title": "THE SILENT RELAY", "foe": "SIGNAL WRAITH", "power": 7, "item": "COPPER KEY", "xp": 25, "gold": 18},
    "VAULT": {"title": "THE ARCHIVE VAULT", "foe": "TAPE GOLEM", "power": 10, "item": "ARCHIVE SEAL", "xp": 35, "gold": 25},
    "NODE": {"title": "THE MIDNIGHT NODE", "foe": "PACKET DRAGON", "power": 13, "item": "CRYSTAL MODEM", "xp": 50, "gold": 40},
}

WORLD_EVENTS = {
    0: "THE LONG NIGHT -- quest experience awards are doubled.",
    1: "MERCHANT CONVOY -- successful quests yield five extra gold.",
    2: "STATIC STORM -- enemies gain two power.",
}


def _user(app):
    return app.current_user_id or "GUEST"


def _characters(state):
    return state.setdefault("adventure_league", {})


def character(app):
    return _characters(app.cis_dynamic.load_state(app)).get(_user(app))


def create_character(app, name, character_class):
    character_class = character_class.upper()
    if character_class not in CLASSES:
        return "Choose SCOUT, ENGINEER, or COURIER."
    state = app.cis_dynamic.load_state(app); roster = _characters(state); user = _user(app)
    if user in roster:
        return "A League character already exists for this member."
    hp, ability, _ = CLASSES[character_class]
    roster[user] = {
        "name": (name.strip() or "WANDERER")[:20].upper(), "class": character_class,
        "level": 1, "xp": 0, "hp": hp, "max_hp": hp, "gold": 20,
        "inventory": ["TRAVEL RATION"], "completed": [], "campaign": 1,
        "guild": None, "party": [], "daily": {}, "journals": 0, "ability": ability,
    }
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.record_activity(app, app.current_user_id, "GAME", f"Joined Adventure League as {roster[user]['name']}, {character_class}.")
    return f"WELCOME, {roster[user]['name']} THE {character_class}."


def world_event(app):
    state = app.cis_dynamic.load_state(app)
    override = state.get("world_controls", {}).get("adventure")
    if override:
        return str(override).upper()
    return WORLD_EVENTS[app.cis_dynamic.simulation_day().day % 3]


def available_quests(app):
    hero = character(app)
    if not hero:
        return []
    count = min(3, hero.get("campaign", 1))
    return list(QUESTS)[:count]


def undertake(app, quest_id, approach):
    quest_id, approach = quest_id.upper(), approach.upper()
    state = app.cis_dynamic.load_state(app); hero = _characters(state).get(_user(app))
    if not hero:
        return "Create a character first."
    if quest_id not in available_quests(app):
        return "That quest is not yet available."
    day_key = app.cis_dynamic.simulation_day().isoformat()
    if hero.setdefault("daily", {}).get(day_key):
        return "Today's League quest is already complete. Return after the simulation date advances."
    quest = QUESTS[quest_id]; event = world_event(app)
    foe_power = quest["power"] + (2 if "STATIC STORM" in event else 0)
    bonuses = {"SEARCH": 3 if hero["class"] == "SCOUT" else 0, "REPAIR": 3 if hero["class"] == "ENGINEER" else 0, "BARGAIN": 3 if hero["class"] == "COURIER" else 0}
    tactic = bonuses.get(approach, 0)
    roll = random.Random(f'{_user(app)}:{day_key}:{quest_id}:{approach}').randint(4, 12) + hero["level"] + tactic
    if roll < foe_power:
        damage = max(1, foe_power - roll)
        hero["hp"] = max(1, hero["hp"] - damage)
        app.cis_dynamic.save_state(app, state)
        return f'{quest["foe"]} drives you back. You lose {damage} health; the daily quest remains open.'
    xp = quest["xp"] * (2 if "LONG NIGHT" in event else 1)
    gold = quest["gold"] + (5 if "MERCHANT CONVOY" in event else 0) + (5 if hero["class"] == "COURIER" else 0)
    hero["xp"] += xp; hero["gold"] += gold; hero["daily"][day_key] = quest_id
    if quest_id not in hero["completed"]:
        hero["completed"].append(quest_id)
        hero["inventory"].append(quest["item"])
    old_level = hero["level"]; hero["level"] = min(10, 1 + hero["xp"] // 75)
    hero["campaign"] = min(3, 1 + len(hero["completed"]))
    if approach == "REPAIR" and hero["class"] == "ENGINEER":
        hero["hp"] = hero["max_hp"]
    app.cis_dynamic.save_state(app, state)
    if hero["level"] > old_level:
        app.cis_dynamic.schedule_event(app, "mail", {"to": _user(app), "from": "ADVENTURE LEAGUE", "subject": f'LEVEL {hero["level"]} ATTAINED', "body": f'{hero["name"]} has advanced to level {hero["level"]}.'})
    app.cis_dynamic.record_activity(app, app.current_user_id, "GAME", f'Completed {quest["title"]}; earned {xp} XP.')
    return f'VICTORY OVER {quest["foe"]}: +{xp} XP, +{gold} GOLD, ITEM {quest["item"]}.'


def join_guild(app, name):
    state = app.cis_dynamic.load_state(app); hero = _characters(state).get(_user(app))
    if not hero:
        return "Create a character first."
    hero["guild"] = (name.strip() or "COMPUSERVE EXPLORERS")[:28].upper()
    app.cis_dynamic.save_state(app, state)
    return f'GUILD JOINED: {hero["guild"]}.'


def invite_party(app, handle):
    state = app.cis_dynamic.load_state(app); hero = _characters(state).get(_user(app))
    if not hero:
        return "Create a character first."
    handle = (handle.strip() or "BYTEBENDER")[:20]
    if handle.upper() not in {item.upper() for item in hero["party"]}:
        hero["party"].append(handle)
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "mail", {"to": _user(app), "from": handle, "subject": "ADVENTURE PARTY ACCEPTED", "body": f"I will join {hero['name']} on the next League expedition."})
    return f"PARTY INVITATION SENT TO {handle.upper()}."


def post_journal(app, text):
    state = app.cis_dynamic.load_state(app); hero = _characters(state).get(_user(app))
    if not hero:
        return "Create a character first."
    section = app.forum_threads.setdefault("gamers_general", [])
    ids = [item.get("id", 0) for messages in app.forum_threads.values() for item in messages]
    section.append({"id": max(ids, default=1000) + 1, "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"), "author": hero["name"], "author_user_id": _user(app), "subject": f'LEAGUE JOURNAL: CHAPTER {hero["campaign"]}', "body": text.strip()[:1200] or "The road continues.", "adventure_league": True})
    hero["journals"] += 1
    app.cis_dynamic.save_state(app, state); app.save_json_atomic("forums.json", app.forum_threads)
    return "Adventure journal posted to the Gamers Forum."


def profile_lines(app):
    hero = character(app)
    if not hero:
        return ["No Adventure League character.", "Choose C to create one."]
    return [
        f'{hero["name"]}  LEVEL {hero["level"]} {hero["class"]}',
        f'HEALTH {hero["hp"]}/{hero["max_hp"]}  XP {hero["xp"]}  GOLD {hero["gold"]}',
        f'ABILITY {hero["ability"]}  CAMPAIGN CHAPTER {hero["campaign"]}',
        f'GUILD {hero.get("guild") or "NONE"}', f'PARTY {", ".join(hero.get("party", [])) or "NONE"}',
        f'INVENTORY {", ".join(hero["inventory"])}', f'JOURNALS {hero.get("journals", 0)}',
        "", "WORLD EVENT", world_event(app), "", "AVAILABLE QUESTS",
        *[f'{key:<6} {QUESTS[key]["title"]}' for key in available_quests(app)],
    ]


def service(app):
    while True:
        app.text_page("games", "ONLINE ADVENTURE LEAGUE", profile_lines(app))
        action = input("C create, Q quest, G guild, P party, J journal, or M ! ").strip().upper()
        if action in ("M", "QUIT", ""):
            return
        if action == "C":
            app.ansi_scroll(create_character(app, input("Character name: "), input("Class [SCOUT/ENGINEER/COURIER]: ")), 0.01)
        elif action == "Q":
            app.ansi_scroll(undertake(app, input("Quest code: "), input("Approach [SEARCH/REPAIR/BARGAIN/FIGHT]: ")), 0.01)
        elif action == "G":
            app.ansi_scroll(join_guild(app, input("Guild name: ")), 0.01)
        elif action == "P":
            app.ansi_scroll(invite_party(app, input("Member handle: ")), 0.01)
        elif action == "J":
            app.ansi_scroll(post_journal(app, input("Journal entry: ")), 0.01)
        else:
            app.ansi_scroll("Enter C, Q, G, P, J, or M.", 0.01)
