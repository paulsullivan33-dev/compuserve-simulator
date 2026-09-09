"""Persistent cross-service story cases for the December 1988 simulation."""

CASE_ID = "CHIP-88"
TITLE = "The Vanishing Chip Shipment"
REQUIRED_CLUES = {"NEWS", "FORUM", "REFERENCE", "FINANCE"}


def _case(state, user_id):
    return state.setdefault("story_cases", {}).setdefault(user_id, {
        "id": CASE_ID,
        "status": "OPEN",
        "clues": [],
        "decision": None,
        "started": None,
    })


def _mail(app, subject, body, sender="CIS SPECIAL DESK"):
    messages = app.load_json("easyplex.json", default=[])
    messages.append({
        "id": max((item.get("id", 0) for item in messages), default=0) + 1,
        "from": sender,
        "to": app.current_user_id,
        "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"),
        "subject": subject,
        "body": body,
        "read": False,
    })
    app.save_json_atomic("easyplex.json", messages)


def ensure_case(app):
    """Open the case once for a logged-in member and seed other services."""
    if not app.current_user_id or app.cis_dynamic.simulation_day().day < 12:
        return False
    state = app.cis_dynamic.load_state(app)
    case = _case(state, app.current_user_id)
    if case["started"]:
        return False
    case["started"] = app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")
    app.cis_dynamic.save_state(app, state)
    _mail(
        app,
        "MEMBER RESEARCH REQUEST CHIP-88",
        "A Midwest computer club reports that a promised shipment of scarce memory "
        "chips vanished between distributor and dealer. Conflicting notices now appear "
        "in News, the IBM Hardware Forum, Reference, and MicroQuote.\n\n"
        "Enter GO CASE to review the evidence. This is a fictional December 1988 scenario.",
    )
    section = app.forum_threads.setdefault("ibmhw_hw", [])
    if not any(message.get("story_case") == CASE_ID for message in section):
        ids = [message.get("id", 0) for messages in app.forum_threads.values() for message in messages]
        section.append({
            "id": max(ids, default=1000) + 1,
            "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"),
            "author": "CHIPWATCH",
            "author_user_id": "SIMULATED",
            "subject": "DID ANYONE RECEIVE THE 256K DRAM SHIPMENT?",
            "body": "Three dealers advertised the same incoming lot. Ours now says allocation "
                    "was withdrawn, but the freight number appears valid. Compare the date codes "
                    "before accusing the dealer; gray-market and remarked parts are both possible.",
            "story_case": CASE_ID,
        })
        app.save_json_atomic("forums.json", app.forum_threads)
    app.cis_dynamic.record_activity(app, app.current_user_id, "CASE", "Special Desk opened investigation CHIP-88.")
    return True


def status_lines(app):
    if not app.current_user_id:
        return ["Sign in to begin a member investigation."]
    state = app.cis_dynamic.load_state(app)
    case = _case(state, app.current_user_id)
    clues = set(case["clues"])
    lines = [
        f"CASE {CASE_ID}: {TITLE.upper()}",
        f"STATUS {case['status']}  EVIDENCE {len(clues)}/{len(REQUIRED_CLUES)}",
    ]
    for source in ("NEWS", "FORUM", "REFERENCE", "FINANCE"):
        lines.append(f"[{('X' if source in clues else ' ')}] {source}")
    if case.get("decision"):
        lines.append(f"DECISION {case['decision']}")
    else:
        lines.append("Use GO CASE to examine sources and file your conclusion.")
    return lines


def _mark(app, source):
    state = app.cis_dynamic.load_state(app)
    case = _case(state, app.current_user_id)
    added = False
    if source not in case["clues"]:
        case["clues"].append(source)
        added = True
    app.cis_dynamic.save_state(app, state)
    if added:
        app.cis_dynamic.record_activity(app, app.current_user_id, "CASE", f"CHIP-88 evidence collected from {source}.")
    return case


