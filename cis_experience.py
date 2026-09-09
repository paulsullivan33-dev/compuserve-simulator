"""Cross-service personal tools for the persistent 1988 simulation."""

from cis_web_files import offer_download

from pathlib import Path

def calendar_lines(app):
    state = app.cis_dynamic.load_state(app)
    user = app.current_user_id
    lines = ["PERSONAL SIMULATION CALENDAR", ""]
    for event in sorted((e for e in state.get("events", []) if not e.get("processed")), key=lambda e: (e.get("due_tick", 0), e.get("id", 0))):
        payload = event.get("payload", {})
        if payload.get("to") not in (None, user) and user not in str(payload.get("event_key", "")):
            continue
        label = {"mail": "EASYPLEX DELIVERY", "order_status": "STORE ORDER", "reservation_status": "TRAVEL UPDATE", "forum_reply": "FORUM REPLY"}.get(event.get("type"), event.get("type", "EVENT").upper())
        lines.append(f'{event.get("due_at", "")[:16]}  {label}  {payload.get("number") or payload.get("confirmation") or payload.get("subject", "")}'[:79])
    for reservation in state.get("reservations", []):
        if reservation.get("user_id") == user:
            lines.append(f'{reservation.get("travel_date", reservation.get("date", "")):<16}  TRIP {reservation.get("confirmation")} {reservation.get("origin")}-{reservation.get("destination")} [{reservation.get("status")}]')
    for item in state.get("classifieds", []):
        if item.get("seller") == user and item.get("status") == "ACTIVE":
            lines.append(f'{item.get("expires", ""):<16}  CLASSIFIED #{item.get("id")} EXPIRES')
    return lines if len(lines) > 2 else [*lines, "No dated personal items."]

def _notes(app, state=None):
    state = app.cis_dynamic.load_state(app) if state is None else state
    return state.setdefault("notebooks", {}).setdefault(app.current_user_id or "GUEST", [])

def add_note(app, title, body, source="MEMBER"):
    if not title.strip() or not body.strip():
        return "Title and note text are required."
    result = {}
    def update(state):
        notes = _notes(app, state); note_id = max((item.get("id", 0) for item in notes), default=0) + 1
        notes.append({"id": note_id, "title": title.strip()[:80], "body": body.strip()[:2000], "source": source[:30], "date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")}); result["id"] = note_id
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)
    return f"Notebook item #{result['id']} saved."

def notebook_lines(app):
    return [f'#{item["id"]} {item["title"]} [{item["source"]}] {item["date"]}' for item in _notes(app)] or ["Notebook is empty."]

def read_note(app, note_id):
    item = next((n for n in _notes(app) if n.get("id") == note_id), None)
    return [item["title"], f'SOURCE {item["source"]}  {item["date"]}', "", item["body"]] if item else ["Notebook item not found."]

def delete_note(app, note_id):
    removed = {"value": False}
    def update(state):
        notes = _notes(app, state); before = len(notes); notes[:] = [item for item in notes if item.get("id") != note_id]; removed["value"] = len(notes) < before
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)
    return "Notebook item deleted." if removed["value"] else "Notebook item not found."

def download_lines(app):
    folder = app.BASE_DIR / "downloads"
    if not folder.exists():
        return ["No downloaded files."]
    files = sorted((path for path in folder.iterdir() if path.is_file()), key=lambda p: p.name.lower())
    return [f"{index:>2} {path.name:<40} {path.stat().st_size:>8} BYTES" for index, path in enumerate(files, 1)] or ["No downloaded files."]

def achievement_lines(app):
    state = app.cis_dynamic.load_state(app); user = app.current_user_id
    activity = [a for a in state.get("activity", []) if a.get("user_id") == user]
    kinds = {a.get("kind") for a in activity}
    portfolio = state.get("stock_portfolios", {}).get(user, {})
    reservations = [r for r in state.get("reservations", []) if r.get("user_id") == user]
    equipment = state.get("owned_equipment", {}).get(user or "GUEST", [])
    tests = [
        ("EXPLORER", len(kinds) >= 5, "Use five different service families"),
        ("CORRESPONDENT", "FORUM" in kinds or "MAIL" in kinds, "Participate in member correspondence"),
        ("RESEARCHER", "REFERENCE" in kinds, "Prepare or use reference research"),
        ("MARKET PARTICIPANT", bool(portfolio.get("transactions")), "Record a fictional market trade"),
        ("TRAVELER", bool(reservations), "Build a fictional itinerary"),
        ("SHOPPER", "STORE" in kinds, "Place a fictional catalog order"),
        ("EQUIPMENT OWNER", bool(equipment), "Receive a fictional catalog product"),
        ("GAME PLAYER", any(k in kinds for k in ("GAME", "MEGAWARS", "ADVENTURE")), "Record a game achievement"),
    ]
    return [f"[{'X' if earned else ' '}] {name:<20} {description}" for name, earned, description in tests]

def session_cost_lines(app):
    seconds = app.get_elapsed_seconds()
    online = app.get_estimated_cost(seconds)
    minutes = max(1, int(seconds / 60 + .999))
    packet_saving = max(0.0, online - app.connection_rate_per_hour() / 60)
    return [f"BAUD RATE                 {app.connection_baud}", f"SESSION TIME              {app.format_elapsed(seconds)}", f"ESTIMATED CONNECT CHARGE  ${online:.2f}", f"PREMIUM SERVICE CHARGES   ${app.premium_charges:.2f}", f"MINUTES ONLINE            {minutes}", f"EST. SAVING IF FINAL REPORT READ OFFLINE  ${packet_saving:.2f}", "Telephone toll charges are not included."]

def request_representative(app, department, question):
    department = department.upper()
    agents = {"TRAVEL": ("Martha/Travel", "I reviewed your travel question. Check the Trip Folder, compare the displayed fare and hotel location, and verify every arrangement with the provider."), "FINANCE": ("Robert/Research", "I reviewed your business question. The company report, period wire, and economic indicators provide useful background; remember that all portfolio activity is fictional."), "STORE": ("Helen/Orders", "I reviewed your catalog question. Check compatibility, stock status, shipping, and the owner's report before sending the fictional order.")}
    if department not in agents or not question.strip():
        return "Choose TRAVEL, FINANCE, or STORE and enter a question."
    name, answer = agents[department]
    app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": name, "subject": f"RE: {department} SERVICE QUESTION", "body": f"Your question: {question[:500]}\n\n{answer}"})
    app.cis_dynamic.remember_member_for_user(app, app.current_user_id, name, department.lower(), question)
    return f"Question sent to {name}; an EasyPlex reply will follow."

def first_hint(app, key, message):
    fresh = {"value": False}
    def update(state):
        seen = state.setdefault("member_hints", {}).setdefault(app.current_user_id or "GUEST", [])
        if key not in seen: seen.append(key); fresh["value"] = True
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)
    if not fresh["value"]: return None
    return "HINT: " + message

def export_command_card(app):
    destination = app.BASE_DIR / "downloads" / "CIS_COMMAND_CARD.TXT"
    destination.parent.mkdir(exist_ok=True)
    lines = ["COMPUSERVE INFORMATION SERVICE", "MEMBER COMMAND CARD -- DECEMBER 1988 SIMULATION", "", *app.COMMAND_HELP_LINES, "", "SERVICE HELP", "HELP FINANCE / TRAVEL / STORE / REFERENCE / FORUMS / CB / GAMES", "COMMANDS displays actions for the current service."]
    destination.write_text("\n".join(lines) + "\n", encoding="ascii", errors="replace")
    offer_download(destination)
    return destination

