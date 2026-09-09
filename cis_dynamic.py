"""Deterministic, period-appropriate daily content for the 1988 simulation."""

import hashlib
import os
import random
import re
from datetime import date, datetime, time, timedelta


HANDLES = [
    "ByteBender", "NightOwl", "SilverFox", "ModemMan", "DataDave", "LadyLogic",
    "PacketPete", "DiskDoctor", "AmigaAce", "AppleAnnie", "AtariKid", "BASICBob",
    "BitBucket", "CodeRunner", "CommodoreCat", "CPMGuru", "DialTone", "DocHoliday",
    "EGAEd", "FloppyFran", "HamHank", "LaserLarry", "LotusLeaf", "MacMaven",
    "MegaMolly", "PascalPat", "PrintShop", "QWKReader", "SectorZero", "SharewareSam",
    "SysopSue", "UnixWiz", "VGAVal", "WordPro",
]
MEMBER_PROFILES = {
    "DiskDoctor": ("IBMHW", "disk controllers and diagnostics", "IBM PC AT"),
    "PacketPete": ("HAMNET", "packet radio and modems", "Heathkit terminal"),
    "LadyLogic": ("MACDEV", "Pascal and user interfaces", "Macintosh Plus"),
    "ByteBender": ("GAMERS", "adventure games", "Commodore 64"),
    "DataDave": ("IBMHW", "DOS memory and expansion cards", "IBM PC XT"),
    "AmigaAce": ("GAMERS", "Amiga graphics and sound", "Amiga 500"),
    "AppleAnnie": ("MACDEV", "desktop publishing", "Macintosh SE"),
    "AtariKid": ("GAMERS", "Atari games and MIDI", "Atari ST"),
    "BASICBob": ("IBMHW", "BASIC programming", "Tandy 1000"),
    "CodeRunner": ("MACDEV", "compilers and algorithms", "Macintosh II"),
    "DialTone": ("HAMNET", "telephone lines and modems", "IBM PC"),
    "EGAEd": ("IBMHW", "graphics adapters", "IBM PC AT"),
    "FloppyFran": ("IBMHW", "diskettes and backups", "Compaq Portable"),
    "HamHank": ("HAMNET", "amateur radio", "Heathkit H-89"),
    "LotusLeaf": ("IBMHW", "spreadsheets and business software", "IBM PC XT"),
    "MacMaven": ("MACDEV", "Macintosh system software", "Macintosh Plus"),
    "PascalPat": ("MACDEV", "Pascal programming", "Apple IIgs"),
    "SharewareSam": ("IBMHW", "shareware and utilities", "Zenith Z-248"),
    "UnixWiz": ("SCIENCE", "Unix and networking", "Sun workstation"),
    "VGAVal": ("IBMHW", "VGA hardware", "PS/2 Model 80"),
    "WordPro": ("IBMHW", "word processing", "IBM PC AT"),
}
FORUM_CASES = [
    {
        "keywords": ("irq", "serial", "com1", "com2", "mouse"),
        "sections": ("ibmhw",), "handle": "DiskDoctor", "topic": "serial-port interrupts",
        "library_number": 103,
        "reply": "That sounds like an interrupt assignment conflict. Check which adapter is using IRQ 3 and IRQ 4 before moving jumpers. Data Library 1 file #103, IRQSCAN.ARC, has a useful assignment report.",
    },
    {
        "keywords": ("memory", "config.sys", "640k", "expanded", "ems"),
        "sections": ("ibmhw",), "handle": "DataDave", "topic": "DOS memory",
        "library_number": 101,
        "reply": "List the drivers loaded by CONFIG.SYS and AUTOEXEC.BAT, then remove one at a time. Data Library 1 file #101, MEMTST.ARC, will help distinguish a configuration problem from faulty memory.",
    },
    {
        "keywords": ("modem", "hayes", "baud", "handshake", "carrier"),
        "sections": ("ibmhw", "hamnet"), "handle": "PacketPete", "topic": "modem setup",
        "library_number": 103,
        "reply": "Post the modem result code and initialization string. Also verify the serial adapter assignment; Data Library 1 file #103, IRQSCAN.ARC, may reveal a conflict before you change the modem setup.",
    },
]
CB_LINES = [
    "Anybody running a 2400-baud modem yet?", "My CONFIG.SYS finally leaves 580K free.",
    "The local store has DSDD diskettes on sale.", "Has anyone tried the new VGA boards?",
    "Uploading a Hayes command summary tonight.", "The long-distance rates drop after eleven.",
    "The IBMHW conference starts at nine Eastern.", "My XT hard disk sounds like a coffee grinder.",
    "Is WordPerfect 5.0 worth the upgrade?", "I finally solved that COM2 mouse conflict.",
    "Packet was open on twenty meters after sunset.", "Anybody using an AdLib board yet?",
    "The new 386 machines are still beyond my budget.", "I left a Pascal example in MACDEV.",
    "Remember to keep a bootable DOS disk nearby.", "The snow is making the phone lines noisy tonight.",
    "Who has a good source for DSDD diskettes?", "My 1541 drive is aligned again at last.",
    "The GAMERS Forum is trading adventure hints.", "Just downloaded IRQSCAN from Data Library 1.",
    "MultiFinder is useful if you can spare the memory.", "Does anyone have the latest shareware directory?",
    "The evening connect rate makes long downloads easier.", "My dot-matrix ribbon gave up halfway through a report.",
    "Anyone following the shuttle mission reports?", "The local club is trying packet radio this weekend.",
    "VGA looks sharp, but my older games prefer EGA.", "I am cleaning up AUTOEXEC.BAT before changing anything else.",
]
CB_CONVERSATIONS = {
    "1": [
        (("SilverFox", "Anybody staying for the evening conference?"), ("NightOwl", "I will, if the long-distance rate behaves.")),
        (("SharewareSam", "I posted a new utilities list in the library."), ("QWKReader", "Good. I will capture the descriptions before downloading.")),
        (("FloppyFran", "Backups are finished for once."), ("SectorZero", "That is always when the drive behaves perfectly.")),
    ],
    "2": [
        (("WordPro", "Is anyone printing holiday letters tonight?"), ("PrintShop", "Yes, and the ribbon is fading on page twelve.")),
        (("CommodoreCat", "The snow finally started here."), ("SilverFox", "Same here. My telephone line is already noisier.")),
        (("MegaMolly", "Who is up for a game after the conference?"), ("AtariKid", "Count me in if we avoid spoilers.")),
    ],
    "3": [
        (("VGAVal", "The new board works in text mode but one game rolls."), ("EGAEd", "Check its compatibility switch before changing the monitor.")),
        (("DialTone", "Carrier drops stopped when I shortened the serial cable."), ("PacketPete", "That is a useful clue. Marginal RS-232 wiring causes strange failures.")),
        (("BASICBob", "I found the loop that was eating all the memory."), ("CodeRunner", "Those are satisfying bugs once the numbers finally add up.")),
        (("UnixWiz", "The host requirements discussion is getting interesting."), ("CPMGuru", "Networking standards are moving faster than my hardware budget.")),
    ],
}
CB_TOPICS = {
    "modem": {"keywords": ("modem", "baud", "hayes", "carrier", "handshake", "atdt"), "handles": ("ModemMan", "PacketPete"), "responses": ("Check the result code first, then compare the initialization string with the manual.", "I would test at 1200 baud before blaming the telephone line.", "Make sure the modem and terminal agree on data bits, parity, and stop bits."), "followups": ("What result code appears after dialing?", "Does ATZ return OK?", "Is carrier detect following the modem or forced high?")},
    "memory": {"keywords": ("memory", "config.sys", "autoexec", "ems", "640k", "driver"), "handles": ("DataDave", "DiskDoctor"), "responses": ("Make one CONFIG.SYS change at a time and keep a bootable diskette ready.", "Resident programs can consume conventional memory surprisingly quickly.", "FILES and BUFFERS matter, but device drivers are usually the first place I look."), "followups": ("How much conventional memory remains after boot?", "Which drivers load before the failure?", "Are you using expanded memory or extended memory?")},
    "disk": {"keywords": ("disk", "drive", "mfm", "rll", "sector", "floppy"), "handles": ("DiskDoctor", "DataDave"), "responses": ("Back up anything important before running a surface test.", "Check the controller cables and termination before assuming the drive is bad.", "A repeated bad sector deserves attention even if DOS can mark it unusable."), "followups": ("Is the error repeatable after a cold boot?", "Which controller and drive type are installed?", "Do you have a current backup?")},
    "display": {"keywords": ("vga", "ega", "cga", "monitor", "video", "flicker"), "handles": ("LadyLogic", "DataDave"), "responses": ("Verify the monitor can accept the adapter timing before changing switches.", "Some older games behave better when the adapter is placed in a compatibility mode.", "Flicker at one resolution may point to refresh timing rather than bad display memory."), "followups": ("Does the problem occur in text mode too?", "Which resolution causes the trouble?", "Is the monitor intended for that adapter?")},
    "mac": {"keywords": ("mac", "macintosh", "multifinder", "pascal", "toolbox"), "handles": ("LadyLogic",), "responses": ("Under MultiFinder, leave more free memory than the application normally requests.", "The latest technical notes clarify several Toolbox calls.", "Test handles after a purgeable allocation; low-memory behavior can be deceptive."), "followups": ("Does it fail on a Plus, a II, or both?", "Which System version are you using?", "Can you reduce the application partition for a test?")},
    "radio": {"keywords": ("packet", "radio", "tnc", "ham", "propagation"), "handles": ("PacketPete",), "responses": ("Confirm the TNC serial rate separately from the over-the-air packet rate.", "Twenty meters has been opening shortly after sunset here.", "A short, known-good RS-232 cable eliminates many packet-station mysteries."), "followups": ("Which TNC and terminal program are you using?", "Are received packets clean even when transmit fails?", "What band and time did you try?")},
    "games": {"keywords": ("game", "score", "adventure", "megawars", "ultima"), "handles": ("ByteBender", "NightOwl"), "responses": ("The GAMERS Forum has a hint exchange, but put spoilers in the subject.", "I keep a separate save disk before trying anything dangerous.", "MegaWars traders are claiming the outer sectors pay better, if you survive the trip."), "followups": ("Which machine version are you playing?", "Are you looking for a hint or a complete solution?", "What is your best score so far?")},
    "software": {"keywords": ("wordperfect", "lotus", "software", "shareware", "program"), "handles": ("DataDave", "LadyLogic"), "responses": ("Check the Forum library for an update note before installing a new release.", "Shareware authors usually include registration details in the archive.", "Keep the old program directory until your documents open correctly in the new version."), "followups": ("Which version are you replacing?", "Does the problem affect a new document too?", "Have you checked the program's README file?")},
    "printer": {"keywords": ("printer", "ribbon", "laser", "dot matrix", "font"), "handles": ("DataDave", "LadyLogic"), "responses": ("Try the printer's self-test before changing the software driver.", "A fresh ribbon often fixes pale or uneven dot-matrix output.", "Downloadable fonts can consume more printer memory than expected."), "followups": ("Does the self-test print correctly?", "Which printer emulation is selected?", "Is the trouble limited to one application?")},
    "weather": {"keywords": ("weather", "snow", "storm", "rain", "cold"), "handles": ("SilverFox", "NightOwl"), "responses": ("The weather wire shows snow tonight; noisy local loops would not surprise me.", "Cold weather has made my connection less steady than usual.", "I would save the long download for after the storm passes."), "followups": ("Are you losing carrier or only seeing bad characters?", "What city are you calling from?", "Has the line improved since sunset?")},
    "shopping": {"keywords": ("buy", "price", "sale", "diskette", "classified"), "handles": ("SilverFox", "ByteBender"), "responses": ("Check the Electronic Classifieds, but ask about manuals and cables before agreeing.", "Local computer shows can be better for odd cables and used drives.", "New DSDD diskettes cost more, but questionable media is false economy."), "followups": ("Is the seller including the original manual?", "Can you test it before buying?", "Did you place a WANTED notice in the Classifieds?")},
    "news": {"keywords": ("news", "shuttle", "soviet", "market", "headline"), "handles": ("NightOwl", "SilverFox"), "responses": ("The period wire has a fresh December edition under GO NEWS.", "I have been following the shuttle reports and the East-West stories.", "The business wire is full of buyout financing and year-end trading."), "followups": ("Which section of the wire are you reading?", "Did you see the latest period dispatches?", "Are you following world news or the markets?")},
    "greeting": {"keywords": ("hello", "hi", "good evening", "anybody here"), "handles": ("SilverFox", "NightOwl", "ByteBender"), "responses": ("Good evening. What system are you calling from?", "Hello there. The channel has been busy since dinner.", "Welcome aboard. Mind the connect charges if you stay late."), "followups": ("What brings you onto CB tonight?", "Have you joined any Forums yet?", "Is your connection holding steady?")},
    "farewell": {"keywords": ("bye", "good night", "signing off", "later"), "handles": ("SilverFox", "NightOwl"), "responses": ("Good night. Watch those connect charges!", "See you next call.", "Take care, and remember to save your capture file."), "followups": ("Will you be at tomorrow's conference?", "Leave me an EasyPlex note if that fix works.", "Good luck with the system.")},
}
TRIVIA = [
    ("Which company introduced the IBM PC?", ("IBM", "INTERNATIONAL BUSINESS MACHINES"), "IBM"),
    ("What does DOS stand for?", ("DISK OPERATING SYSTEM",), "Disk Operating System"),
    ("Which key combination reboots an IBM PC compatible?", ("CTRL ALT DEL", "CONTROL ALT DELETE", "CTRL-ALT-DEL"), "Ctrl-Alt-Del"),
    ("What storage medium commonly holds 360 kilobytes?", ("FLOPPY", "FLOPPY DISK", "5.25 INCH FLOPPY", "DISKETTE"), "a 5.25-inch diskette"),
]