def news_article(app):
    return {
        "category": "Business",
        "title": "MIDWEST MEMORY ALLOCATIONS TIGHTEN AS SHIPMENT IS DISPUTED",
        "published": app.cis_dynamic.simulation_day().strftime("December %d, 1988"),
        "source": "CIS Period Business Wire",
        "summary": "Dealers report abrupt changes to allocations of 256-kilobit dynamic RAM. "
                   "One disputed shipment appears on a freight manifest but not on the authorized "
                   "distributor's receiving ledger. Analysts warn that shortage rumors can move "
                   "component and computer-company quotations before facts are confirmed.",
    }


def source_lines(app, source):
    _mark(app, source)
    if source == "NEWS":
        article = news_article(app)
        return [article["title"], "", article["summary"], "", "CLUE: freight exists, but authorized receiving does not confirm it."]
    if source == "FORUM":
        return [
            "IBM HARDWARE FORUM DIGEST", "",
            "CHIPWATCH compared markings from two dealers. The disputed parts carry date code 8849,",
            "but the manufacturer bulletin says that package revision began in week 50.",
            "", "CLUE: the photographed date code predates the claimed package revision.",
        ]
    if source == "REFERENCE":
        return [
            "ELECTRONIC LIBRARY RECORD L4017 -- SEMICONDUCTOR MARKING PRACTICES", "",
            "Date codes normally identify year and production week. Package markings alone do not",
            "establish authorized distribution; remarked or qualification samples may circulate.",
            "", "CLUE: 8849 means 1988, week 49, and provenance requires more than a label.",
        ]
    return [
        "MICROQUOTE COMPONENT WATCH", "",
        "Fictional semiconductor quotations rose on shortage talk while affected computer makers",
        "were nearly unchanged. Volume increased before the dealer notice reached the Forum.",
        "", "CLUE: trading activity preceded the public shortage claim.",
    ]


def decide(app, decision):
    state = app.cis_dynamic.load_state(app)
    case = _case(state, app.current_user_id)
    if case.get("decision"):
        return f"Decision already filed: {case['decision']}."
    if len(set(case["clues"])) < 3:
        return "Collect evidence from at least three services before filing a decision."
    decision = decision.upper()
    outcomes = {
        "REPORT": ("REFERRED TO DISTRIBUTOR", "You sent the evidence privately to the authorized distributor. The suspect lot was held for inspection before members purchased it."),
        "PUBLISH": ("PUBLIC WARNING POSTED", "You posted a carefully qualified warning. Dealers supplied records, but shortage speculation briefly intensified."),
        "HOLD": ("EVIDENCE HELD", "You waited for confirmation. The distributor later isolated a paperwork error and a small group of remarked parts."),
    }
    if decision not in outcomes:
        return "Enter REPORT, PUBLISH, or HOLD."
    case["decision"] = decision
    case["status"], outcome = outcomes[decision]
    case["completed"] = app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.remember_member_for_user(app, app.current_user_id, "DiskDoctor", "CHIP-88 investigation", outcome)
    _mail(app, f"CHIP-88 CLOSED: {case['status']}", outcome + "\n\nYour evidence trail remains available under GO CASE.")
    app.cis_dynamic.record_activity(app, app.current_user_id, "CASE", f"CHIP-88 completed: {case['status']}.")
    return outcome


def service(app):
    if not app.current_user_id:
        app.text_page("support", "SPECIAL DESK", ["Sign in to begin a member investigation."])
        return
    if app.cis_dynamic.simulation_day().day < 12:
        app.text_page("support", "SPECIAL DESK", ["No member investigation is open yet in this December 1988 timeline."])
        return
    ensure_case(app)
    while True:
        app.clear()
        app.header_bar("support")
        for line in status_lines(app):
            app.ansi_scroll(line, 0.005)
        command = input("NEWS, FORUM, REFERENCE, FINANCE, DECIDE, or M ! ")
        command = command.strip().upper()
        if command in ("M", "QUIT"):
            return
        if command in REQUIRED_CLUES:
            app.text_page("support", f"CHIP-88 {command} EVIDENCE", source_lines(app, command))
        elif command == "DECIDE":
            choice = input("REPORT privately, PUBLISH warning, or HOLD evidence ! ").strip().upper()
            app.text_page("support", "CHIP-88 DECISION", [decide(app, choice)])
        else:
            app.ansi_scroll("Enter a source name, DECIDE, or M.", 0.01)