def simulation_day():
    configured = os.environ.get("CIS_SIMULATION_DATE")
    if configured:
        return datetime.strptime(configured, "%Y-%m-%d").date()
    # Vary by real day while remaining within the project's December 1988 setting.
    return date(1988, 12, 1 + date.today().toordinal() % 31)


def simulation_datetime():
    configured_time = os.environ.get("CIS_SIMULATION_TIME")
    clock = datetime.strptime(configured_time, "%H:%M").time() if configured_time else datetime.now().time().replace(second=0, microsecond=0)
    return datetime.combine(simulation_day(), clock)


def timeline_now(app, state=None):
    """Return monotonic simulated minutes while the visible calendar stays in 1988."""
    state = state if state is not None else load_state(app)
    clock = simulation_datetime().time()
    minute = clock.hour * 60 + clock.minute
    if state.get("simulation_date"):
        return int(state.setdefault("timeline_day", 0)) * 1440 + minute
    # Automatic mode follows real elapsed days, not the wrapping December label.
    return date.today().toordinal() * 1440 + minute


def load_state(app):
    state = app.load_json("dynamic_state.json", default={})
    state.setdefault("events", [])
    state.setdefault("next_event_id", 1)
    state.setdefault("scores", {})
    state.setdefault("classifieds", [])
    profiles = state.setdefault("member_profiles", {})
    for handle in HANDLES:
        values = MEMBER_PROFILES.get(handle, ("CB", "online conversation and file libraries", "home computer"))
        profiles.setdefault(handle, {"home_forum": values[0], "interests": values[1], "computer": values[2]})
    return state


def save_state(app, state):
    app.save_json_atomic("dynamic_state.json", state)


def apply_clock_state(app):
    state = app.load_json("dynamic_state.json", default={})
    if state.get("simulation_date"):
        os.environ["CIS_SIMULATION_DATE"] = state["simulation_date"]
    if state.get("simulation_time"):
        os.environ["CIS_SIMULATION_TIME"] = state["simulation_time"]
    for key, value in state.get("world_controls", {}).items():
        os.environ[f"CIS_{key.upper()}_ALERT"] = value


def schedule_event(app, event_type, payload, due_at=None):
    if due_at is None:
        delays = {
            "mail": timedelta(minutes=10),
            "forum_reply": timedelta(hours=2),
            "order_status": timedelta(days=1),
        }
        due_at = simulation_datetime() + delays.get(event_type, timedelta(minutes=10))
    display_now = simulation_datetime()
    delay_minutes = max(0, int((due_at - display_now).total_seconds() // 60))
    result = {}
    def append_event(state):
        state.setdefault("events", []); state.setdefault("next_event_id", 1)
        event = {"id": state["next_event_id"], "type": event_type, "due_at": due_at.isoformat(timespec="minutes"), "due_tick": timeline_now(app, state) + delay_minutes, "payload": payload, "processed": False}
        state["next_event_id"] += 1; state["events"].append(event); result["id"] = event["id"]
    if hasattr(app, "update_json_atomic"):
        app.update_json_atomic("dynamic_state.json", {}, append_event)
    else:
        state = load_state(app); append_event(state); save_state(app, state)
    return result["id"]


def _deliver_mail(app, payload):
    messages = app.load_json("easyplex.json", default=[])
    messages.append({"id": max((m.get("id", 0) for m in messages), default=0) + 1, "from": payload.get("from", "COMPUSERVE"), "to": payload["to"], "date": simulation_day().strftime("%m/%d/%y"), "subject": payload["subject"][:120], "body": payload["body"][:5000], "read": False})
    app.save_json_atomic("easyplex.json", messages)


def _forum_reply(app, payload):
    threads = app.forum_threads.get(payload["section"], [])
    target = next((m for m in threads if m.get("id") == payload["message_id"]), None)
    if not target:
        return
    ids = [m.get("id", 0) for group in app.forum_threads.values() for m in group]
    reply_id = max(ids, default=1000) + 1
    threads.append({"id": reply_id, "parent_id": target["id"], "date": simulation_day().strftime("%m/%d/%y"), "author": payload["author"], "author_user_id": "SIMULATED", "subject": "RE: " + target.get("subject", ""), "body": payload["body"]})
    app.save_json_atomic("forums.json", app.forum_threads)
    recipient = payload.get("to") or target.get("author_user_id")
    if recipient and recipient != "SIMULATED":
        _deliver_mail(app, {
            "to": recipient, "from": "FORUMS",
            "subject": f'REPLY TO MESSAGE #{target["id"]}',
            "body": f'{payload["author"]} posted message #{reply_id} in reply to your Forum message.\n\n{payload["body"]}',
        })
        record_activity(app, recipient, "FORUM", f'{payload["author"]} replied to message #{target["id"]}.', {"message_id": reply_id, "library_number": payload.get("library_number")})
        remember_member_for_user(app, recipient, payload["author"], target.get("subject", "forum discussion"), payload["body"], **({"library_number": payload["library_number"]} if payload.get("library_number") else {}))
        state = load_state(app)
        for case in state.get("forum_cases", {}).values():
            if case.get("message_id") == target["id"] and case.get("handle") == payload["author"]:
                case.update({"status": "ANSWERED", "reply_id": reply_id, "answered": simulation_datetime().isoformat(timespec="minutes")})
        save_state(app, state)


def process_events(app):
    state = load_state(app)
    now = simulation_datetime()
    current_tick = timeline_now(app, state)
    due = [event for event in state["events"] if not event.get("processed") and (event.get("due_tick", current_tick + 1) <= current_tick if "due_tick" in event else datetime.fromisoformat(event["due_at"]) <= now)]
    if not due:
        return False
    for event in due:
        event["processed"] = True
    # Commit queue state first. Event handlers may write relationship or
    # activity records and must not have those changes overwritten afterward.
    save_state(app, state)
    for event in due:
        if event["type"] == "mail":
            _deliver_mail(app, event["payload"])
        elif event["type"] == "forum_reply":
            _forum_reply(app, event["payload"])
        elif event["type"] == "order_status":
            orders = app.load_json("orders.json", default=[])
            changed = False
            changed_order = None
            for order in orders:
                if order.get("event_key") == event["payload"]["event_key"]:
                    order["status"] = event["payload"]["status"]
                    changed = True
                    changed_order = order
            app.save_json_atomic("orders.json", orders)
            if changed and event["payload"].get("to"):
                status = event["payload"]["status"]
                number = event["payload"].get("number", "CATALOG ORDER")
                wording = "has left our fictional fulfillment desk" if status == "SHIPPED" else "is awaiting replenishment" if status == "BACK ORDER" else "is being prepared"
                if status == "DELIVERED":
                    wording = "has been delivered and added to GO EQUIPMENT"
                _deliver_mail(app, {"to": event["payload"]["to"], "from": "COMP-U-STORE", "subject": f"ORDER {number} - {status}", "body": f"Your Comp-U-Store order {number} {wording}. Check GO PROFILE for current status."})
                record_activity(app, event["payload"]["to"], "STORE", f"Order {number} changed to {status}.")
                if status == "DELIVERED" and changed_order is not None and hasattr(app, "cis_ownership"):
                    app.cis_ownership.receive_order(app, changed_order)
        elif event["type"] == "reservation_status":
            latest = load_state(app)
            reservation = next((item for item in latest.get("reservations", []) if item.get("confirmation") == event["payload"].get("confirmation")), None)
            if reservation and reservation.get("status") != "CANCELLED":
                if ("WEATHER" in reservation.get("status", "") or reservation.get("weather_resolution")) and event["payload"].get("status") == "TICKETED":
                    continue
                reservation["status"] = event["payload"]["status"]
                save_state(app, latest)
                _deliver_mail(app, {"to": reservation["user_id"], "from": "TRAVEL", "subject": f'{reservation["confirmation"]} {reservation["status"]}', "body": f'Your fictional travel item is now {reservation["status"]}. Review your Trip Folder and verify all details with the provider.'})
                record_activity(app, reservation["user_id"], "TRAVEL", f'{reservation["confirmation"]} changed to {reservation["status"]}.')
    return True


def rng(service, user_id=""):
    key = f"{simulation_day().isoformat()}:{service}:{user_id}".encode()
    seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed)


def announcements(user_id, mail_count=0, app=None):
    choices = [
        "IBMHW conference: memory expansion boards at 9 PM Eastern.",
        "New in Data Library 1: hard-disk diagnostic notes.",
        "GAMERS high-score exchange remains open through Sunday.",
        "Reduced connect rates apply during evening hours.",
        "Please download large files after 11 PM local time.",
    ]
    selected = rng("announcements", user_id).sample(choices, 2)
    state = load_state(app) if app is not None else {}
    sysop_lines = state.get("system_announcements", [])[-2:]
    if app is not None:
        sysop_lines.extend(f'*** {item.get("priority", "NORMAL")} *** {item.get("title")}' for item in app.cis_announcements.active(app, user_id)[:2])
    member_lines = []
    if app is not None:
        activity = [item for item in state.get("activity", []) if item.get("user_id") == user_id]
        pending = [event for event in state.get("events", []) if not event.get("processed") and event.get("payload", {}).get("to") == user_id]
        if activity:
            member_lines.append("SINCE YOUR LAST CALL: " + activity[-1].get("summary", "Member activity recorded."))
        if pending:
            member_lines.append(f"PENDING FOLLOW-UPS: {len(pending)}")
    return [f"DATE {simulation_datetime().strftime('%m/%d/%y  %I:%M %p')}", f"EASYPLEX: {mail_count} message(s) waiting", *member_lines, *sysop_lines, *selected]


def market_quotes(base_quotes):
    result = {}
    randomizer = rng("market")
    sector_biases = {"IBM": .35, "AAPL": .35, "DEC": .35, "MSFT": .35, "INTC": -.20, "MOT": -.20, "T": .15, "S": .10, "GM": -.10, "F": -.10, "BA": .05, "KO": .05}
    closed = simulation_day().weekday() >= 5
    for symbol, quote in sorted(base_quotes.items()):
        change = 0.0 if closed else round(randomizer.uniform(-1.25, 1.25) + sector_biases.get(symbol, 0), 2)
        result[symbol] = {"last": round(max(1, quote["last"] + change), 2), "change": change}
    return result


def market_report(base_quotes):
    quotes = market_quotes(base_quotes)
    average = sum(item["change"] for item in quotes.values()) / max(1, len(quotes))
    djia_change = round(average * 9.4, 2)
    volume = rng("volume").randrange(1120, 1690) * 100_000
    tone = "Computer and industrial issues led the advance." if djia_change >= 0 else "Profit taking weighed on industrial and computer shares."
    catalyst = "Period wire: personal-computer demand and year-end retail activity influence sector sentiment."
    if simulation_day().weekday() >= 5:
        tone = "U.S. exchanges closed for the weekend; previous simulated closes shown."
    alert = os.environ.get("CIS_MARKET_ALERT")
    return [f"DJIA  {2168.57 + djia_change:.2f}  {djia_change:+.2f}", f"NYSE volume {volume:,} shares", tone, catalyst, *(["SYSOP MARKET BULLETIN: " + alert] if alert else []), "Figures are fictional December 1988 simulation data."]


def classifieds(base_items):
    extras = [
        "FOR SALE: Hayes-compatible 1200 baud modem, manuals included. USER 72345,1122",
        "WANTED: 384K memory expansion for IBM PC AT. USER 73456,0091",
        "FOR SALE: Commodore 1541 disk drive, good condition. USER 74567,3310",
        "TRADE: WordPerfect 5.0 manuals for Lotus 1-2-3 books. USER 71220,8841",
        "WANTED: Used RGB monitor suitable for EGA. USER 70118,4402",
    ]
    return list(base_items) + rng("classifieds").sample(extras, 3)


def cb_presence(channel):
    randomizer = rng(f"cb-{channel}")
    return randomizer.sample(HANDLES, randomizer.randint(7, 12))


def cb_line(channel, counter):
    randomizer = rng(f"cb-{channel}-{counter}")
    return randomizer.choice(HANDLES), randomizer.choice(CB_LINES)


def cb_ambient_events(channel, bucket, recent_text=(), hour=None):
    """Return a quiet-to-busy, deterministic batch of period CB activity."""
    channel = str(channel).upper()
    hour = simulation_datetime().hour if hour is None else int(hour) % 24
    randomizer = rng(f"cb-ambient-{channel}-{bucket}-{hour}")
    chance = 0.20 if 1 <= hour < 7 else 0.45 if 7 <= hour < 17 else 0.80
    if randomizer.random() > chance:
        return []
    recent = " ".join(str(item).casefold() for item in recent_text[-30:])
    conversations = CB_CONVERSATIONS.get(channel, CB_CONVERSATIONS["1"])
    available = [conversation for conversation in conversations if not any(line.casefold() in recent for _, line in conversation)]
    if not available:
        return []
    conversation = randomizer.choice(available)
    events = list(conversation if randomizer.random() < (0.75 if 17 <= hour <= 23 else 0.45) else conversation[:1])
    if randomizer.random() < 0.18:
        mover = randomizer.choice([handle for handle in HANDLES if handle not in {sender for sender, _ in events}])
        destination = randomizer.choice([key for key in ("1", "2", "3") if key != channel] or ["1"])
        events.append(("SYSTEM", f"*** {mover} left for channel {destination} ***"))
    return events


def cb_member_info(app, handle):
    match = next((item for item in HANDLES if item.casefold() == handle.strip().casefold()), None)
    if not match:
        return None
    state = load_state(app)
    profile = state["member_profiles"][match]
    memory = state.get("member_memory", {}).get(app.current_user_id or "GUEST", {}).get(match, {})
    relationship = relationship_summary(memory)
    return [
        f"HANDLE: {match} [SIMULATED MEMBER]",
        f'HOME FORUM: {profile["home_forum"]}',
        f'COMPUTER: {profile["computer"]}',
        f'INTERESTS: {profile["interests"]}',
        f'YOUR EXCHANGES: {memory.get("interactions", 0)}',
        f'RELATIONSHIP: {relationship["level"]}  TRUST {relationship["trust"]}  FRICTION {relationship["friction"]}',
        f'RECENT TOPIC: {memory.get("topic", "None recorded")}',
        f'OPEN FAVOR: {memory.get("favor", "None")}',
    ]


def daily_trivia(user_id):
    return rng("trivia", user_id).choice(TRIVIA)


def record_trivia_result(app, user_id, correct):
    state = load_state(app)
    score = state["scores"].setdefault(user_id, {"correct": 0, "attempts": 0})
    score["attempts"] += 1
    score["correct"] += int(correct)
    save_state(app, state)
    return dict(score)


def relationship_summary(memory):
    interactions = int(memory.get("interactions", 0))
    trust = int(memory.get("trust", max(0, interactions // 2)))
    friction = int(memory.get("friction", 0))
    if friction >= 3 and friction > trust:
        level = "RIVAL"
    elif trust >= 9:
        level = "CONFIDANT"
    elif trust >= 5:
        level = "TRUSTED"
    elif interactions >= 3:
        level = "REGULAR"
    elif interactions:
        level = "ACQUAINTED"
    else:
        level = "UNFAMILIAR"
    return {"level": level, "trust": trust, "friction": friction, "interactions": interactions}


def relationship_lines(app):
    memories = load_state(app).get("member_memory", {}).get(app.current_user_id or "GUEST", {})
    lines = ["MY SIMULATED-MEMBER RELATIONSHIPS", ""]
    for handle, memory in sorted(memories.items(), key=lambda item: (-relationship_summary(item[1])["trust"], item[0].casefold())):
        summary = relationship_summary(memory)
        lines.append(f'{handle:<16} {summary["level"]:<11} TRUST {summary["trust"]:<2} EXCHANGES {summary["interactions"]:<3}')
        lines.append(f'  LAST: {memory.get("topic", "general correspondence")}' + (f'  FAVOR: {memory["favor"]}' if memory.get("favor") else ""))
    return lines if memories else [*lines, "No recurring correspondents yet. Visit Forums or CB."]


def remember_member_for_user(app, user_id, handle, topic, note, **details):
    state = load_state(app)
    user_memory = state.setdefault("member_memory", {}).setdefault(user_id or "GUEST", {})
    memory = user_memory.setdefault(handle, {"interactions": 0})
    previous = relationship_summary(memory)
    memory.update({"topic": topic[:80], "note": note[:200], "last_date": simulation_day().isoformat()})
    memory.update(details)
    memory["interactions"] += 1
    hostile = any(word in note.casefold().split() for word in ("wrong", "nonsense", "idiot", "stupid"))
    if hostile:
        memory["friction"] = memory.get("friction", 0) + 1
    else:
        memory["trust"] = memory.get("trust", max(0, previous["interactions"] // 2)) + (1 if memory["interactions"] % 2 == 0 else 0)
    if memory["interactions"] >= 6 and not memory.get("favor"):
        memory["favor"] = f"Follow up on {topic[:50]}"
    save_state(app, state)
    current = relationship_summary(memory)
    if user_id and user_id != "GUEST" and current["level"] != previous["level"] and current["level"] in ("REGULAR", "TRUSTED", "CONFIDANT"):
        schedule_event(app, "mail", {
            "to": user_id, "from": handle, "subject": f"GOOD TO HEAR FROM YOU - {current['level']}",
            "body": f"We have exchanged {memory['interactions']} messages now. I remember our recent topic: {topic}. "
                    "Look for me in my usual Forum or CB channel.",
        })
    return memory


def remember_member(app, handle, topic, note):
    return remember_member_for_user(app, app.current_user_id or "GUEST", handle, topic, note)


def begin_forum_case(app, section, message_id, subject, body):
    if not app.current_user_id:
        return None
    text = f"{subject} {body}".lower()
    case = next((item for item in FORUM_CASES if section.startswith(item["sections"]) and any(word in text for word in item["keywords"])), None)
    if not case:
        return None
    state = load_state(app)
    case_key = f'{app.current_user_id}:{message_id}'
    if case_key in state.setdefault("forum_cases", {}):
        return None
    state["forum_cases"][case_key] = {"status": "AWAITING REPLY", "handle": case["handle"], "topic": case["topic"], "message_id": message_id, "library_number": case["library_number"]}
    save_state(app, state)
    remember_member_for_user(app, app.current_user_id, case["handle"], case["topic"], subject, library_number=case["library_number"], forum_message=message_id)
    schedule_event(app, "forum_reply", {"section": section, "message_id": message_id, "author": case["handle"], "body": case["reply"], "to": app.current_user_id, "library_number": case["library_number"]}, simulation_datetime() + timedelta(hours=2))
    return case["handle"]


def cb_response(channel, message, counter=0, app=None):
    lowered = message.lower()
    words = set(re.findall(r"[a-z0-9]+", lowered))

    def mentions(keywords):
        return any((" " in keyword and keyword in lowered) or (" " not in keyword and keyword in words) for keyword in keywords)

    def choose(topic_key, topic, handle=None):
        randomizer = rng(f"cb-response-{topic_key}-{channel}-{counter}", app.current_user_id if app is not None else "")
        selected_handle = handle or randomizer.choice(topic["handles"])
        prior = {}
        if app is not None:
            prior = load_state(app).get("member_memory", {}).get(app.current_user_id or "GUEST", {}).get(selected_handle, {})
        choices = [item for item in topic["responses"] if item != prior.get("last_response")] or list(topic["responses"])
        response = randomizer.choice(choices)
        relationship = relationship_summary(prior)
        if relationship["level"] in ("TRUSTED", "CONFIDANT"):
            response = f"Good to catch you again. {response}"
        elif relationship["level"] == "RIVAL":
            response = f"We have disagreed before, but here is what I see. {response}"
        details = []
        systems = [("386", "386"), ("286", "286"), ("xt", "XT"), ("amiga", "Amiga"), ("mac", "Macintosh"), ("c64", "Commodore 64")]
        mentioned_system = next((label for token, label in systems if token in words), None)
        if mentioned_system and mentioned_system.lower() not in response.lower():
            details.append(f"On a {mentioned_system}, I would write down the present settings first.")
        if "?" in message and topic_key not in ("greeting", "farewell"):
            details.append(randomizer.choice(topic["followups"]))
        response = " ".join([response, *details])
        if app is not None:
            remember_member_for_user(app, app.current_user_id or "GUEST", selected_handle, topic_key, message, topic_key=topic_key, last_response=response)
        return selected_handle, response

    addressed = next((handle for handle in HANDLES if handle.casefold() in lowered), None)
    if app is not None:
        memories = load_state(app).get("member_memory", {}).get(app.current_user_id or "GUEST", {})
        if memories and not addressed and mentions(("hello", "hi", "follow up", "remember", "worked")):
            handle, memory = max(memories.items(), key=lambda item: item[1].get("interactions", 0))
            library = f' Did you get file #{memory["library_number"]} from the Data Library?' if memory.get("library_number") else ""
            remember_member_for_user(app, app.current_user_id or "GUEST", handle, memory.get("topic", "our last exchange"), message, **({"library_number": memory["library_number"]} if memory.get("library_number") else {}))
            return handle, f'Good to see you again, {app.current_handle or app.current_user_id}.{library}'
    if app is not None:
        memories = load_state(app).get("member_memory", {}).get(app.current_user_id or "GUEST", {})
        contextual = [(handle, memory) for handle, memory in memories.items() if memory.get("topic_key") and (not addressed or handle == addressed) and mentions(("why", "how", "what", "which", "still", "tried that"))]
        if contextual:
            handle, memory = contextual[-1]
            topic = CB_TOPICS.get(memory["topic_key"])
            if topic:
                response = rng(f"cb-followup-{channel}-{counter}", app.current_user_id).choice(topic["followups"])
                acknowledgement = "I remember the earlier details. " if memory.get("interactions", 0) > 1 else ""
                remember_member_for_user(app, app.current_user_id, handle, memory.get("topic", memory["topic_key"]), message, topic_key=memory["topic_key"], last_response=response)
                return handle, acknowledgement + response
    for topic_key, topic in CB_TOPICS.items():
        if mentions(topic["keywords"]):
            return choose(topic_key, topic, addressed if addressed in topic["handles"] else None)
    if addressed or "?" in message:
        handle = addressed or rng(f"cb-general-{channel}-{counter}", app.current_user_id if app is not None else "").choice(HANDLES)
        profile = MEMBER_PROFILES.get(handle, ("CB", "online services", "home computer"))
        response = f"I do not have a firm answer yet. I use a {profile[2]} and follow {profile[1]}; can you give one more detail?"
        if app is not None:
            remember_member_for_user(app, app.current_user_id or "GUEST", handle, "general question", message, last_response=response)
        return handle, response
    return None


def active_classifieds(app, base_items):
    state = load_state(app)
    today = simulation_day()
    if not state["classifieds"]:
        for index, text in enumerate(classifieds(base_items)):
            state["classifieds"].append({"id": index + 1, "text": text, "seller": text.rsplit("USER ", 1)[-1] if "USER " in text else "COMPUSERVE", "posted": today.isoformat(), "expires": (today + timedelta(days=14 + index * 3)).isoformat(), "status": "ACTIVE", "category": "GENERAL", "generated": True})
        state["next_classified_id"] = len(state["classifieds"]) + 1
    if state.get("classified_day") != today.isoformat():
        state["classified_day"] = today.isoformat()
    # Records written by schema 4/5 predate classified IDs and seller metadata.
    # Upgrade them in place so an existing compuserve.db remains usable.
    used_ids = {item.get("id") for item in state["classifieds"] if isinstance(item.get("id"), int)}
    next_id = max(used_ids, default=0) + 1
    for item in state["classifieds"]:
        if not isinstance(item.get("id"), int):
            while next_id in used_ids:
                next_id += 1
            item["id"] = next_id
            used_ids.add(next_id)
            next_id += 1
        text = item.get("text", "")
        item.setdefault("seller", text.rsplit("USER ", 1)[-1] if "USER " in text else "COMPUSERVE")
        item.setdefault("posted", today.isoformat())
        item.setdefault("expires", (today + timedelta(days=21)).isoformat())
        item.setdefault("status", "ACTIVE")
        item.setdefault("category", "GENERAL")
    state["next_classified_id"] = max(used_ids, default=0) + 1
    for item in state["classifieds"]:
        if date.fromisoformat(item["expires"]) < today and item["status"] == "ACTIVE":
            item["status"] = "EXPIRED"
    save_state(app, state)
    return [f'#{item["id"]} [{item.get("category", "GENERAL")}] {item["text"]}' for item in state["classifieds"] if item["status"] == "ACTIVE"]


def post_classified(app, text, category="GENERAL"):
    state = load_state(app)
    item_id = state.setdefault("next_classified_id", max((i.get("id", 0) for i in state["classifieds"]), default=0) + 1)
    state["next_classified_id"] = item_id + 1
    allowed = {"COMPUTERS", "MODEMS", "SOFTWARE", "PERIPHERALS", "BOOKS", "WANTED", "GENERAL"}
    category = category.upper() if category.upper() in allowed else "GENERAL"
    state["classifieds"].append({"id": item_id, "category": category, "text": text[:240], "seller": app.current_user_id, "posted": simulation_day().isoformat(), "expires": (simulation_day() + timedelta(days=21)).isoformat(), "status": "ACTIVE"})
    save_state(app, state)
    record_activity(app, app.current_user_id, "CLASSIFIED", f"Advertisement #{item_id} posted in {category}.")
    return item_id


def member_classifieds(app):
    state = load_state(app)
    return [f'#{item["id"]} [{item.get("status", "ACTIVE")}] [{item.get("category", "GENERAL")}] {item["text"]}' for item in state["classifieds"] if item.get("seller") == app.current_user_id] or ["No advertisements posted by this member."]


def classified_action(app, item_id, action, message=""):
    state = load_state(app)
    item = next((i for i in state["classifieds"] if i.get("id") == item_id), None)
    if not item:
        return "Advertisement not found."
    if action == "sold":
        if item.get("seller") != app.current_user_id:
            return "Only the seller may mark this advertisement sold."
        item["status"] = "SOLD"
        save_state(app, state)
        return "Advertisement marked SOLD."
    if action == "inquire":
        schedule_event(app, "mail", {"to": item["seller"], "from": app.current_user_id, "subject": f"CLASSIFIED INQUIRY #{item_id}", "body": message[:1000]})
        return "Inquiry accepted for EasyPlex delivery."
    return "Unknown classified action."


def dashboard(app):
    state = load_state(app)
    messages = app.load_json("easyplex.json", default=[])
    orders = app.load_json("orders.json", default=[])
    inbox = [m for m in messages if m.get("to") == app.current_user_id]
    score = state["scores"].get(app.current_user_id, {"correct": 0, "attempts": 0})
    posts = sum(m.get("author_user_id") == app.current_user_id for group in app.forum_threads.values() for m in group)
    activity = [item for item in state.get("activity", []) if item.get("user_id") == app.current_user_id]
    downloads = sum(item.get("kind") == "LIBRARY" for item in activity)
    lines = [f"MEMBER {app.current_user_id}", f"HANDLE {app.current_handle or app.current_profile.get('last_handle') or 'NOT SET'}", f"EASYPLEX {sum(not m.get('read') for m in inbox)} waiting / {len(inbox)} total", f"FORUM POSTS {posts}", f"JOINED FORUMS {len(app.current_profile.get('joined_forums', []))}", f"TRIVIA {score['correct']} correct in {score['attempts']} attempts", f"LIBRARY ACCESSES {downloads}", "RECENT ACTIVITY"]
    lines.extend(f"  {item['date']} {item['summary']}" for item in activity[-5:])
    correspondents = state.get("member_memory", {}).get(app.current_user_id or "GUEST", {})
    lines.append("FORUM CORRESPONDENTS")
    lines.extend(f'  {handle:<12} {relationship_summary(memory)["level"]:<11} {memory.get("topic", "general correspondence")} ({memory.get("interactions", 0)})' for handle, memory in sorted(correspondents.items()))
    if not correspondents:
        lines.append("  None recorded")
    lines.append("ORDERS")
    lines.extend(f"  {o.get('number')} {o.get('name')} [{o.get('status', 'RECEIVED')}]" for o in orders if o.get("user_id") == app.current_user_id)
    owned = state.get("owned_equipment", {}).get(app.current_user_id or "GUEST", [])
    lines.append("OWNED EQUIPMENT")
    lines.extend(f'  {item.get("id")} {item.get("name")} [{item.get("status")}]' for item in owned)
    if not owned:
        lines.append("  None delivered")
    lines.append("RESERVATIONS")
    lines.extend(f"  {r['confirmation']} {r['origin']}-{r['destination']} [{r['status']}]" for r in state.get("reservations", []) if r.get("user_id") == app.current_user_id)
    return lines


def record_activity(app, user_id, kind, summary, details=None):
    if not user_id:
        return
    def append_activity(state):
        activity = state.setdefault("activity", [])
        activity.append({"user_id": user_id, "kind": kind, "date": simulation_datetime().isoformat(timespec="minutes"), "summary": summary[:160], "details": details or {}})
        state["activity"] = activity[-1000:]
    if hasattr(app, "update_json_atomic"):
        app.update_json_atomic("dynamic_state.json", {}, append_activity)
    else:
        state = load_state(app); append_activity(state); save_state(app, state)


def conference_schedule(forum_id):
    schedules = {"ibmhw": (21, "DOS MEMORY AND EXPANSION BOARDS"), "gamers": (20, "ADVENTURE GAME HINT EXCHANGE"), "hamnet": (22, "PACKET RADIO OPERATING NET"), "macdev": (19, "MACINTOSH PASCAL WORKSHOP")}
    schedules.update({'commodore': (20, 'DOCK64 FLIGHT LOG AND ASCII POSTCARDS'),
                      'appleii': (19, 'APPLESOFT TYPE-IN AND CLUB DISK CATALOG'),
                      'atarist': (21, 'TEMPO CALCULATOR AND NEWSLETTER WORKSHOP'),
                      'dos': (20, 'LOSTDISK BASIC ADVENTURE WORKSHOP')})
    hour, topic = schedules.get(forum_id, (21, "OPEN MEMBER CONFERENCE"))
    status = "OPEN NOW" if simulation_datetime().hour == hour else f"SCHEDULED {hour:02d}00 EASTERN"
    return topic, status


def conference_remark(forum_id, counter):
    remarks = ["Has anyone compared expanded-memory managers?", "Please identify your computer before asking a hardware question.", "I will place tonight's notes in the data library.", "Remember to keep replies brief for members at 300 baud."]
    community_remarks = {
        'commodore': [('Harbor64', 'DOCK64 pilots: record height, speed, and fuel after each turn.'), ('CopperCat', 'Our postcard exchange uses printable characters and lines no wider than 38 columns.')],
        'appleii': [('OrchardAnn', 'ORCHARD has five rounds. Has anyone tried changing the apples-per-basket line?'), ('DiskDaisy', 'I brought ten disks and ten blank catalog cards. That is enough for one evening.')],
        'atarist': [('MidiMoth', 'At 120 BPM, TEMPO should show 500 milliseconds for a quarter note.'), ('GemGwen', 'Please include a plain-text article copy with your newsletter project.')],
        'dos': [('SectorSam', 'LOSTDISK testers: try the cabinet before the desk and report what happens.'), ('BatchBeth', 'A useful bug report includes the inputs and the result you expected.')],
    }
    randomizer = rng(f"conference-{forum_id}-{counter}")
    if forum_id in community_remarks:
        return randomizer.choice(community_remarks[forum_id])
    return randomizer.choice(list(MEMBER_PROFILES)), randomizer.choice(remarks)


def weather(city):
    city = city.upper() or "CHICAGO"
    randomizer = rng(f"weather-{city}")
    temperature = randomizer.randint(12, 48)
    conditions = randomizer.choice(["CLEAR", "CLOUDY", "LIGHT SNOW", "LIGHT RAIN", "FOG"])
    wind = randomizer.choice(["NW", "N", "SW", "W"]) + f" {randomizer.randint(4, 18)}"
    alert = os.environ.get("CIS_WEATHER_ALERT")
    return [f"{city}  {temperature}F  {conditions}", f"WIND {wind}", f"TONIGHT: {conditions}, LOW {max(5, temperature - randomizer.randint(5, 14))}", *(["SYSOP WEATHER BULLETIN: " + alert] if alert else []), "DECEMBER 1988 SIMULATION WEATHER"]


def flight_schedule(origin, destination, travel_date="", cabin="COACH"):
    randomizer = rng(f"flight-{origin}-{destination}-{travel_date}-{cabin}")
    airlines = [("AA", "American"), ("UA", "United"), ("TW", "TWA"), ("EA", "Eastern"), ("PA", "Pan Am"), ("NW", "Northwest")]
    lines = []
    for code, _ in randomizer.sample(airlines, 3):
        departure = randomizer.choice([(7, 30), (8, 45), (10, 15), (12, 40), (14, 10), (17, 35)])
        duration = randomizer.randint(105, 270)
        departure_minutes = departure[0] * 60 + departure[1]
        arrival_minutes = departure_minutes + duration
        next_day = arrival_minutes >= 24 * 60
        arrival_minutes %= 24 * 60
        departure_text = f"{departure[0]:02d}{departure[1]:02d}"
        arrival_text = f"{arrival_minutes // 60:02d}{arrival_minutes % 60:02d}" + ("+1" if next_day else "")
        seats = randomizer.choice(["AVAILABLE", "AVAILABLE", "LIMITED", "WAIT LIST"])
        operation = randomizer.randrange(20)
        if operation == 0:
            seats = "CANCELLED"
        elif operation < 4:
            seats = "DELAYED"
        fare = randomizer.randrange(89, 329)
        lines.append(f"{code} {randomizer.randint(100, 899):>3}  {origin} {departure_text}  {destination} {arrival_text:<6} {seats:<9} ${fare} {cabin}")
    alert = os.environ.get("CIS_TRAVEL_ALERT")
    notice = "Schedules and availability are fictional simulation data." + (f" BULLETIN: {alert}" if alert else "")
    return lines + [notice]


def manage_world(app, command):
    parts = command.strip().split(maxsplit=1)
    if not parts or parts[0].upper() not in ("MARKET", "WEATHER", "TRAVEL", "STORE", "ADVENTURE", "CLEAR"):
        return "Commands: MARKET text, WEATHER text, TRAVEL text, STORE text, ADVENTURE text, or CLEAR name."
    state = load_state(app)
    controls = state.setdefault("world_controls", {})
    if parts[0].upper() == "CLEAR":
        if len(parts) < 2:
            return "Enter the control name to clear."
        key = parts[1].strip().lower()
        controls.pop(key, None); os.environ.pop(f"CIS_{key.upper()}_ALERT", None)
        save_state(app, state); return f"{key.upper()} bulletin cleared."
    if len(parts) < 2 or not parts[1].strip():
        return "Bulletin text is required."
    key = parts[0].lower(); controls[key] = parts[1].strip()[:160]
    os.environ[f"CIS_{key.upper()}_ALERT"] = controls[key]
    save_state(app, state)
    return f"{key.upper()} simulation bulletin set."


def reserve_itinerary(app, origin, destination, flight_line, travel_date="OPEN", passengers=1):
    if "CANCELLED" in flight_line:
        return None
    result = {}
    def update(state):
        reservations = state.setdefault("reservations", [])
        used = {item.get("confirmation") for item in reservations}
        number = 1001
        while f"CIS{number}" in used: number += 1
        confirmation = f"CIS{number}"; result["confirmation"] = confirmation
        reservations.append({"confirmation": confirmation, "user_id": app.current_user_id, "date": simulation_day().isoformat(), "travel_date": travel_date, "passengers": passengers, "origin": origin, "destination": destination, "flight": flight_line, "status": "CONFIRMED", "type": "AIR"})
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = load_state(app); update(state); save_state(app, state)
    confirmation = result["confirmation"]
    schedule_event(app, "mail", {"to": app.current_user_id, "from": "TRAVEL", "subject": f"ITINERARY {confirmation}", "body": f"Fictional reservation confirmed for {passengers} passenger(s), {travel_date}:\n{flight_line}\nAlways verify schedules and fares with the carrier."})
    if "DELAYED" in flight_line:
        schedule_event(app, "reservation_status", {"confirmation": confirmation, "status": "DELAYED - REBOOKING AVAILABLE"}, simulation_datetime() + timedelta(hours=1))
    schedule_event(app, "reservation_status", {"confirmation": confirmation, "status": "TICKETED"}, simulation_datetime() + timedelta(days=1))
    record_activity(app, app.current_user_id, "TRAVEL", f"Air itinerary {confirmation} reserved: {origin}-{destination}.")
    if hasattr(app, "cis_disruptions"):
        app.cis_disruptions.evaluate_reservations(app)
    return confirmation


def rebook_itinerary(app, confirmation, flight_line):
    if "CANCELLED" in flight_line:
        return "The replacement flight is cancelled."
    changed = {"value": False}
    def update(state):
        reservation = next((item for item in state.get("reservations", []) if item.get("confirmation") == confirmation.upper() and item.get("user_id") == app.current_user_id and item.get("type", "AIR") == "AIR" and item.get("status") != "CANCELLED"), None)
        if reservation: reservation["flight"] = flight_line; reservation["status"] = "REBOOKED"; changed["value"] = True
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = load_state(app); update(state); save_state(app, state)
    if not changed["value"]: return "Active air reservation not found."
    schedule_event(app, "mail", {"to": app.current_user_id, "from": "TRAVEL", "subject": f"REBOOKED {confirmation.upper()}", "body": f"Your fictional itinerary was rebooked:\n{flight_line}\nVerify the change with the carrier."})
    record_activity(app, app.current_user_id, "TRAVEL", f"Air itinerary {confirmation.upper()} rebooked.")
    return "Replacement itinerary recorded; EasyPlex confirmation will follow."


def reserve_hotel(app, city, hotel_line, nights=1):
    result = {}
    def update(state):
        reservations = state.setdefault("reservations", []); used = {item.get("confirmation") for item in reservations}; number = 1001
        while f"HTL{number}" in used: number += 1
        confirmation = f"HTL{number}"; result["confirmation"] = confirmation
        reservations.append({"confirmation": confirmation, "user_id": app.current_user_id, "date": simulation_day().isoformat(), "origin": city, "destination": city, "flight": hotel_line, "nights": nights, "status": "CONFIRMED", "type": "HOTEL"})
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = load_state(app); update(state); save_state(app, state)
    confirmation = result["confirmation"]
    schedule_event(app, "mail", {"to": app.current_user_id, "from": "TRAVEL", "subject": f"LODGING {confirmation}", "body": f"Fictional lodging request confirmed for {nights} night(s):\n{hotel_line}\nRates and availability must be verified with the property."})
    schedule_event(app, "reservation_status", {"confirmation": confirmation, "status": "GUARANTEED"}, simulation_datetime() + timedelta(days=1))
    record_activity(app, app.current_user_id, "TRAVEL", f"Hotel request {confirmation} recorded for {city}.")
    return confirmation


def cancel_member_item(app, command):
    parts = command.strip().upper().split()
    if len(parts) != 3 or parts[0] != "CANCEL":
        return "Commands: CANCEL ORDER number or CANCEL RES confirmation."
    if parts[1] == "ORDER":
        orders = app.load_json("orders.json", default=[])
        order = next((o for o in orders if o.get("user_id") == app.current_user_id and str(o.get("number")) == parts[2]), None)
        if not order:
            return "Order not found."
        if order.get("status", "RECEIVED") not in ("RECEIVED", "PROCESSING", "BACK ORDER", "BACK ORDERED"):
            return "That order can no longer be cancelled."
        order["status"] = "CANCELLED"
        app.save_json_atomic("orders.json", orders)
        return "Order cancelled."
    if parts[1] in ("RES", "RESERVATION"):
        state = load_state(app)
        reservation = next((r for r in state.get("reservations", []) if r.get("user_id") == app.current_user_id and r.get("confirmation") == parts[2]), None)
        if not reservation:
            return "Reservation not found."
        reservation["status"] = "CANCELLED"
        save_state(app, state)
        return "Reservation cancelled."
    return "Unknown item type."


def ensure_library_activity(app):
    state = load_state(app)
    marker = simulation_day().isoformat()
    if state.get("library_day") == marker:
        return False
    numbers = [f.get("number", 0) for group in app.library_files.values() for f in group]
    candidates = [("IRQNOTE.TXT", "IRQ assignments for common PC expansion boards"), ("MODEMREF.TXT", "Hayes-compatible modem command reference"), ("MEMORY.TXT", "DOS conventional and expanded memory notes"), ("RS232.TXT", "RS-232 connector and signal reference"), ("CONFIG.TXT", "CONFIG.SYS configuration notes"), ("AUTOEXEC.TXT", "AUTOEXEC.BAT startup notes"), ("VGAINFO.TXT", "VGA display compatibility notes"), ("EMSNOTE.TXT", "LIM expanded-memory notes")]
    name, description = rng("library-daily").choice(candidates)
    app.library_files.setdefault("ibmhw_lib1", []).append({"number": max(numbers, default=100) + 1, "name": name, "bytes": 4096, "date": simulation_day().strftime("%m/%d/%y"), "downloads": 0, "description": description, "status": "approved"})
    app.save_json_atomic("library_files.json", app.library_files)
    state["library_day"] = marker
    save_state(app, state)
    return True


def event_monitor(app):
    state = load_state(app)
    pending = [e for e in state["events"] if not e.get("processed")]
    processed = [e for e in state["events"] if e.get("processed")]
    by_type = {}
    for event in pending:
        by_type[event["type"]] = by_type.get(event["type"], 0) + 1
    lines = [f"SIMULATED CLOCK {simulation_datetime().strftime('%m/%d/%y %I:%M %p')}", f"EVENTS WAITING {len(pending)}", f"EVENTS PROCESSED {len(processed)}"]
    lines.extend(f"{kind.upper():<18} {count}" for kind, count in sorted(by_type.items()))
    lines.extend(["", "SIMULATED MEMBERS"])
    lines.extend(f"{handle:<12} {profile[0]:<7} {profile[1]}" for handle, profile in MEMBER_PROFILES.items())
    return lines


def manage_event(app, command):
    if command.strip().upper() == "REPAIR STATE":
        repairs = repair_state(app)
        return "; ".join(repairs) if repairs else "State checked; no repairs required."
    state = load_state(app)
    parts = command.strip().upper().split()
    if len(parts) == 3 and parts[:2] == ["SET", "DATE"]:
        try:
            selected = datetime.strptime(parts[2], "%m/%d/%y").date()
        except ValueError:
            return "Date must have the form 12/15/88."
        if selected.year != 1988:
            return "Simulation date must remain in 1988."
        state["simulation_date"] = selected.isoformat()
        state.setdefault("timeline_day", 0)
        os.environ["CIS_SIMULATION_DATE"] = selected.isoformat()
        save_state(app, state)
        return f"Simulation date set to {selected:%m/%d/%y}."
    if len(parts) == 3 and parts[:2] == ["SET", "TIME"]:
        try:
            selected_time = datetime.strptime(parts[2], "%H:%M").strftime("%H:%M")
        except ValueError:
            return "Time must have the form 21:30."
        state["simulation_time"] = selected_time
        os.environ["CIS_SIMULATION_TIME"] = selected_time
        save_state(app, state)
        return f"Simulation time set to {selected_time}."
    if parts == ["ADVANCE", "1", "DAY"]:
        selected = simulation_day() + timedelta(days=1)
        if selected.year != 1988:
            selected = date(1988, 12, 1)
        state["simulation_date"] = selected.isoformat()
        state["timeline_day"] = int(state.get("timeline_day", 0)) + 1
        os.environ["CIS_SIMULATION_DATE"] = selected.isoformat()
        save_state(app, state)
        return f"Simulation advanced to {selected:%m/%d/%y}."
    if parts == ["PROCESS", "EVENTS"]:
        return "Due events processed." if process_events(app) else "No due events."
    if parts == ["ARCHIVE"]:
        before = len(state["events"])
        state["events"] = [event for event in state["events"] if not event.get("processed")]
        save_state(app, state)
        return f"Archived {before - len(state['events'])} processed event(s)."
    if len(parts) == 2 and parts[0] == "CANCEL" and parts[1].isdigit():
        event = next((e for e in state["events"] if e["id"] == int(parts[1]) and not e.get("processed")), None)
        if not event:
            return "Pending event not found."
        event["processed"] = True
        event["cancelled"] = True
        save_state(app, state)
        return f"Event {event['id']} cancelled."
    return "Commands: CANCEL n, ARCHIVE, REPAIR STATE, SET DATE, SET TIME, ADVANCE 1 DAY, PROCESS EVENTS, or M."


def validate_state(app):
    state = load_state(app)
    issues = []
    for event in state.get("events", []):
        if not all(key in event for key in ("id", "type", "due_at", "payload")):
            issues.append("event missing required fields")
    for item in state.get("classifieds", []):
        if not all(key in item for key in ("id", "text", "status")):
            issues.append("classified missing required fields")
    for reservation in state.get("reservations", []):
        if not all(key in reservation for key in ("confirmation", "user_id", "status")):
            issues.append("reservation missing required fields")
    for user, portfolio in state.get("stock_portfolios", {}).items():
        if not isinstance(portfolio, dict) or not isinstance(portfolio.get("cash"), (int, float)) or not isinstance(portfolio.get("holdings"), dict):
            issues.append(f"portfolio invalid for {user}")
    for user, notes in state.get("notebooks", {}).items():
        if not isinstance(notes, list) or any(not isinstance(item, dict) or "id" not in item or "title" not in item for item in notes):
            issues.append(f"notebook invalid for {user}")
    return issues


def repair_state(app):
    repairs = []
    def repair(state):
        for key, empty in (("events", []), ("classifieds", []), ("reservations", []), ("activity", []), ("stock_portfolios", {}), ("notebooks", {}), ("store_carts", {}), ("traveler_profiles", {})):
            if not isinstance(state.get(key), type(empty)):
                state[key] = empty.copy(); repairs.append(f"reset invalid {key}")
        valid_events = [event for event in state["events"] if isinstance(event, dict) and all(key in event for key in ("id", "type", "due_at", "payload"))]
        if len(valid_events) != len(state["events"]): repairs.append("removed malformed events")
        state["events"] = valid_events
        used = set()
        for event in state["events"]:
            if not isinstance(event.get("id"), int) or event["id"] in used:
                event["id"] = max(used, default=0) + 1; repairs.append("renumbered event")
            used.add(event["id"]); event.setdefault("processed", False)
        state["next_event_id"] = max(used, default=0) + 1
        for user, portfolio in list(state["stock_portfolios"].items()):
            if not isinstance(portfolio, dict):
                state["stock_portfolios"][user] = {"cash": 10000.0, "realized": 0.0, "holdings": {}, "transactions": []}; repairs.append(f"reset portfolio {user}"); continue
            portfolio.setdefault("cash", 10000.0); portfolio.setdefault("realized", 0.0); portfolio.setdefault("holdings", {}); portfolio.setdefault("transactions", [])
            if not isinstance(portfolio["holdings"], dict): portfolio["holdings"] = {}; repairs.append(f"reset holdings {user}")
            portfolio["holdings"] = {symbol: pos for symbol, pos in portfolio["holdings"].items() if isinstance(pos, dict) and isinstance(pos.get("shares"), int) and pos["shares"] > 0 and isinstance(pos.get("average_cost"), (int, float))}
        for user, notes in list(state["notebooks"].items()):
            if not isinstance(notes, list): state["notebooks"][user] = []; repairs.append(f"reset notebook {user}")
        valid_reservations = [item for item in state["reservations"] if isinstance(item, dict) and item.get("confirmation") and item.get("user_id")]
        if len(valid_reservations) != len(state["reservations"]): repairs.append("removed malformed reservations")
        state["reservations"] = valid_reservations
        for reservation in state["reservations"]: reservation.setdefault("status", "CONFIRMED"); reservation.setdefault("type", "AIR")
        state.setdefault("repair_log", []).append({"date": simulation_datetime().isoformat(timespec="minutes"), "repairs": list(repairs)})
        state["repair_log"] = state["repair_log"][-25:]
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, repair)
    else:
        state = load_state(app); repair(state); save_state(app, state)
    return repairs


def manage_content(app, command):
    state = load_state(app)
    if command.upper().startswith("ANN "):
        text = command[4:].strip()[:160]
        if text:
            state.setdefault("system_announcements", []).append(text)
            save_state(app, state)
            return "System announcement posted."
    if command.upper().startswith("NOTE "):
        parts = command.split(maxsplit=2)
        if len(parts) == 3 and parts[1] in state.get("member_profiles", {}):
            state["member_profiles"][parts[1]]["sysop_note"] = parts[2][:160]
            save_state(app, state)
            return "Simulated-member note updated."
    return "Commands: ANN text, NOTE Handle text, or M."


def ensure_forum_activity(app):
    marker = simulation_day().isoformat()
    metadata = app.load_json("dynamic_state.json", default={})
    if metadata.get("forum_day") == marker:
        return False
    templates = [
        ("ibmhw_tech", "IRQ conflict with serial board", "My second serial adapter conflicts with the mouse. Which IRQ arrangement has worked for you?"),
        ("gamers_general", "Weekend high scores", "Post your best scores and the machine version you played."),
        ("hamnet_general", "Evening propagation report", "Ten meters was quiet here, but twenty opened shortly after sunset."),
    ]
    section, subject, body = rng("forum-activity").choice(templates)
    ids = [m.get("id", 0) for messages in app.forum_threads.values() for m in messages]
    author = rng("forum-author").choice(HANDLES)
    app.forum_threads.setdefault(section, []).append({"id": max(ids, default=1000) + 1, "date": simulation_day().strftime("%m/%d/%y"), "author": author, "author_user_id": "SIMULATED", "subject": subject, "body": body})
    app.save_json_atomic("forums.json", app.forum_threads)
    metadata["forum_day"] = marker
    app.save_json_atomic("dynamic_state.json", metadata)
    schedule_event(app, "forum_reply", {"section": section, "message_id": max(ids, default=1000) + 1, "author": rng("reply-author").choice([h for h in HANDLES if h != author]), "body": "I have seen the same thing here. I will check my notes and post the settings that worked."}, simulation_datetime() + timedelta(hours=2))
    return True
