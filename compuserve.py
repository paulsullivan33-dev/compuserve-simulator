from cis_session import read_input as input
import time
import random
import sys
import re
import getpass
import os
import uuid
import textwrap
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from cis_security import hash_password, verify_password
from cis_migrations import CURRENT_SCHEMA_VERSION, migrate_data
from cis_session import SessionState, GoNavigation, navigation_prompts, active_session
from cis_settings import PRESETS, apply_preset, merged_settings
from cis_storage import (
    MUTABLE_DATA_FILES,
    create_backup as storage_create_backup,
    load_json as storage_load_json,
    restore_latest as storage_restore_latest,
    upgrade_database, database_status,
    register_session, unregister_session, list_sessions,
    post_live_message, read_live_messages, recent_live_messages,
    set_cb_presence, remove_cb_presence, list_cb_presence, claim_cb_ambient,
    write_json_atomic as storage_write_json_atomic,
    update_json_atomic as storage_update_json_atomic,
)
from cis_sysop import (
    account_rows, pending_uploads, reset_password, set_upload_status,
    toggle_disabled, unlock_account,
)
from cis_terminal import header_line, menu_lines, wrap_terminal_text
from cis_version import RELEASE_NAME, VERSION
from cis_web_files import offer_download
import cis_mail
import cis_billing
import cis_accounts
import cis_communities
import cis_phones
import cis_forums
import cis_library
import cis_news
import cis_dynamic
import cis_period_news
import cis_reference
import cis_store
import cis_discovery
import cis_business
import cis_travel
import cis_experience
import cis_drafts
import cis_announcements
import cis_weather
import cis_timeline
import cis_timecapsule
import cis_features
import cis_magazine
import cis_cb
import cis_story
import cis_disruptions
import cis_ownership
import cis_shareware
import cis_adventure_league

try:
    import msvcrt
except ImportError:
    msvcrt = None

try:
    import winsound
except ImportError:
    winsound = None

SIMULATION_YEAR = 1988
SIMULATION_DATE = "12/15/88"
SCREEN_WIDTH = 80
BAUD_RATES = {300: 6.00, 1200: 12.00, 2400: 24.00}
connection_baud = 1200
premium_charges = 0.0
capture_path = None
startup_options = {
    "display_mode": "scroll", "skip_dialing": False, "customized": False,
    "connection_mode": "clean", "sound": False, "page_pause": False,
    "refresh_news": False,
}
transmitted_line_count = 0
session_state = SessionState()
BASE_DIR = Path(__file__).resolve().parent

def load_json(filename, default=None):
    data = storage_load_json(BASE_DIR, filename, default)
    data, changed = migrate_data(filename, data)
    if changed and filename in MUTABLE_DATA_FILES:
        storage_write_json_atomic(BASE_DIR, filename, data)
    return data


def create_data_backup():
    return storage_create_backup(BASE_DIR, MUTABLE_DATA_FILES)


def update_json_atomic(filename, default, mutator):
    return storage_update_json_atomic(BASE_DIR, filename, default, mutator)


def restore_latest_backup():
    return storage_restore_latest(BASE_DIR, MUTABLE_DATA_FILES)


startup_options = merged_settings(load_json("terminal_config.json", default={}))
connection_baud = int(startup_options["baud"])
SCREEN_WIDTH = int(startup_options["columns"])

page_names = load_json("page_names.json")


current_handle = None
current_user_id = None
current_profile = {}

session_start = None
live_session_id = os.environ.get("CIS_SESSION_ID") or uuid.uuid4().hex

OPTION_TARGETS = {
    "main": {
        "1": "mail", "2": "forums", "3": "cb", "4": "news",
        "5": "finance", "6": "travel", "7": "reference",
        "8": "shopping", "9": "games", "10": "support",
    },
    "forums": {"1": "ibmhw", "2": "gamers"},
    "ibmhw_libs": {
        "1": "ibmhw_lib1", "2": "ibmhw_lib2",
        "3": "ibmhw_lib3", "4": "ibmhw_lib4",
    },
}

FORUM_CATALOG = {
    "ibmhw": {
        "title": "IBM PC Hardware Forum",
        "sections": {
            "1": ("ibmhw_hw", "Hardware Discussion"),
            "2": ("ibmhw_tech", "Technical Support"),
            "3": ("ibmhw_reviews", "Hardware Reviews"),
            "4": ("ibmhw_tips", "Tips & Techniques"),
            "5": ("ibmhw_vendors", "Vendor Support"),
            "6": ("ibmhw_announcements", "Sysop Announcements"),
            "7": ("ibmhw_rules", "Instructions & Rules"),
        },
    },
    "gamers": {
        "title": "Gamers Forum",
        "sections": {
            "1": ("gamers_general", "General Gaming"),
            "2": ("gamers_pc", "PC Games"),
            "3": ("gamers_console", "Console Games"),
            "4": ("gamers_reviews", "Game Reviews"),
        },
    },
    "macdev": {"title": "Macintosh Developers Forum", "sections": {"1": ("macdev_general", "General")}},
    "photo": {"title": "Photography Forum", "sections": {"1": ("photography_general", "General")}},
    "hamnet": {"title": "Amateur Radio Forum", "sections": {"1": ("hamnet_general", "General")}},
    "science": {"title": "Science Forum", "sections": {"1": ("science_general", "General")}},
}

FORUM_CATALOG.update(cis_communities.FORUMS)
FORUM_CHOICES = dict(zip((str(i) for i in range(1, 11)),
                        ('ibmhw', 'gamers', 'macdev', 'photo', 'hamnet', 'science',
                         'commodore', 'appleii', 'atarist', 'dos')))

def cis_prompt(context="command"):
    prompts = {
        "main": "Enter choice !",
        "forums": "Enter choice !",
        "library": "Enter choice !",
        "cb": "CB>",
        "go": "GO:",
        "more": "More:",
        "error": "Huh"
    }
    return prompts.get(context, "Command:")


def header_bar(screen_key):
    global go_prompt_screen
    go_prompt_screen = screen_key
    page = page_names.get(screen_key, "")
    ansi_scroll(header_line("CompuServe", page, SCREEN_WIDTH), 0.01)


def page_indicator(screen_key):
    page = page_names.get(screen_key, "")
    ansi_scroll(page.rjust(SCREEN_WIDTH), 0.01)


def clear():
    mode = current_profile.get("display_mode", startup_options["display_mode"])
    if os.environ.get("CIS_ANSI") == "1":
        sys.stdout.write("\x1b[2J\x1b[H")
        sys.stdout.flush()
    elif mode == "screen":
        sys.stdout.write("\f")
        sys.stdout.flush()
    else:
        print()

def ansi_scroll(text, delay=0.01):
    global transmitted_line_count
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(text))
    delay = 0 if startup_options.get("fast_mode") else max(delay, 10 / connection_baud)
    visual_lines = wrap_terminal_text(text, SCREEN_WIDTH)
    for line in visual_lines:
        for char in line:
            if terminal_flow_control() == "interrupt":
                print("^C")
                return False
            if startup_options["connection_mode"] == "variable" and random.random() < 0.001:
                char = random.choice("?#%")
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
        transmitted_line_count += 1
        if capture_path:
            with capture_path.open("a", encoding="utf-8") as capture:
                capture.write(line + "\n")
        page_pause = current_profile.get("page_pause", startup_options["page_pause"])
        if page_pause and transmitted_line_count % 16 == 0:
            input("More ! ")
    return True


def terminal_flow_control():
    # A web session has no direct relationship with the launcher's physical
    # keyboard. Reading msvcrt there can consume unrelated keys, and Ctrl-S
    # would wait forever for a Ctrl-Q that the browser cannot deliver.
    if os.environ.get("CIS_WEB_TERMINAL") == "1":
        return None
    if msvcrt is None or not msvcrt.kbhit():
        return None
    key = msvcrt.getwch()
    if key == "\x03":
        return "interrupt"
    if key == "\x13":
        while True:
            resumed = msvcrt.getwch()
            if resumed == "\x11":
                return None
            if resumed == "\x03":
                return "interrupt"
    return None


def modem_sound(frequency, duration):
    if startup_options["sound"] and winsound is not None:
        winsound.Beep(frequency, duration)


def startup_configuration():
    global connection_baud, SCREEN_WIDTH
    ansi_scroll("COMPUSERVE TERMINAL CONFIGURATION", 0.001)
    ansi_scroll(
        f"{connection_baud} baud, {SCREEN_WIDTH} columns, "
        f'{startup_options["display_mode"]} display',
        0.001,
    )
    action = input("Press RETURN to accept, C to change, or P for preset: ").strip().upper()
    if action == "P":
        ansi_scroll("Presets: C64, IBM, MAC", 0.001)
        if apply_preset(startup_options, input("Preset: ").strip()):
            connection_baud = int(startup_options["baud"])
            SCREEN_WIDTH = int(startup_options["columns"])
            save_json_atomic("terminal_config.json", startup_options)
        return
    if action != "C":
        return
    baud = input("Baud [300/1200/2400]: ").strip()
    columns = input("Columns [40/80]: ").strip()
    mode = input("Display [scroll/screen]: ").strip().lower()
    skip = input("Skip modem dialing [Y/N]: ").strip().upper()
    connection = input("Connection [clean/variable]: ").strip().lower()
    sound = input("Modem sound [Y/N]: ").strip().upper()
    paging = input("Pause every 16 lines [Y/N]: ").strip().upper()
    refresh = input("Refresh current news after login [Y/N]: ").strip().upper()
    fast = input("Fast output mode [Y/N]: ").strip().upper()
    if baud.isdigit() and int(baud) in BAUD_RATES:
        connection_baud = int(baud)
    if columns.isdigit() and int(columns) in (40, 80):
        SCREEN_WIDTH = int(columns)
    if mode in ("scroll", "screen"):
        startup_options["display_mode"] = mode
    startup_options["skip_dialing"] = skip == "Y"
    if connection in ("clean", "variable"):
        startup_options["connection_mode"] = connection
    startup_options["sound"] = sound == "Y"
    startup_options["page_pause"] = paging == "Y"
    startup_options["refresh_news"] = refresh == "Y"
    startup_options["fast_mode"] = fast == "Y"
    startup_options["customized"] = True
    startup_options["baud"] = connection_baud
    startup_options["columns"] = SCREEN_WIDTH
    save_json_atomic("terminal_config.json", startup_options)


def set_capture(enabled):
    global capture_path
    if enabled:
        captures = BASE_DIR / "captures"
        captures.mkdir(exist_ok=True)
        capture_path = captures / (datetime.now().strftime("CIS-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8] + '.txt')
        capture_path.write_text("CompuServe session capture\n", encoding="utf-8")
        ansi_scroll(f"Capture started: {capture_path.name}", 0.01)
    else:
        old_path = capture_path
        capture_path = None
        ansi_scroll(
            f"Capture closed: {old_path.name}" if old_path else "Capture was not active.",
            0.01,
        )
        if old_path:
            offer_download(old_path)

# --- Time & Billing ----------------------------------------------------------

def get_elapsed_seconds():
    if session_start is None:
        return 0
    return int(time.time() - session_start)

def format_elapsed(seconds):
    return cis_billing.format_elapsed(seconds)

def is_prime_time(now=None):
    return cis_billing.is_prime_time(now)


def connection_rate_per_hour(now=None):
    return cis_billing.connection_rate_per_hour(connection_baud, BAUD_RATES, now)


def get_estimated_cost(seconds, now=None):
    return cis_billing.estimated_cost(seconds, connection_baud, BAUD_RATES, now)

def show_logout_summary():
    clear()
    seconds = get_elapsed_seconds()
    elapsed_str = format_elapsed(seconds)
    cost = get_estimated_cost(seconds)
    if current_user_id:
        cis_billing.record_session(sys.modules[__name__], seconds, connection_baud, cost, premium_charges)
    ansi_scroll("Session Summary", 0.01)
    ansi_scroll("--------------", 0.01)
    ansi_scroll(f"Connect time: {elapsed_str}", 0.01)
    ansi_scroll(f"Estimated charges: ${cost:0.2f}", 0.01)
    ansi_scroll(f"Premium service charges: ${premium_charges:0.2f}", 0.01)
    ansi_scroll(f"Estimated total: ${cost + premium_charges:0.2f}", 0.01)
    ansi_scroll("\nThank you for using CompuServe!", 0.01)
    time.sleep(3)

# --- Load JSON files ---------------------------------------------------------

screens = load_json("screens.json")
for forum_id, forum in cis_communities.FORUMS.items():
    screens[forum['library']] = {'title': forum['title'] + ' Data Library', 'options': {}}
fake_lines = load_json("fake_lines.json")
forum_threads = load_json("forums.json")
go_map = load_json("go_commands.json")
cb_personalities = load_json("cb_personalities.json")
profiles = load_json("profiles.json", default={})
library_files = load_json("library_files.json", default={})
service_data = load_json("service_data.json", default={})
cis_dynamic.apply_clock_state(sys.modules[__name__])


def initialize_database():
    """Upgrade persistent storage explicitly before starting an interactive session.

    The module remains importable by tests and supporting tools without running a
    full application-schema upgrade. Reload mutable datasets after the upgrade so
    migrations that add or transform fields are reflected in this process.
    """
    global forum_threads, profiles, library_files
    result = upgrade_database(BASE_DIR, CURRENT_SCHEMA_VERSION)
    cis_communities.install(BASE_DIR)
    forum_threads = load_json("forums.json")
    profiles = load_json("profiles.json", default={})
    library_files = load_json("library_files.json", default={})
    cis_dynamic.apply_clock_state(sys.modules[__name__])
    return result

PAGE_ADDRESSES = {
    "CIS-1": "main", "CIS-4": "support", "PCS-31": "mail",
    "PCS-32": "cb", "PCS-50": "forums", "NEW-1": "news",
    "FIN-1": "finance", "TRV-1": "travel", "REF-1": "reference",
    "HOM-8": "shopping", "HOM-60": "games", "IBMHW-1": "ibmhw", "MAG-1": "magazine",
    "GAMERS-1": "gamers", "LIB-1": "ibmhw_lib1", "LIB-2": "ibmhw_lib2",
    "LIB-3": "ibmhw_lib3", "LIB-4": "ibmhw_lib4",
}
for forum_id, forum in cis_communities.FORUMS.items():
    PAGE_ADDRESSES[page_names[forum_id]] = forum_id
    PAGE_ADDRESSES[page_names[forum['library']]] = forum['library']


def resolve_go_destination(destination, current_screen="main"):
    destination = destination.strip().upper()
    if destination in ("BACK", "RECENT"):
        return destination.lower()
    keyword_target = go_map.get("GO " + destination)
    if keyword_target:
        return keyword_target
    prefix_matches = {target for command, target in go_map.items() if command[3:].startswith(destination) and len(destination) >= 3}
    if len(prefix_matches) == 1:
        return prefix_matches.pop()
    if destination in PAGE_ADDRESSES:
        return PAGE_ADDRESSES[destination]
    if destination.isdigit():
        current_address = page_names.get(current_screen, "")
        if "-" in current_address:
            relative = current_address.split("-", 1)[0] + "-" + destination
            return PAGE_ADDRESSES.get(relative)
    return None

# --- Modem Dial-In ----------------------------------------------------------

def modem_dial_in():
    while True:
        clear()
        ansi_scroll("ATZ", 0.01)
        ansi_scroll("OK", 0.01)
        ansi_scroll("ATDT 1-800-555-1234", 0.01)
        modem_sound(440, 180)
        modem_sound(620, 180)
        outcome = "CONNECT"
        if startup_options["connection_mode"] == "variable":
            outcome = random.choices(
                ["CONNECT", "BUSY", "NO CARRIER", "NO DIALTONE"],
                weights=[75, 12, 9, 4],
            )[0]
        if outcome != "CONNECT":
            ansi_scroll(outcome, 0.01)
            if input("R to redial, Q to quit: ").strip().upper() == "R":
                continue
            return False
        modem_sound(1000, 120)
        ansi_scroll(f"CONNECT {connection_baud}", 0.01)
        ansi_scroll("CompuServe Information Service", 0.02)
        ansi_scroll(f"Copyright (c) {SIMULATION_YEAR} CompuServe Incorporated", 0.02)
        return True

# --- Profiles ---------------------------------------------------------------


def password_input(prompt="Password: "):
    """Read a secret from the console or the web terminal's masked input."""
    if os.environ.get("CIS_WEB_TERMINAL") == "1" or os.environ.get("CIS_REMOTE_TERMINAL") == "1":
        import builtins
        return builtins.input(prompt)
    return getpass.getpass(prompt)


def load_profile(user_id):
    global current_profile
    current_profile = cis_accounts.load_profile(sys.modules[__name__], user_id)

def save_json_atomic(filename, data):
    storage_write_json_atomic(BASE_DIR, filename, data)


def save_profiles():
    save_json_atomic("profiles.json", profiles)


def set_account_password(profile, prompt="New password: "):
    return cis_accounts.set_password(sys.modules[__name__], profile, prompt)


def authenticate_account(user_id):
    return cis_accounts.authenticate(sys.modules[__name__], user_id)

# --- Login Screen ------------------------------------------------------------

def login_screen():
    global current_user_id, session_start, connection_baud, SCREEN_WIDTH
    ansi_scroll("Enter CIS to log in, or PHONES for access numbers.", 0.01)
    while True:
        host = input("Host Name: ").strip().upper() or "CIS"
        if host == "PHONES":
            cis_phones.run(ansi_scroll)
            continue
        if host != "CIS":
            ansi_scroll("Invalid Host Name", 0.01)
        break
    user_id = input("User ID: ").strip() or "70000,0001"
    while not re.fullmatch(r"\d{5},\d{4}", user_id):
        ansi_scroll("User ID must have the form 70000,0001", 0.01)
        user_id = input("User ID: ").strip() or "70000,0001"
    if not authenticate_account(user_id):
        return False
    session_state.top_announcements_shown = False
    current_user_id = user_id
    load_profile(user_id)
    session_state.user_id = current_user_id
    session_state.profile = current_profile
    connection_baud = (
        connection_baud if startup_options["customized"]
        else int(current_profile.get("baud", 1200))
    )
    if connection_baud not in BAUD_RATES:
        connection_baud = 1200
    SCREEN_WIDTH = (
        SCREEN_WIDTH if startup_options["customized"]
        else int(current_profile.get("columns", 80))
    )
    if SCREEN_WIDTH not in (40, 80):
        SCREEN_WIDTH = 80
    if startup_options["customized"]:
        current_profile.update({
            "baud": connection_baud,
            "columns": SCREEN_WIDTH,
            "display_mode": startup_options["display_mode"],
            "page_pause": startup_options["page_pause"],
        })
        save_profiles()
    ansi_scroll("Access granted", 0.01)
    waiting = mail_waiting_count(user_id)
    if waiting and current_profile.get("mail_notice", True):
        ansi_scroll(f"You have {waiting} waiting EasyPlex message(s).", 0.01)
    session_start = time.time()
    session_state.started_at = session_start
    register_session(
        BASE_DIR, live_session_id, current_user_id,
        current_handle or current_profile.get("handle", current_user_id),
        os.environ.get("CIS_TRANSPORT", "CONSOLE"),
    )
    cis_dynamic.ensure_forum_activity(sys.modules[__name__])
    cis_dynamic.ensure_library_activity(sys.modules[__name__])
    cis_shareware.ensure_arc(sys.modules[__name__])
    cis_dynamic.process_events(sys.modules[__name__])
    cis_story.ensure_case(sys.modules[__name__])
    cis_disruptions.evaluate_reservations(sys.modules[__name__])
    return True


# --- Temporal Destination (time-capsule mode) ---------------------------------

def _remembered_simulation_date():
    """The account's last-chosen era, or None."""
    return cis_timecapsule.parse_stored_date(current_profile.get("last_simulation_date"))


def _set_simulation_date(value):
    session_state.simulation_date = value
    if value is None:
        current_profile.pop("last_simulation_date", None)
    else:
        current_profile["last_simulation_date"] = value.isoformat()
    save_profiles()
    ansi_scroll(f"Temporal destination: {cis_timecapsule.describe(value)}.", 0.01)


def _featured_date_menu():
    """Return the chosen featured date, or None to go back."""
    while True:
        clear()
        header_bar("main")
        ansi_scroll("FEATURED DATES", 0.01)
        ansi_scroll("--------------", 0.01)
        for index, (when, label) in enumerate(cis_timecapsule.FEATURED_DATES, 1):
            ansi_scroll(f"{index}  {when:%m/%d/%Y}  {label}", 0.01)
        ansi_scroll("M  Back", 0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(cis_timecapsule.FEATURED_DATES):
            return cis_timecapsule.FEATURED_DATES[int(choice) - 1][0]
        ansi_scroll("Enter a number from the list, or M.", 0.01)


def _prompt_for_simulation_date():
    """Return the typed date, or None to go back."""
    while True:
        text = input("Date (MM/DD/YYYY), or M to go back: ").strip()
        if text.upper() == "M":
            return None
        try:
            return cis_timecapsule.parse_user_date(text)
        except ValueError as exc:
            ansi_scroll(str(exc), 0.01)


def choose_temporal_destination():
    """Offer time-capsule date selection once, right after login."""
    remembered = _remembered_simulation_date()
    if remembered is not None:
        answer = input(f"Return to {remembered:%A, %B %d, %Y}? (Y/N) ").strip().upper()
        if answer in ("Y", "YES", ""):
            _set_simulation_date(remembered)
            return
        if answer not in ("N", "NO"):
            ansi_scroll("Assuming NO.", 0.01)
    while True:
        clear()
        header_bar("main")
        ansi_scroll("TEMPORAL DESTINATION", 0.01)
        ansi_scroll("--------------------", 0.01)
        ansi_scroll("Experience CompuServe as of the date you choose.", 0.01)
        ansi_scroll("", 0.01)
        ansi_scroll("1  Present Day (the service's current date)", 0.01)
        ansi_scroll("2  Featured dates...", 0.01)
        ansi_scroll("3  Enter a date (MM/DD/YYYY, 1979-1998)", 0.01)
        ansi_scroll("4  Surprise me", 0.01)
        choice = input("Choice: ").strip()
        if choice == "1":
            _set_simulation_date(None)
            return
        if choice == "2":
            picked = _featured_date_menu()
            if picked is None:
                continue
            _set_simulation_date(picked)
            return
        if choice == "3":
            picked = _prompt_for_simulation_date()
            if picked is None:
                continue
            _set_simulation_date(picked)
            return
        if choice == "4":
            picked = cis_timecapsule.surprise_date(current_user_id or "")
            ansi_scroll(f"Your destination: {picked:%A, %B %d, %Y}.", 0.01)
            _set_simulation_date(picked)
            return
        ansi_scroll("Enter 1, 2, 3, or 4.", 0.01)


def account_settings():
    ansi_scroll(f"Account: {current_user_id}", 0.01)
    choice = input("P Change password, or M for menu ! ").strip().upper()
    if choice != "P":
        return
    current = password_input("Current password: ")
    if not verify_password(current, current_profile.get("password_hash", "")):
        ansi_scroll("Current password is incorrect.", 0.01)
        return
    set_account_password(current_profile)


def sysop_console():
    if not current_profile.get("is_sysop"):
        ansi_scroll("SYSOP privileges required.", 0.01)
        return
    while True:
        clear()
        header_bar("sysop")
        ansi_scroll("COMPUSERVE LOCAL SYSOP MAINTENANCE", 0.01)
        ansi_scroll("1  Account maintenance", 0.01)
        ansi_scroll("2  Library upload approval", 0.01)
        ansi_scroll("3  Feedback and order review", 0.01)
        ansi_scroll("4  Post IBMHW announcement", 0.01)
        ansi_scroll("5  Create backup", 0.01)
        ansi_scroll("6  Restore latest backup", 0.01)
        ansi_scroll("7  Dynamic event monitor", 0.01)
        ansi_scroll("8  Dynamic content editor", 0.01)
        ansi_scroll("9  Members now online", 0.01)
        ansi_scroll("10 Simulation world controls", 0.01)
        ansi_scroll("11 System announcements", 0.01)
        ansi_scroll("M  Return to service", 0.01)
        choice = input("SYSOP ! ").strip().upper()
        if choice == "M":
            return
        if choice == "1":
            sysop_accounts()
        elif choice == "2":
            sysop_uploads()
        elif choice == "3":
            sysop_review_data()
        elif choice == "4":
            subject = input("Subject: ").strip()
            body = line_editor()
            if subject and body:
                forum_post("ibmhw_announcements", subject, body)
        elif choice == "5":
            ansi_scroll(f"Backup complete: {create_data_backup().name}", 0.01)
        elif choice == "6":
            if input("Restore latest backup [Y/N]? ").strip().upper() == "Y":
                archive = restore_latest_backup()
                ansi_scroll(
                    f"Restored {archive.name}; restart required." if archive else "No backup available.",
                    0.01,
                )
        elif choice == "7":
            text_page("sysop", "DYNAMIC EVENT MONITOR", cis_dynamic.event_monitor(sys.modules[__name__]))
            command = input("CANCEL n, ARCHIVE, REPAIR STATE, SET DATE/TIME, ADVANCE 1 DAY, PROCESS EVENTS, or M ! ").strip()
            if command.upper() != "M":
                ansi_scroll(cis_dynamic.manage_event(sys.modules[__name__], command), 0.01)
        elif choice == "8":
            command = input("ANN text, NOTE Handle text, or M ! ").strip()
            if command.upper() != "M":
                ansi_scroll(cis_dynamic.manage_content(sys.modules[__name__], command), 0.01)
        elif choice == "9":
            rows = list_sessions(BASE_DIR)
            lines = [f"{user:<10} {handle or '-':<16} {transport:<8} since {connected}" for _, user, handle, transport, connected in rows]
            text_page("sysop", "MEMBERS NOW ONLINE", lines or ["No members online."])
        elif choice == "10":
            state = cis_dynamic.load_state(sys.modules[__name__])
            controls = state.get("world_controls", {})
            text_page("sysop", "SIMULATION WORLD CONTROLS", [f"{key.upper():<8} {value}" for key, value in sorted(controls.items())] or ["No special bulletins active."])
            command = input("MARKET/WEATHER/TRAVEL/STORE text, CLEAR name, or M ! ").strip()
            if command.upper() != "M":
                ansi_scroll(cis_dynamic.manage_world(sys.modules[__name__], command), 0.01)
        elif choice == "11":
            sysop_announcements()


def sysop_announcements():
    while True:
        records = cis_announcements.all_records(sys.modules[__name__])
        clear()
        header_bar("sysop")
        ansi_scroll("SYSTEM ANNOUNCEMENTS", 0.01)
        for record in records:
            status = "EXPIRED" if record.get("expired") else "ACTIVE"
            ansi_scroll(f'{record["id"]:>3} {record.get("priority", "NORMAL"):<9} {status:<7} {record.get("target", "ALL"):<10} {record.get("title")}', 0.005)
        command = input("N New, X number expire, or M ! ").strip().upper()
        if command == "M":
            return
        if command.startswith("X ") and command[2:].strip().isdigit():
            changed = cis_announcements.expire(sys.modules[__name__], int(command[2:].strip()))
            ansi_scroll("Announcement expired." if changed else "Announcement not found.", 0.01)
            continue
        if command == "N":
            title = input("Title: ").strip()
            priority = input("Priority [NORMAL/IMPORTANT/EMERGENCY]: ").strip() or "NORMAL"
            target = input("Target [ALL or User ID]: ").strip() or "ALL"
            starts = input("Starts [NOW or MM/DD/YY]: ").strip() or "NOW"
            expires = input("Expires [NONE or MM/DD/YY]: ").strip() or "NONE"
            body = line_editor()
            if not body:
                continue
            try:
                record = cis_announcements.create(sys.modules[__name__], title, body, priority, target, starts, expires)
                ansi_scroll(f'Announcement #{record["id"]} posted.', 0.01)
            except ValueError as exc:
                ansi_scroll(str(exc), 0.01)


def sysop_accounts():
    while True:
        clear()
        header_bar("sysop")
        for user_id, role, state in account_rows(profiles):
            ansi_scroll(f"{user_id}  {role:<6}  {state}", 0.005)
        command = input("U unlock, D enable/disable, P reset password, or M ! ").strip().upper()
        if command == "M":
            return
        if command.startswith("U "):
            ansi_scroll("Account unlocked." if unlock_account(profiles, command[2:].strip()) else "User ID not found.", 0.01)
            save_profiles()
        elif command.startswith("D "):
            state = toggle_disabled(profiles, command[2:].strip())
            ansi_scroll("User ID not found." if state is None else f'Account {"disabled" if state else "enabled"}.', 0.01)
            save_profiles()
        elif command.startswith("P "):
            ansi_scroll(
                "Password reset; member will establish a new one at login."
                if reset_password(profiles, command[2:].strip()) else "User ID not found.",
                0.01,
            )
            save_profiles()


def sysop_uploads():
    pending = pending_uploads(library_files)
    clear()
    header_bar("sysop")
    if not pending:
        ansi_scroll("No uploads are awaiting approval.", 0.01)
        input("Press RETURN ! ")
        return
    for section, file in pending:
        ansi_scroll(f'{file["number"]} {file["name"]} {file["bytes"]} bytes {section}', 0.005)
        ansi_scroll(f'   {file["description"]}', 0.005)
    command = input("A number approve, R number reject, or M ! ").strip().upper()
    if len(command) > 2 and command[2:].isdigit() and command[0] in ("A", "R"):
        status = "approved" if command[0] == "A" else "rejected"
        if set_upload_status(library_files, int(command[2:]), status):
            save_json_atomic("library_files.json", library_files)
            ansi_scroll(f"Upload {status}.", 0.01)


def sysop_review_data():
    feedback = load_json("feedback.json", default=[])
    orders = load_json("orders.json", default=[])
    lines = ["FEEDBACK"]
    lines.extend(f'{item.get("user_id")}: {item.get("message")}' for item in feedback)
    lines.append("")
    lines.append("ORDERS")
    lines.extend(f'{item.get("user_id")}: {item.get("number")} {item.get("name")}' for item in orders)
    text_page("sysop", "CUSTOMER SERVICE REVIEW", lines or ["No records."])


COMMAND_HELP_LINES = [
        "T          TOP menu page",
        "M          Previous MENU",
        "G name     GO directly to a service or page",
        "GO TOP     Return to the main service menu",
        "GO BACK    Return to the previous menu",
        "GO RECENT  Select one of your last 10 destinations",
        "GO MAIL / FORUMS / CB / NEWS",
        "GO FINANCE / TRAVEL / REFERENCE / SHOP / GAMES / SUPPORT",
        "GO NEW     Display new activity across services",
        "GO PROFILE Display personal activity, orders, and reservations",
        "GO CALENDAR Display pending events and dated personal items",
        "GO NOTEBOOK List persistent personal notes",
        "GO DOWNLOADS List generated packets and downloaded files",
        "GO ACHIEVEMENTS Display service milestones",
        "GO DRAFTS  Preview, resume, or delete saved drafts",
        "GO TIMELINE Browse curated December 1988 history",
        "GO FEATURES Read curated multi-day historical stories",
        "GO MAGAZINE Read Online Weekly and download back issues",
        "GO CASE     Investigate the active cross-service special report",
        "GO PEOPLE   View persistent simulated-member relationships",
        "GO EQUIPMENT View owned catalog products and support cases",
        "GO SHAREWARE Follow the TERMLINK Forum and Data Library project",
        "GO SYSOP   Open maintenance console (SysOp accounts only)",
        "H          HELP",
        "R          RESEND the current page",
        "F          FORWARD one page",
        "B          BACK one page",
        "N          NEXT menu item",
        "P          PREVIOUS menu item",
        "S n        SELECT menu item n",
        "FIND words Search all indexed services",
        "NOTE text  Save a note from the current service",
        "NOTE title | text  Save a titled personal note",
        "CAPTURE ON Save displayed text for offline reading",
        "CAPTURE OFF Close the current capture file",
        "BACKUP     Save mutable service data",
        "RESTORE    Restore the newest backup archive",
        "VERSION    Display simulation release",
        "STATUS     Display current session settings",
        "DIAG       Check local data health",
        "OFF or BYE Log off CompuServe",
        "CTRL-S pauses output; CTRL-Q resumes it.",
]

SERVICE_HELP = {
    "finance": ["FINANCE COMMANDS", "MicroQuote: LIST, WATCH symbol, MY, REMOVE symbol", "MicroQuote: BUY, SELL, LIMIT, ORDERS, PORT, HISTORY, M", "Portfolio Center: H history, D download", "All trading, balances, and quotations are fictional."],
    "travel": ["TRAVEL COMMANDS", "Use three-letter airport codes in the Airline Guide.", "Trip Folder: D download, P preferences, B rebook", "Weather Operations: FLIGHT, RAIL, HOTEL, STANDBY, CANCEL", "Reservations: CANCEL RES confirmation from GO PROFILE", "All schedules, fares, and reservations are fictional."],
    "shopping": ["SHOPPING COMMANDS", "Catalog: item number, F/B, C category, S search", "Catalog: D deals, K compatibility, A/V/R/O, M", "Owned Equipment: INSTALL, WARRANTY, RETURN, REVIEW, SELL", "Orders: CANCEL ORDER number from GO PROFILE"],
    "reference": ["REFERENCE COMMANDS", "Words or Boolean AND/OR/NOT; B browse; SUBJECTS", "HISTORY, RECALL n, CLEAR HISTORY, MARK id, MARKED, DOWNLOAD"],
    "forums": ["FORUM COMMANDS", "SELECT, READ, CHANGE, COMPOSE; search by number, FROM, or SUBJECT"],
    "cb": ["CB COMMANDS", "/WHO lists handles; /HELP shows help; /EXIT leaves channel"],
    "games": ["GAME COMMANDS", "Adventure: LOOK, directions, TAKE, INVENTORY, EXAMINE, USE", "MegaWars: FIRE, SCAN, JUMP, TRADE, REPAIR, STATUS, SAVE"],
    "support": ["PERSONAL TOOLS", "GO CALENDAR, GO NOTEBOOK, GO DOWNLOADS, GO ACHIEVEMENTS", "NOTE title | text saves a note from any service."],
}

HELP_TOPICS = {
    "TRADING": SERVICE_HELP["finance"], "FINANCE": SERVICE_HELP["finance"],
    "TRAVEL": SERVICE_HELP["travel"], "SHOPPING": SERVICE_HELP["shopping"], "STORE": SERVICE_HELP["shopping"],
    "REFERENCE": SERVICE_HELP["reference"], "FORUMS": SERVICE_HELP["forums"], "CB": SERVICE_HELP["cb"],
    "GAMES": SERVICE_HELP["games"], "DOWNLOADS": SERVICE_HELP["support"], "NOTEBOOK": SERVICE_HELP["support"],
}


def command_help(topic="", context="main", commands_only=False):
    topic = topic.strip().upper()
    if topic:
        matches = [lines for name, lines in HELP_TOPICS.items() if name.startswith(topic)]
        if len(matches) == 1:
            text_page("command", f"HELP {topic}", matches[0] + ["", "GLOBAL COMMANDS", *COMMAND_HELP_LINES])
        else:
            text_page("command", "HELP TOPICS", ["Topics: " + ", ".join(sorted(HELP_TOPICS)), "Enter HELP followed by one topic."])
        return
    local = SERVICE_HELP.get(context, [])
    title = "COMMANDS FOR THIS SERVICE" if commands_only else "COMPUSERVE COMMAND SUMMARY"
    text_page("command", title, [*local, *([""] if local else []), *COMMAND_HELP_LINES])


def version_screen():
    text_page("command", RELEASE_NAME, [
        f"Version {VERSION}", f"Data schema {CURRENT_SCHEMA_VERSION}",
        "Independent historical simulation -- not an online service.",
    ])


def status_screen():
    backup_dir = BASE_DIR / "backups"
    backups = len(list(backup_dir.glob("CIS-*.db"))) if backup_dir.exists() else 0
    text_page("command", "SESSION STATUS", [
        f"User ID: {current_user_id or 'Not logged in'}",
        f"Baud: {connection_baud}", f"Columns: {SCREEN_WIDTH}",
        f'Display: {current_profile.get("display_mode", startup_options["display_mode"])}',
        f'Fast mode: {"ON" if startup_options.get("fast_mode") else "OFF"}',
        f'Capture: {capture_path.name if capture_path else "OFF"}',
        f"Backup archives: {backups}",
    ])


def diagnostics_screen():
    failures = []
    checked = 0
    for path in BASE_DIR.glob("*.json"):
        try:
            storage_load_json(BASE_DIR, path.name)
            checked += 1
        except RuntimeError as exc:
            failures.append(str(exc))
    news = load_json("news.json", default={}).get("_meta", {})
    database = database_status(BASE_DIR)
    dynamic_issues = cis_dynamic.validate_state(sys.modules[__name__])
    lines = [
        f"Release: {VERSION}", f"Schema: {CURRENT_SCHEMA_VERSION}",
        f"Static JSON files checked: {checked}",
        f"News updated: {news.get('updated', 'not recorded')}",
        f"SQLite integrity: {database['integrity'].upper()}",
        f"Database schema: {database['schema']}",
        f"Database size: {database['bytes']} bytes",
        f"Dynamic record issues: {len(dynamic_issues)}",
    ]
    lines.extend(f"ERROR: {failure}" for failure in failures)
    lines.append("DATA CHECK PASSED" if not failures else "DATA CHECK FAILED")
    text_page("command", "LOCAL DIAGNOSTICS", lines)


def line_editor(initial_lines=None, on_change=None):
    lines = list(initial_lines or [])
    ansi_scroll("LINEDIT -- enter text one line at a time.", 0.01)
    ansi_scroll("Commands: LIST, DELETE n, REPLACE n text, SAVE, ABORT", 0.01)
    while True:
        entry = input(f"{len(lines) + 1}: ")
        command = entry.strip()
        upper = command.upper()
        if upper == "SAVE":
            return "\n".join(lines) if lines else None
        if upper == "ABORT":
            return None
        if upper == "LIST":
            for number, line in enumerate(lines, 1):
                ansi_scroll(f"{number:>3} {line}", 0.005)
            continue
        if upper.startswith("DELETE ") and upper[7:].isdigit():
            number = int(upper[7:])
            if 1 <= number <= len(lines):
                lines.pop(number - 1)
                if on_change:
                    on_change(list(lines))
            continue
        if upper.startswith("REPLACE "):
            parts = command.split(maxsplit=2)
            if len(parts) == 3 and parts[1].isdigit():
                number = int(parts[1])
                if 1 <= number <= len(lines):
                    lines[number - 1] = parts[2]
                    if on_change:
                        on_change(list(lines))
            continue
        if command:
            lines.append(command[:SCREEN_WIDTH])
            if on_change:
                on_change(list(lines))


def load_mail():
    return cis_mail.load_mail(sys.modules[__name__])


def mail_waiting_count(user_id):
    return cis_mail.waiting_count(sys.modules[__name__], user_id)


def mail_service(choice):
    return cis_mail.service(sys.modules[__name__], choice)


def mail_read():
    return cis_mail.read(sys.modules[__name__])


def mail_message_list(folder, all_messages, title, sent_folder=False):
    return cis_mail.message_list(sys.modules[__name__], folder, all_messages, title, sent_folder)


def mail_compose(recipient=None, subject_default="", initial_lines=None, resume_saved=False):
    return cis_mail.compose(sys.modules[__name__], recipient, subject_default, initial_lines, resume_saved)


def mail_folders():
    return cis_mail.folders(sys.modules[__name__])


def mail_settings():
    return cis_mail.settings(sys.modules[__name__])

# --- Forum Section -----------------------------------------------------------

def forum_service(forum_id):
    forum = FORUM_CATALOG[forum_id]
    joined = forum_id in current_profile.get("joined_forums", [])
    while True:
        clear()
        header_bar(forum_id)
        ansi_scroll(forum["title"], 0.01)
        ansi_scroll("Forum Functions", 0.01)
        ansi_scroll("1  Messages", 0.01)
        ansi_scroll("2  Libraries", 0.01)
        ansi_scroll("3  Conferencing", 0.01)
        ansi_scroll("4  Announcements", 0.01)
        ansi_scroll("5  Member directory", 0.01)
        ansi_scroll("6  Options", 0.01)
        ansi_scroll("7  Instructions", 0.01)
        ansi_scroll("8  JOIN this Forum" if not joined else "8  Membership active", 0.01)
        ansi_scroll("M  Return to Forums Directory", 0.01)
        choice = input("Enter choice ! ").strip().upper()
        if choice == "M":
            return
        if choice in ("1", "MES", "MESSAGES"):
            forum_messages_menu(forum_id)
        elif choice in ("2", "LIB", "LIBRARIES"):
            forum_libraries(forum_id)
        elif choice in ("3", "CON", "CONFERENCING"):
            forum_conference(forum_id)
        elif choice in ("4", "ANN", "ANNOUNCEMENTS"):
            forum_announcements(forum_id)
        elif choice in ("5", "MEM", "MEMBERS"):
            forum_members(forum_id)
        elif choice in ("6", "OPT", "OPTIONS"):
            forum_options()
        elif choice in ("7", "INS", "INSTRUCTIONS", "H", "HELP"):
            forum_instructions()
        elif choice in ("8", "JOIN"):
            memberships = current_profile.setdefault("joined_forums", [])
            if forum_id not in memberships:
                memberships.append(forum_id)
                save_profiles()
            joined = True
            ansi_scroll("Forum membership activated.", 0.01)


def forum_messages_menu(forum_id):
    forum = FORUM_CATALOG[forum_id]
    while True:
        clear()
        header_bar(forum_id)
        age = current_profile.get("message_age", "New")
        ansi_scroll(f'{forum["title"]} Messages Menu', 0.01)
        ansi_scroll(f"Message age selection = [{age}]", 0.01)
        ansi_scroll("1  SELECT (Read by section and subject)", 0.01)
        ansi_scroll("2  READ or search messages", 0.01)
        ansi_scroll("3  CHANGE age selection", 0.01)
        ansi_scroll("4  COMPOSE a message", 0.01)
        ansi_scroll("M  Return to Forum Functions", 0.01)
        choice = input("Enter choice ! ").strip().upper()
        if choice == "M":
            return
        if choice in ("1", "SEL", "SELECT"):
            forum_select_section(forum_id)
        elif choice in ("2", "REA", "READ"):
            forum_read_search(forum_id)
        elif choice in ("3", "CHA", "CHANGE"):
            current_profile["message_age"] = "All" if age == "New" else "New"
            save_profiles()
        elif choice in ("4", "COM", "COMPOSE"):
            forum_compose(forum_id)


def forum_select_section(forum_id):
    forum = FORUM_CATALOG[forum_id]
    clear()
    header_bar(forum_id)
    ansi_scroll("Select section", 0.01)
    for number, (_, title) in forum["sections"].items():
        ansi_scroll(f"{number}  {title}", 0.01)
    choice = input("Enter choice ! ").strip()
    target = forum["sections"].get(choice)
    if target:
        forum_section(target[0], f'{forum["title"]} - {target[1]}')


def forum_read_search(forum_id):
    forum = FORUM_CATALOG[forum_id]
    query = input("NUMBER, FROM name, or SUBJECT words: ").strip().lower()
    matches = []
    for section_key, _ in forum["sections"].values():
        for message in forum_threads.get(section_key, []):
            if query.isdigit() and str(message.get("id")) == query:
                matches.append((section_key, message))
            elif query.startswith("from ") and query[5:] in message.get("author", "").lower():
                matches.append((section_key, message))
            elif query.startswith("subject ") and query[8:] in message.get("subject", "").lower():
                matches.append((section_key, message))
            elif query and not query.startswith(("from ", "subject ")) and query in message.get("subject", "").lower():
                matches.append((section_key, message))
    if not matches:
        ansi_scroll("No messages found.", 0.01)
        input("Press RETURN ! ")
        return
    for section_key, message in matches:
        text_page(forum_id, f'Message #{message["id"]}  {message["date"]}', [
            f'From: {message["author"]}', f'Subject: {message["subject"]}', "", message["body"]
        ])
        forum_message_actions(section_key, message)


def forum_compose(forum_id):
    forum = FORUM_CATALOG[forum_id]
    draft = cis_drafts.get_draft(sys.modules[__name__], "forum")
    if draft:
        ansi_scroll("SAVED DRAFT: " + cis_drafts.draft_summary(draft), 0.01)
        action = input("R Resume, D Delete, N New, or M ! ").strip().upper()
        if action == "M":
            return
        if action == "D":
            cis_drafts.delete_draft(sys.modules[__name__], "forum")
            ansi_scroll("Forum draft deleted.", 0.01)
            return
        if action == "R":
            section_key = draft.get("section")
            if section_key not in {key for key, _ in forum["sections"].values()}:
                ansi_scroll("The saved draft belongs to another Forum.", 0.01)
                return
            subject = draft.get("subject", "")
            initial_lines = draft.get("lines", [])
            body = line_editor(initial_lines, on_change=lambda lines: cis_drafts.save_draft(sys.modules[__name__], "forum", forum=forum_id, section=section_key, subject=subject, lines=lines))
            if body:
                forum_post(section_key, subject, body)
                cis_drafts.delete_draft(sys.modules[__name__], "forum")
            return
    clear()
    for number, (_, title) in forum["sections"].items():
        ansi_scroll(f"{number}  {title}", 0.01)
    choice = input("Section: ").strip()
    target = forum["sections"].get(choice)
    if not target:
        return
    subject = input("Subject: ").strip()[:120]
    if not subject:
        return
    cis_drafts.save_draft(sys.modules[__name__], "forum", forum=forum_id, section=target[0], subject=subject, lines=[])
    body = line_editor(on_change=lambda lines: cis_drafts.save_draft(sys.modules[__name__], "forum", forum=forum_id, section=target[0], subject=subject, lines=lines))
    if not subject or not body:
        return
    forum_post(target[0], subject, body)
    cis_drafts.delete_draft(sys.modules[__name__], "forum")


def resume_draft_record(draft):
    if draft.get("service") == "mail":
        mail_compose(resume_saved=True)
        return
    if draft.get("service") == "forum":
        section = draft.get("section")
        subject = draft.get("subject", "")
        parent_id = draft.get("parent_id")
        body = line_editor(draft.get("lines", []), on_change=lambda lines: cis_drafts.save_draft(sys.modules[__name__], "forum", section=section, subject=subject, parent_id=parent_id, lines=lines))
        if body and section in forum_threads:
            forum_post(section, subject, body, parent_id=parent_id)
            cis_drafts.delete_draft(sys.modules[__name__], "forum")


def draft_center():
    while True:
        drafts = cis_drafts.list_drafts(sys.modules[__name__])
        clear()
        header_bar("support")
        ansi_scroll("PERSONAL DRAFT CENTER", 0.01)
        for index, draft in enumerate(drafts, 1):
            ansi_scroll(f"{index:>2}  {cis_drafts.draft_summary(draft)}", 0.005)
            ansi_scroll(f'    Updated {draft.get("updated_at", "")}  {len(draft.get("lines", []))} line(s)', 0.005)
        if not drafts:
            ansi_scroll("No saved drafts.", 0.01)
        command = input("R number resume, V number view, D number delete, or M ! ").strip().upper()
        if command == "M":
            return
        parts = command.split()
        if len(parts) != 2 or parts[0] not in ("R", "V", "D") or not parts[1].isdigit() or not 1 <= int(parts[1]) <= len(drafts):
            continue
        draft = drafts[int(parts[1]) - 1]
        if parts[0] == "R":
            resume_draft_record(draft)
        elif parts[0] == "V":
            text_page("support", "DRAFT PREVIEW", [cis_drafts.draft_summary(draft), f'Updated: {draft.get("updated_at", "")}', "", *draft.get("lines", [])])
        elif input("Delete this draft [Y/N]? ").strip().upper() == "Y":
            cis_drafts.delete_draft(sys.modules[__name__], draft["service"])
            ansi_scroll("Draft deleted.", 0.01)


def forum_post(section_key, subject, body, parent_id=None):
    return cis_forums.post(sys.modules[__name__], section_key, subject, body, parent_id)


def forum_message_actions(section_key, message):
    if message.get("story_case") == cis_story.CASE_ID and current_user_id:
        cis_story._mark(sys.modules[__name__], "FORUM")
    return cis_forums.message_actions(sys.modules[__name__], section_key, message)


def forum_libraries(forum_id):
    if forum_id in cis_communities.LIBRARIES:
        library_download_screen(cis_communities.LIBRARIES[forum_id])
    elif forum_id == "ibmhw":
        while True:
            clear()
            header_bar("ibmhw_libs")
            ansi_scroll("IBMHW Data Libraries", 0.01)
            for number, target in OPTION_TARGETS["ibmhw_libs"].items():
                ansi_scroll(f'{number}  {screens[target]["title"]}', 0.01)
            choice = input("Enter choice or M ! ").strip().upper()
            if choice == "M":
                return
            target = OPTION_TARGETS["ibmhw_libs"].get(choice)
            if target:
                library_download_screen(target)
    else:
        text_page(forum_id, "Forum Data Libraries", [
            "1  START.TXT   New member information",
            "2  INDEX.TXT   Library file index",
            "3  FAQ.TXT     Frequently asked questions",
            "Use the IBMHW Forum for simulated file downloads.",
        ])


def forum_conference(forum_id):
    forum = FORUM_CATALOG[forum_id]
    topic, status = cis_dynamic.conference_schedule(forum_id)
    transcript = []
    counter = 0
    room = f"conference:{forum_id}"
    last_message_id = 0
    clear()
    header_bar(forum_id)
    ansi_scroll(f'{forum["title"]} Conference', 0.01)
    ansi_scroll(f"Topic: {topic}", 0.01)
    ansi_scroll(f"Status: {status}. Type /EXIT to leave.", 0.01)
    while True:
        shared = read_live_messages(BASE_DIR, room, last_message_id)
        for message_id, speaker, body, _ in shared:
            last_message_id = message_id
            line = f"{speaker}: {body}"
            transcript.append(line)
            ansi_scroll(line, 0.005)
        speaker, remark = cis_dynamic.conference_remark(forum_id, counter)
        counter += 1
        transcript.append(f"{speaker}: {remark}")
        ansi_scroll(transcript[-1], 0.005)
        message = input(": ").strip()
        if message.upper() == "/EXIT":
            if transcript:
                section_key = next(iter(forum["sections"].values()))[0]
                forum_post(section_key, f"CONFERENCE TRANSCRIPT: {topic}", "\n".join(transcript))
            return
        if message:
            line = f"{current_handle or current_user_id}: {message}"
            transcript.append(line)
            last_message_id = post_live_message(BASE_DIR, room, current_handle or current_user_id, message)
            ansi_scroll(line, 0.005)


def forum_announcements(forum_id):
    forum = FORUM_CATALOG[forum_id]
    lines = ["SYSOP BULLETIN", f'Welcome to the {forum["title"]}.']
    for section_key, _ in forum["sections"].values():
        for message in forum_threads.get(section_key, []):
            if "announcement" in section_key or message.get("author") == "SYSOP":
                lines.extend(["", message["subject"], message["body"]])
    text_page(forum_id, "Forum Announcements", lines)


def forum_members(forum_id):
    members = sorted({
        message.get("author", "")
        for section_key, _ in FORUM_CATALOG[forum_id]["sections"].values()
        for message in forum_threads.get(section_key, [])
        if message.get("author")
    })
    text_page(forum_id, "Member Directory", [f"{n:>3}  {name}" for n, name in enumerate(members, 1)])


def forum_options():
    text_page("forums", "Forum Options", [
        f'Message age selection: {current_profile.get("message_age", "New")}',
        f"Terminal width: {SCREEN_WIDTH}",
        f"Connection speed: {connection_baud} baud",
        "Use CHANGE in the Messages menu to alter message age.",
    ])


def forum_instructions():
    text_page("forums", "Forum Instructions", [
        "MES  Messages", "LIB  Libraries", "CON  Conferencing",
        "ANN  Announcements", "MEM  Member directory", "OPT  Options",
        "JOIN Join this Forum", "M    Previous menu",
        "In Messages use SEL, REA, CHA, and COM.",
    ])

def forum_section(section_key, title):
    threads = forum_threads.get(section_key, [])
    while True:
        clear()
        header_bar(section_key)  # NEW
        ansi_scroll(title, 0.01)
        ansi_scroll("-" * len(title), 0.01)
        if not threads:
            ansi_scroll("No messages in this section.\n", 0.01)
        else:
            last_read = current_profile.get("forum_last_read", {}).get(section_key, 0)
            for idx, msg in enumerate(threads, start=1):
                marker = "*" if msg["id"] > last_read else " "
                thread_mark = f" RE #{msg['parent_id']}" if msg.get("parent_id") else ""
                line = f"{idx}){marker} #{msg['id']}{thread_mark}  {msg['date']}  {msg['author']}\nSubject: {msg['subject']}"
                ansi_scroll(line, 0.005)
        ansi_scroll("\nSelect message, T number for thread, U number to unwatch, or M.\n", 0.01)
        #choice = input("> ").strip()
        choice = input(cis_prompt("forums") + " ").strip()

        if choice.upper() == "M" or choice == "0":
            break
        if choice.upper().startswith("T ") and choice[2:].strip().isdigit():
            selected_number = int(choice[2:].strip())
            if 1 <= selected_number <= len(threads):
                text_page(section_key, "MESSAGE THREAD", cis_forums.thread_lines(threads, threads[selected_number - 1]["id"]))
            continue
        if choice.upper().startswith("U ") and choice[2:].strip().isdigit():
            selected_number = int(choice[2:].strip())
            if 1 <= selected_number <= len(threads):
                ansi_scroll(cis_forums.set_watch(sys.modules[__name__], threads[selected_number - 1]["id"], False), 0.01)
            continue
        try:
            num = int(choice)
        except ValueError:
            ansi_scroll("\nInvalid selection.\n", 0.01)
            time.sleep(0.5)
            continue
        if 1 <= num <= len(threads):
            msg = threads[num - 1]
            clear()
            header = f"Message #{msg['id']}  {msg['date']}  {msg['author']}"
            ansi_scroll(header, 0.01)
            ansi_scroll("Subject: " + msg['subject'], 0.01)
            ansi_scroll("-" * len(header), 0.01)
            ansi_scroll(msg['body'], 0.01)
            reads = current_profile.setdefault("forum_last_read", {})
            reads[section_key] = max(reads.get(section_key, 0), msg["id"])
            save_profiles()
            forum_message_actions(section_key, msg)
        else:
            ansi_scroll("\nInvalid message number.\n", 0.01)
            time.sleep(0.5)

# --- Library Download Simulation --------------------------------------------

def library_download_screen(screen_key):
    screen = screens[screen_key]
    files = library_files.get(screen_key, [])
    while True:
        clear()
        header_bar(screen_key)  # NEW
        ansi_scroll(screen["title"], 0.01)
        ansi_scroll("-" * len(screen["title"]), 0.01)
        visible_files = [file for file in files if file.get("status", "approved") == "approved"]
        popular = sorted(visible_files, key=lambda item: item.get("downloads", 0), reverse=True)[:3]
        if popular:
            ansi_scroll("MOST ACCESSED: " + ", ".join(file["name"] for file in popular), 0.005)
        for file in visible_files:
            ansi_scroll(
                f'{file["number"]:>4} {file["name"]:<12} {file["bytes"]:>7} bytes  {file["date"]}',
                0.005,
            )
            ansi_scroll(f'     {file["description"]}  ({file["downloads"]} accesses)', 0.005)
        ansi_scroll("\nM  Return to previous menu\n", 0.01)
        ansi_scroll("U  Upload a file", 0.01)
        ansi_scroll("I number  File notes, versions and member reviews", 0.01)
        choice = input("File number, I number, U, or M ! ").strip()

        if choice.upper() == "M" or choice == "0":
            break
        if choice.upper() == "U":
            library_upload(screen_key)
            continue
        if choice.upper().startswith('I '):
            selected = next((file for file in visible_files if str(file['number']) == choice[2:].strip()), None)
            if selected:
                text_page(screen_key, selected['name'], cis_communities.detail_lines(selected))
            else:
                ansi_scroll('File not found.', 0.01)
            continue
        selected = next((file for file in visible_files if str(file["number"]) == choice), None)
        if selected:
            library_transfer(selected)
        else:
            ansi_scroll("Huh", 0.01)
            time.sleep(0.3)


def library_transfer(file):
    ansi_scroll(f'File: {file["name"]}  Size: {file["bytes"]} bytes', 0.01)
    protocol = input("Protocol: B (CompuServe B) or X (XMODEM) ! ").strip().upper()
    if protocol not in ("B", "X"):
        ansi_scroll("Transfer cancelled.", 0.01)
        return
    block_size = 512 if protocol == "B" else 128
    blocks = (file["bytes"] + block_size - 1) // block_size
    name = "CompuServe B" if protocol == "B" else "XMODEM"
    ansi_scroll(f"Beginning {name} transfer...", 0.01)
    for completed in range(0, blocks, max(1, blocks // 10)):
        ansi_scroll(f"Block {min(completed + 1, blocks):>4} of {blocks}", 0.001)
    destination = cis_library.materialize_download(sys.modules[__name__], file, protocol)
    ansi_scroll(f"Transfer complete -- {destination.stat().st_size} bytes received.", 0.01)
    ansi_scroll(f"Stored as {destination}", 0.01)


def library_upload(screen_key):
    source_text = input("Local file path: ").strip().strip('"')
    if not source_text:
        return
    source = Path(source_text).expanduser().resolve()
    if not source.is_file():
        ansi_scroll("File not found.", 0.01)
        return
    if source.stat().st_size > 1024 * 1024:
        ansi_scroll("Upload exceeds the 1 MiB simulation limit.", 0.01)
        return
    description = input("Description: ").strip()[:240]
    if not description:
        ansi_scroll("Upload cancelled; a description is required.", 0.01)
        return
    upload_dir = BASE_DIR / "uploads"
    upload_dir.mkdir(exist_ok=True)
    destination = upload_dir / source.name
    if destination.exists():
        ansi_scroll("A file with that name is already awaiting approval.", 0.01)
        return
    shutil.copy2(source, destination)
    numbers = [file["number"] for files in library_files.values() for file in files]
    record = {
        "number": max(numbers, default=100) + 1, "name": source.name.upper()[:12],
        "bytes": destination.stat().st_size, "date": SIMULATION_DATE,
        "downloads": 0, "description": description,
        "stored_path": str(destination.relative_to(BASE_DIR)), "status": "pending",
    }
    library_files.setdefault(screen_key, []).append(record)
    save_json_atomic("library_files.json", library_files)
    ansi_scroll(f'Upload #{record["number"]} is pending SysOp approval.', 0.01)


def news_section(category):
    news_data = load_json("news.json", default={})
    articles = news_data.get(category, [])
    metadata = news_data.get("_meta", {})
    page_size = 16
    page = 0
    while True:
        clear()
        header_bar("news")
        ansi_scroll(f"NEWS WIRE - {category.upper()}", 0.01)
        ansi_scroll("Current dispatches", 0.01)
        if metadata.get("updated"):
            ansi_scroll(f'Wire updated: {metadata["updated"]}', 0.005)
        if metadata.get("sources"):
            ansi_scroll("Sources: " + ", ".join(metadata["sources"]), 0.005)
        if not articles:
            ansi_scroll("No current dispatches. Run news_feed.py to update the wire.", 0.01)
            input("!")
            return
        start = page * page_size
        visible = articles[start:start + page_size]
        for index, article in enumerate(visible, start=start + 1):
            title = article.get("title") or "UNTITLED"
            ansi_scroll(f"{index:>2} {title}", 0.005)
        ansi_scroll("\nEnter item, F, B, H, or M", 0.01)
        choice = input("! ").strip().upper()
        if choice == "M":
            return
        if choice in ("H", "HELP"):
            text_page("news", "NEWS WIRE HELP", [
                "Enter a number to read a dispatch.",
                "F  Forward one headline page",
                "B  Back one headline page",
                "R  Resend this page",
                "M  Return to the News menu",
            ])
        elif choice == "F" and start + page_size < len(articles):
            page += 1
        elif choice == "B" and page > 0:
            page -= 1
        elif choice.isdigit() and 1 <= int(choice) <= len(articles):
            news_article(articles[int(choice) - 1], category)
        elif choice not in ("R", ""):
            ansi_scroll("Huh?", 0.01)


def news_article(article, category):
    title = article.get("title") or "UNTITLED"
    published = article.get("published") or "TIME NOT GIVEN"
    body = re.sub(r"<[^>]+>", " ", article.get("summary") or "No text supplied by wire source.")
    if article.get("story_case") == cis_story.CASE_ID and current_user_id:
        cis_story._mark(sys.modules[__name__], "NEWS")
    lines = []
    for paragraph in body.splitlines() or [body]:
        lines.extend(textwrap.wrap(" ".join(paragraph.split()), width=76) or [""])
    page_size = 16
    page = 0
    while True:
        clear()
        header_bar("news")
        ansi_scroll(f"{category.upper()} NEWS", 0.01)
        ansi_scroll(title.upper(), 0.01)
        ansi_scroll(published, 0.005)
        ansi_scroll("Source: " + article.get("source", "Current News Wire"), 0.005)
        background = cis_reference.suggest_records(f"{title} {body}", 1)
        if background:
            ansi_scroll(f'Background: {background[0][1][0]} {background[0][1][1]}', 0.005)
        ansi_scroll("", 0.001)
        for line in lines[page * page_size:(page + 1) * page_size]:
            ansi_scroll(line, 0.005)
        ansi_scroll("\nF Forward  B Back  R Resend  M Headlines", 0.01)
        choice = input("! ").strip().upper()
        if choice in ("M", ""):
            return
        if choice == "F" and (page + 1) * page_size < len(lines):
            page += 1
        elif choice == "B" and page > 0:
            page -= 1
        elif choice not in ("R", "H"):
            ansi_scroll("Huh?", 0.01)


def period_news_edition():
    articles = cis_period_news.edition(sys.modules[__name__])
    if current_user_id and cis_dynamic.simulation_day().day >= 12:
        story_article = cis_story.news_article(sys.modules[__name__])
        story_article["story_case"] = cis_story.CASE_ID
        articles = [story_article, *articles]
    while True:
        clear()
        header_bar("news")
        ansi_scroll("CIS PERIOD NEWS WIRE - DECEMBER 1988", 0.01)
        ansi_scroll("A historical simulation edition; all dispatches remain within 1988.", 0.005)
        for index, article in enumerate(articles, 1):
            ansi_scroll(f'{index:>2} [{article["category"][:3]}] {article["title"]}', 0.005)
        choice = input("\nEnter item or M ! ").strip().upper()
        if choice == "M":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(articles):
            article = articles[int(choice) - 1]
            news_article(article, article["category"])


def refresh_current_news():
    return cis_news.refresh(sys.modules[__name__])


def text_page(screen_key, title, lines):
    clear()
    header_bar(screen_key)
    ansi_scroll(title, 0.01)
    ansi_scroll("-" * len(title), 0.01)
    for line in lines:
        ansi_scroll(line, 0.005)
    ansi_scroll("\nPress ENTER to return.", 0.01)
    input()


def cb_help():
    text_page("cbhelp", "CB SIMULATOR INSTRUCTIONS", [
        "Type a line and press RETURN to transmit to the current channel.",
        "/WHO                 List members and status on this channel",
        "/CHANNELS            Display public and member-created channels",
        "/JOIN name           Move to or create a channel",
        "/MSG handle text     Store a private message",
        "/IGNORE handle       Toggle messages from a handle",
        "/INFO handle         Show a simulated member profile",
        "/STATUS AVAILABLE    Set AVAILABLE, AWAY, or BUSY",
        "/EXIT                Leave CB",
        "The most recent 20 channel messages are retained as scrollback.",
        "Do not reveal passwords or private information.",
    ])


def customer_support(choice):
    if choice == "1":
        text_page("support", "CUSTOMER SERVICE - HELP DESK", [
            "GO <name>  Go directly to a service",
            "M          Return to the previous menu",
            "0          Return to the previous menu",
            "GO TOP     Return to the top menu",
            "GO COMMAND Display command information",
            "For forum help, select Instructions or Rules.",
            "Enter ? for contextual help or HELP topic for detailed help.",
            "Enter COMMANDS to list actions for the current service.",
        ])
        if input("D to prepare ASCII command card, or RETURN ! ").strip().upper() == "D":
            card = cis_experience.export_command_card(sys.modules[__name__])
            ansi_scroll(f"Command card prepared: {card.name}", 0.01)
    elif choice == "2":
        seconds = get_elapsed_seconds()
        text_page("support", "BILLING INFORMATION", [
            f"Current connect rate: ${connection_rate_per_hour():.2f} per hour",
            "Rate period: PRIME" if is_prime_time() else "Rate period: STANDARD",
            f"Connect time: {format_elapsed(seconds)}",
            f"Estimated connect charges: ${get_estimated_cost(seconds):.2f}",
            f"Premium service charges: ${premium_charges:.2f}",
            "Premium services may carry additional charges.",
            "Telephone toll charges are not included.",
        ])
    elif choice == "3":
        text_page("support", "TERMINAL AND ACCESS HELP", [
            "1 Check terminal setting: full duplex",
            "2 Use 7 data bits, even parity, 1 stop bit",
            "3 If characters are garbled, check baud rate",
            "4 If connection drops, redial your access number",
            "5 Capture long instructions for offline reading",
        ])
        terminal_settings()
    elif choice == "4":
        clear()
        header_bar("support")
        ansi_scroll("FEEDBACK TO CUSTOMER SERVICE", 0.01)
        ansi_scroll("Enter one line (blank line cancels).", 0.01)
        message = input("Feedback: ").strip()
        if message:
            feedback = load_json("feedback.json", default=[])
            if not isinstance(feedback, list):
                raise RuntimeError("feedback.json must contain a JSON list")
            feedback.append({
                "user_id": current_user_id,
                "submitted": datetime.now().isoformat(timespec="seconds"),
                "message": message[:2000],
            })
            save_json_atomic("feedback.json", feedback)
            ansi_scroll("Thank you. Your feedback has been recorded.", 0.01)
            time.sleep(1)
    elif choice == "5":
        account_settings()
    elif choice == "6":
        text_page("support", "PERSONAL SIMULATION CALENDAR", cis_experience.calendar_lines(sys.modules[__name__]))
    elif choice == "7":
        text_page("support", "PERSONAL NOTEBOOK", cis_experience.notebook_lines(sys.modules[__name__]))
        action = input("A add, R read, D delete, or RETURN ! ").strip().upper()
        if action == "A":
            title = input("Title: ").strip(); body = input("Note: ").strip()
            ansi_scroll(cis_experience.add_note(sys.modules[__name__], title, body), 0.01)
        elif action in ("R", "D"):
            number = input("Item number: ").strip().lstrip("#")
            if number.isdigit() and action == "R":
                text_page("support", "NOTEBOOK ITEM", cis_experience.read_note(sys.modules[__name__], int(number)))
            elif number.isdigit() and input("Delete this notebook item [Y/N]? ").strip().upper() == "Y":
                ansi_scroll(cis_experience.delete_note(sys.modules[__name__], int(number)), 0.01)
    elif choice == "8":
        text_page("support", "DOWNLOAD CENTER", cis_experience.download_lines(sys.modules[__name__]))
        folder = BASE_DIR / "downloads"
        files = sorted((path for path in folder.iterdir() if path.is_file()), key=lambda p: p.name.lower()) if folder.exists() else []
        action = input("R read, N rename, D delete, or RETURN ! ").strip().upper()
        if action in ("R", "N", "D"):
            number = input("File number: ").strip()
            if number.isdigit() and 1 <= int(number) <= len(files):
                path = files[int(number) - 1]
                if action == "R":
                    text_page("support", path.name, path.read_text(encoding="utf-8", errors="replace").splitlines()[:200])
                elif action == "N":
                    name = Path(input("New filename: ").strip()).name
                    if name and (folder / name).parent == folder:
                        path.rename(folder / name); ansi_scroll("File renamed.", 0.01)
                elif input(f"Delete {path.name} [Y/N]? ").strip().upper() == "Y":
                    path.unlink(); ansi_scroll("Downloaded file deleted; it cannot be recovered here.", 0.01)
    elif choice == "9":
        text_page("support", "MEMBER ACHIEVEMENTS", [*cis_experience.achievement_lines(sys.modules[__name__]), "", *cis_experience.session_cost_lines(sys.modules[__name__])])
    elif choice == "10":
        cis_experience.guided_tour(sys.modules[__name__])
    elif choice == "11":
        text_page("support", "MEMBER USAGE STATEMENT", cis_billing.statement_lines(sys.modules[__name__]))
        if input("D to download statement, or RETURN ! ").strip().upper() == "D":
            statement = cis_billing.export_statement(sys.modules[__name__])
            ansi_scroll(f"ASCII statement prepared: {statement.name}", 0.01)


def terminal_settings():
    global connection_baud, SCREEN_WIDTH
    ansi_scroll("Change settings or press RETURN to retain them.", 0.01)
    baud = input(f"Baud ({connection_baud}) [300/1200/2400]: ").strip()
    columns = input(f"Columns ({SCREEN_WIDTH}) [40/80]: ").strip()
    mode = input(
        f'Display ({current_profile.get("display_mode", "scroll")}) [scroll/screen]: '
    ).strip().lower()
    if baud.isdigit() and int(baud) in BAUD_RATES:
        connection_baud = int(baud)
        current_profile["baud"] = connection_baud
    if columns.isdigit() and int(columns) in (40, 80):
        SCREEN_WIDTH = int(columns)
        current_profile["columns"] = SCREEN_WIDTH
    if mode in ("scroll", "screen"):
        current_profile["display_mode"] = mode
    save_profiles()


def premium_service(label):
    global premium_charges
    hourly_rate = 30.00
    clear()
    header_bar("finance")
    ansi_scroll("PREMIUM SERVICE", 0.01)
    ansi_scroll(label.lstrip("$ "), 0.01)
    ansi_scroll(f"Additional charge: ${hourly_rate:.2f} per hour", 0.01)
    choice = input("Enter Y to continue or M for menu ! ").strip().upper()
    if choice != "Y":
        return False
    ansi_scroll("Premium data service connected.", 0.01)
    premium_charges += hourly_rate / 60  # one-minute minimum charge
    return True


def finance_service(choice):
    if choice == "1":
        if not premium_service("$ MicroQuote"):
            return
        quotes = cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {}))
        cis_business.apply_corporate_actions(sys.modules[__name__])
        cis_business.process_limits(sys.modules[__name__], quotes)
        while True:
            symbol = input("Symbol, LIST, WATCH, MY, BUY, SELL, LIMIT, ORDERS, PORT, HISTORY, or M ! ").strip().upper()
            if symbol == "M":
                return
            if symbol == "LIST":
                text_page("finance", "MICROQUOTE SYMBOL DIRECTORY", [f"{item[0]:<5} {item[1]:<38} {item[2]}" for item in cis_business.directory()])
                continue
            if symbol == "MY":
                watched = cis_business.watchlist(sys.modules[__name__])
                text_page("finance", "MY MICROQUOTE WATCH LIST", [f'{item:<5} {quotes[item]["last"]:>8.2f} {quotes[item]["change"]:+7.2f}  {cis_business.COMPANIES[item][0]}' if item in quotes else f"{item:<5} QUOTE UNAVAILABLE  {cis_business.COMPANIES[item][0]}" for item in watched] or ["No symbols watched."])
                continue
            if symbol.startswith("WATCH "):
                ansi_scroll(cis_business.watchlist(sys.modules[__name__], symbol[6:].strip()), 0.01)
                continue
            if symbol.startswith("REMOVE "):
                ansi_scroll(cis_business.watchlist(sys.modules[__name__], symbol[7:].strip(), True), 0.01)
                continue
            if symbol == "PORT":
                text_page("finance", "MY FICTIONAL MARKET PORTFOLIO", cis_business.portfolio_lines(sys.modules[__name__], quotes))
                continue
            if symbol == "HISTORY":
                text_page("finance", "FICTIONAL TRADE LEDGER", cis_business.ledger_lines(sys.modules[__name__]))
                continue
            if symbol == "ORDERS":
                text_page("finance", "MICROQUOTE LIMIT ORDERS", cis_business.limit_lines(sys.modules[__name__]))
                continue
            if symbol == "LIMIT":
                action = input("BUY or SELL: ").strip().upper(); ticker = input("Symbol: ").strip().upper()
                quantity = input("Whole shares: ").strip(); price = input("Limit price: ").strip()
                shares = int(quantity) if quantity.isdigit() else 0
                try: limit_price = float(price)
                except ValueError: limit_price = 0
                ansi_scroll(cis_business.place_limit(sys.modules[__name__], action, ticker, shares, limit_price), 0.01)
                continue
            if symbol in ("BUY", "SELL"):
                ticker = input("Symbol: ").strip().upper()
                quantity = input("Whole shares: ").strip()
                shares = int(quantity) if quantity.isdigit() else 0
                quote = quotes.get(ticker)
                if quote:
                    fee = cis_business.commission(quote["last"] * shares) if shares else 0
                    confirmation = input(f"{symbol} {shares} {ticker} @ ${quote['last']:.2f} plus ${fee:.2f} commission [Y/N]? ").strip().upper()
                    if confirmation != "Y":
                        ansi_scroll("Trade cancelled.", 0.01)
                        continue
                result = cis_business.trade(sys.modules[__name__], symbol, ticker, shares, quotes)
                ansi_scroll(result, 0.01)
                if "RECORDED" in result:
                    hint = cis_experience.first_hint(sys.modules[__name__], "first_trade", "Enter PORT here or GO FINANCE and choose Portfolio Center to review profit and loss.")
                    if hint: ansi_scroll(hint, 0.01)
                continue
            quote = quotes.get(symbol)
            lines = [f"{symbol}  LAST {quote['last']:.2f}  CHANGE {quote['change']:+.2f}", "Delayed fictional December 1988 quotation."] if quote else ["Symbol not found in demonstration quotation file."]
            text_page("finance", "MICROQUOTE", lines)
    elif choice == "2":
        lines = cis_dynamic.market_report(service_data.get("quotes", {}))
        lines.extend(["", *cis_business.market_arc_lines(sys.modules[__name__])])
        if current_user_id and cis_dynamic.simulation_day().day >= 12:
            lines.extend(["", *cis_story.source_lines(sys.modules[__name__], "FINANCE")])
        text_page("finance", "MARKET REPORT", lines)
    elif choice == "3":
        if not premium_service("$ Standard & Poor's"):
            return
        query = input("Company symbol/name, LIST, or industry: ").strip()
        matches = cis_business.directory(query if query.upper() != "LIST" else "")
        if len(matches) == 1:
            text_page("finance", "STANDARD & POOR'S COMPANY REPORT", cis_business.report(matches[0][0], cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {}))))
        else:
            text_page("finance", "STANDARD & POOR'S DIRECTORY", [f"{item[0]:<5} {item[1]:<38} {item[2]}" for item in matches] or ["No matching company or industry."])
    elif choice == "4":
        lines = [f"USD/{code}  {rate:.2f}" for code, rate in service_data.get("exchange", {}).items()]
        text_page("finance", "FOREIGN EXCHANGE RATES", lines)
    elif choice == "5":
        quotes = cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {}))
        text_page("finance", "PORTFOLIO CENTER", cis_business.portfolio_lines(sys.modules[__name__], quotes))
        action = input("H history, D download research packet, or RETURN ! ").strip().upper()
        if action == "H":
            text_page("finance", "FICTIONAL TRADE LEDGER", cis_business.ledger_lines(sys.modules[__name__]))
        elif action == "D":
            packet = cis_business.export_packet(sys.modules[__name__], quotes)
            ansi_scroll(f"ASCII research packet prepared: {packet.name}", 0.01)
    elif choice == "6":
        text_page("finance", "ECONOMIC AND FIXED-INCOME INDICATORS", cis_business.economic_indicators())
        if input("D to download full research packet, or RETURN ! ").strip().upper() == "D":
            packet = cis_business.export_packet(sys.modules[__name__], cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {})))
            ansi_scroll(f"ASCII research packet prepared: {packet.name}", 0.01)
    elif choice == "7":
        text_page("finance", "DECEMBER MARKET CHALLENGE", cis_business.challenge_lines(sys.modules[__name__], cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {}))))
    elif choice == "8":
        quotes = cis_business.member_quotes(sys.modules[__name__], service_data.get("quotes", {}))
        text_page("finance", "INVESTMENT CLUB MARKET WATCH", cis_business.investment_club_lines(sys.modules[__name__], quotes))
        if not cis_dynamic.load_state(sys.modules[__name__]).get("investment_club", {}).get(current_user_id or "GUEST"):
            if input("F to file a forecast, or RETURN ! ").strip().upper() == "F":
                symbol = input("INTC or MOT: ").strip().upper()
                direction = input("UP or DOWN: ").strip().upper()
                ansi_scroll(cis_business.submit_forecast(sys.modules[__name__], symbol, direction), 0.01)


def travel_service(choice):
    if choice == "1":
        if not premium_service("$ Official Airline Guide"):
            return
        origin = input("From city code: ").strip().upper() or "ORD"
        destination = input("To city code: ").strip().upper() or "LGA"
        if origin not in cis_travel.AIRPORTS or destination not in cis_travel.AIRPORTS or origin == destination:
            text_page("travel", "AIRPORT CODE DIRECTORY", ["Enter two different listed airport codes.", "", *cis_travel.airport_lines()])
            return
        travel_date = cis_travel.validate_travel_date(input("Travel date [MM/DD/88]: "))
        if not travel_date:
            ansi_scroll("Enter a valid December 1988 date, or OPEN.", 0.01)
            return
        cabin = input("Service [COACH/FIRST]: ").strip().upper() or "COACH"
        cabin = cabin if cabin in ("COACH", "FIRST") else "COACH"
        schedules = cis_dynamic.flight_schedule(origin, destination, travel_date, cabin)
        text_page("travel", "OFFICIAL AIRLINE GUIDE", schedules)
        if input("R to make a fictional reservation, or RETURN ! ").strip().upper() == "R":
            selection = input("Flight 1-3: ").strip()
            if selection in ("1", "2", "3"):
                count = input("Passengers 1-6: ").strip()
                passengers = int(count) if count.isdigit() and 1 <= int(count) <= 6 else 1
                confirmation = cis_dynamic.reserve_itinerary(sys.modules[__name__], origin, destination, schedules[int(selection) - 1], travel_date, passengers)
                ansi_scroll(f"Reservation recorded. Confirmation {confirmation}." if confirmation else "That flight is cancelled; choose another itinerary.", 0.01)
                if confirmation:
                    hint = cis_experience.first_hint(sys.modules[__name__], "first_trip", "Enter GO CALENDAR for scheduled updates or use My Trip Folder for the complete itinerary.")
                    if hint: ansi_scroll(hint, 0.01)
    elif choice == "2":
        city = input("City: ").strip().upper()
        city, hotels = cis_travel.hotels(city)
        text_page("travel", "HOTEL AND MOTEL DIRECTORY", hotels or ["No listings found. Try CHICAGO, NEW YORK, DALLAS, LOS ANGELES, SAN FRANCISCO, or BOSTON."])
        if hotels and input("R to make a fictional lodging request, or RETURN ! ").strip().upper() == "R":
            selection = input(f"Property 1-{len(hotels)}: ").strip()
            nights_text = input("Nights 1-14: ").strip()
            nights = int(nights_text) if nights_text.isdigit() and 1 <= int(nights_text) <= 14 else 1
            if selection.isdigit() and 1 <= int(selection) <= len(hotels):
                confirmation = cis_dynamic.reserve_hotel(sys.modules[__name__], city, hotels[int(selection) - 1], nights)
                ansi_scroll(f"Lodging request recorded. Confirmation {confirmation}.", 0.01)
    elif choice == "3":
        city = input("Weather city: ").strip().upper() or "CHICAGO"
        text_page("travel", "TRAVELGRAMS AND WEATHER", [*cis_travel.travelgram(city), "", *cis_dynamic.weather(city)])
    elif choice == "4":
        text_page("travel", "TRAVEL SERVICE INSTRUCTIONS", [
            "Use three-letter airport codes when known.",
            "The airport directory validates twelve major U.S. gateways.",
            "Air displays include fictional availability, fares, dates, and service class.",
            "Hotel requests include nightly rate guidance and EasyPlex confirmation.",
            "$ indicates an additional premium service charge.",
            "Always confirm schedules and fares with the carrier.",
        ])
    elif choice == "5":
        text_page("travel", "MY TRIP FOLDER", cis_travel.trip_folder(sys.modules[__name__]))
        action = input("D download, P preferences, B rebook air, or RETURN ! ").strip().upper()
        if action == "D":
            packet = cis_travel.export_itinerary(sys.modules[__name__])
            ansi_scroll(f"ASCII itinerary prepared: {packet.name}", 0.01)
        elif action == "P":
            current = cis_travel.traveler_profile(sys.modules[__name__])
            seat = input(f'Seat [{current["seat"]}] WINDOW/AISLE/NO PREFERENCE: ').strip().upper() or current["seat"]
            car = input(f'Car [{current["car"]}] COMPACT/INTERMEDIATE/FULL SIZE: ').strip().upper() or current["car"]
            hotel = input(f'Hotel [{current["hotel"]}] ECONOMY/BUSINESS/FULL SERVICE: ').strip().upper() or current["hotel"]
            home = input(f'Home airport [{current["home_airport"]}]: ').strip().upper() or current["home_airport"]
            airline = input(f'Preferred airline [{current["airline"]}]: ').strip().upper() or current["airline"]
            number = input(f'Frequent-traveler number [{current["frequent_traveler"]}]: ').strip().upper() or current["frequent_traveler"]
            cis_travel.traveler_profile(sys.modules[__name__], {"seat": seat, "car": car, "hotel": hotel, "home_airport": home, "airline": airline, "frequent_traveler": number})
            ansi_scroll("Traveler preferences recorded.", 0.01)
        elif action == "B":
            confirmation = input("Confirmation: ").strip().upper()
            state = cis_dynamic.load_state(sys.modules[__name__])
            reservation = next((item for item in state.get("reservations", []) if item.get("confirmation") == confirmation and item.get("user_id") == current_user_id), None)
            if reservation:
                choices = cis_dynamic.flight_schedule(reservation["origin"], reservation["destination"], reservation.get("travel_date", "OPEN"))
                text_page("travel", "REBOOKING OPTIONS", choices)
                selection = input("Replacement flight 1-3: ").strip()
                if selection in ("1", "2", "3"):
                    ansi_scroll(cis_dynamic.rebook_itinerary(sys.modules[__name__], confirmation, choices[int(selection) - 1]), 0.01)
    elif choice == "6":
        city = input("City or airport code: ").strip().upper() or "CHICAGO"
        text_page("travel", "RAIL AND RENTAL CAR DIRECTORY", cis_travel.ground_transport(city))
    elif choice == "7":
        origin = input("From airport: ").strip().upper() or "ORD"
        destination = input("To airport: ").strip().upper() or "LGA"
        city = input("Hotel city: ").strip().upper() or cis_travel.AIRPORTS.get(destination, destination)
        travel_date = cis_travel.validate_travel_date(input("Departure [MM/DD/88]: "))
        if not travel_date:
            ansi_scroll("Enter a valid December 1988 date, or OPEN.", 0.01); return
        nights_text = input("Nights: ").strip(); nights = int(nights_text) if nights_text.isdigit() and 1 <= int(nights_text) <= 14 else 1
        if origin in cis_travel.AIRPORTS and destination in cis_travel.AIRPORTS and origin != destination:
            text_page("travel", "COMBINED TRIP PLANNER", cis_travel.combined_plan(origin, destination, city, nights, travel_date, cis_dynamic.flight_schedule))
        else:
            text_page("travel", "AIRPORT CODE DIRECTORY", cis_travel.airport_lines())
    elif choice == "8":
        live_weather_service()
    elif choice == "9":
        cis_disruptions.service(sys.modules[__name__])


def live_weather_service():
    default_city = current_profile.get("weather_city", "Chicago") if current_profile else "Chicago"
    city = input(f"Live weather city [{default_city}]: ").strip() or default_city
    if current_profile is not None and city != current_profile.get("weather_city"):
        current_profile["weather_city"] = city
        save_profiles()
    ansi_scroll("Contacting live weather wire...", 0.005)
    try:
        report = cis_weather.live_weather(city, BASE_DIR)
        text_page("travel", "COMPUSERVE LIVE WEATHER WIRE", cis_weather.weather_lines(report))
    except cis_weather.LiveWeatherError as exc:
        text_page("travel", "LIVE WEATHER UNAVAILABLE", [str(exc), "", "The fictional December 1988 weather service remains available under Travelgrams."])


def reference_service(choice):
    if choice == "7":
        text_page("reference", "SPECIAL DESK CASE INDEX", cis_story.source_lines(sys.modules[__name__], "REFERENCE"))
        return
    if choice in ("5", "6"):
        live_reference_service("wikipedia" if choice == "5" else "openalex")
        return
    if choice in ("1", "2"):
        if not premium_service(screens["reference"]["options"][choice]):
            return
    database = {"1": "academic", "2": "medical", "3": "science", "4": "library"}.get(choice)
    if not database:
        return
    while True:
        clear()
        header_bar("reference")
        ansi_scroll(cis_reference.DATABASES[database]["title"], 0.01)
        ansi_scroll("Enter words, B browse, SUBJECTS, HISTORY, MARK id, MARKED, DOWNLOAD, or M.", 0.005)
        query = input("SEARCH ! ").strip()
        if query.upper() == "M":
            return
        if query.upper() in ("H", "HELP"):
            text_page("reference", "DATA BASE SEARCH HELP", ["Enter one or more significant words.", "Boolean operators: AND, OR, and NOT.", "B displays the complete alphabetical index.", "SUBJECTS lists subject indexes; enter SUBJECT name to browse one.", "HISTORY, RECALL n, and CLEAR HISTORY manage previous searches.", "MARK id, MARKED, and DOWNLOAD prepare an ASCII research packet.", "Select a result number or record ID to display its record."])
            continue
        command = query.upper()
        if command == "SUBJECTS":
            text_page("reference", "SUBJECT INDEXES", [f"{name:<16} {len(cis_reference.subject_records(database, name))} records" for name in cis_reference.SUBJECTS[database]])
            continue
        if command.startswith("SUBJECT "):
            subject = command[8:].strip()
            records = cis_reference.subject_records(database, subject)
            if not records:
                ansi_scroll("Subject not found. Enter SUBJECTS for the index.", 0.01)
                continue
        elif command == "HISTORY":
            history = cis_reference.search_history(sys.modules[__name__])
            text_page("reference", "REFERENCE SEARCH HISTORY", [f'{index:>2} {item["database"].upper():<9} {item["query"]} ({item["results"]})' for index, item in enumerate(history, 1)] or ["No searches recorded."])
            continue
        elif command.startswith("RECALL "):
            history = cis_reference.search_history(sys.modules[__name__])
            number = command[7:].strip()
            if not number.isdigit() or not 1 <= int(number) <= len(history):
                ansi_scroll("History item not found.", 0.01)
                continue
            item = history[int(number) - 1]
            database = item["database"]
            if database not in cis_reference.DATABASES:
                ansi_scroll("Repeat live searches from the appropriate Live Reference service.", 0.01)
                continue
            query = item["query"]
            records = cis_reference.search(database, query)
            cis_reference.record_search(sys.modules[__name__], database, query, len(records))
        elif command == "CLEAR HISTORY":
            cis_reference.clear_history(sys.modules[__name__])
            ansi_scroll("Reference search history cleared.", 0.01)
            continue
        elif command.startswith("MARK "):
            ansi_scroll(cis_reference.mark_record(sys.modules[__name__], command[5:].strip()), 0.01)
            continue
        elif command == "MARKED":
            marked = cis_reference.marked_records(sys.modules[__name__])
            text_page("reference", "MARKED REFERENCE RECORDS", [f"{record[0]} {record[1]}" for _, record in marked] or ["No records marked."])
            continue
        elif command == "DOWNLOAD":
            packet = cis_reference.export_marked(sys.modules[__name__])
            ansi_scroll(f"Reference packet prepared: {packet.name}" if packet else "No records marked.", 0.01)
            continue
        elif command == "B":
            records = cis_reference.search(database, "")
        else:
            records = cis_reference.search(database, query)
            cis_reference.record_search(sys.modules[__name__], database, query, len(records))
        page = 0
        page_size = 12
        while True:
            clear()
            header_bar("reference")
            ansi_scroll(f'{cis_reference.DATABASES[database]["title"]} - {len(records)} RECORD(S)', 0.01)
            start = page * page_size
            for index, record in enumerate(records[start:start + page_size], start + 1):
                ansi_scroll(f"{index:>2} {cis_reference.result_line(record)}", 0.005)
            ansi_scroll(f"PAGE {page + 1} OF {max(1, (len(records) + page_size - 1) // page_size)}", 0.005)
            selection = input("Record number/ID, F, B, S new search, or M ! ").strip().upper()
            if selection == "M":
                return
            if selection == "S":
                break
            if selection == "F" and start + page_size < len(records):
                page += 1
                continue
            if selection == "B" and page > 0:
                page -= 1
                continue
            record = None
            if selection.isdigit() and 1 <= int(selection) <= len(records):
                record = records[int(selection) - 1]
            elif selection:
                selected_database, selected_record = cis_reference.find_record(selection)
                if selected_database == database:
                    record = selected_record
            if record:
                reference_record_page(database, record)


def live_reference_service(provider="wikipedia"):
    academic = provider == "openalex"
    while True:
        clear()
        header_bar("reference")
        ansi_scroll("COMPUSERVE LIVE ACADEMIC REFERENCE" if academic else "COMPUSERVE LIVE GENERAL REFERENCE", 0.01)
        ansi_scroll("Enter BEFORE 1989 words for historical literature." if academic else "Modern Wikipedia information formatted for your terminal.", 0.005)
        query = input("SEARCH, MARKED, DOWNLOAD (or M) ! ").strip()
        if query.upper() == "M":
            return
        if query.upper() == "MARKED":
            records = cis_reference.marked_live_records(sys.modules[__name__])
            text_page("reference", "MARKED LIVE REFERENCE RECORDS", [cis_reference.live_result_line(record) for record in records] or ["No live records marked."])
            continue
        if query.upper() == "DOWNLOAD":
            packet = cis_reference.export_marked(sys.modules[__name__])
            ansi_scroll(f"Reference packet prepared: {packet.name}" if packet else "No records marked.", 0.01)
            continue
        if not query:
            continue
        ansi_scroll("Contacting live reference service...", 0.005)
        try:
            records = (cis_reference.search_openalex_reference if academic else cis_reference.search_live_reference)(query, base_dir=BASE_DIR)
        except cis_reference.LiveReferenceError as exc:
            text_page("reference", "LIVE REFERENCE UNAVAILABLE", [str(exc), "", "The classic offline reference databases remain available."])
            continue
        cis_reference.record_search(sys.modules[__name__], "academic-live" if academic else "live", query, len(records))
        if not records:
            text_page("reference", "LIVE REFERENCE SEARCH", ["No matching records were returned."])
            continue
        while True:
            clear()
            header_bar("reference")
            cache_label = " - CACHED" if records and records[0].get("cached") else ""
            heading = "LIVE ACADEMIC REFERENCE" if academic else "LIVE GENERAL REFERENCE"
            ansi_scroll(f"{heading} - {len(records)} RECORD(S){cache_label}", 0.01)
            for index, record in enumerate(records, 1):
                ansi_scroll(f"{index:>2} {cis_reference.live_result_line(record)}", 0.005)
            selection = input("Record number, MARK n, S new search, or M ! ").strip().upper()
            if selection == "M":
                return
            if selection == "S":
                break
            if selection.startswith("MARK "):
                target = selection[5:].strip()
                record = None
                if target.isdigit() and 1 <= int(target) <= len(records):
                    record = records[int(target) - 1]
                else:
                    record = next((item for item in records if item["id"].upper() == target), None)
                ansi_scroll(cis_reference.mark_live_record(sys.modules[__name__], record) if record else "Record not found.", 0.01)
                continue
            if selection.isdigit() and 1 <= int(selection) <= len(records):
                record = records[int(selection) - 1]
                text_page("reference", record["title"], cis_reference.live_article_lines(record))


def comp_u_store():
    products = cis_store.CATALOG
    page = 0
    page_size = 10
    while True:
        clear()
        header_bar("shopping")
        ansi_scroll("COMP-U-STORE ELECTRONIC CATALOG", 0.01)
        ansi_scroll(cis_store.catalog_issue(), 0.005)
        ansi_scroll("All orders and charges are fictional.", 0.005)
        start = page * page_size
        for product in products[start:start + page_size]:
            price = cis_store.effective_price(product)
            marker = "*" if price != product["price"] else " "
            ansi_scroll(f'{product["sku"]} {product["name"]:<35} ${price:>7.2f}{marker}', 0.005)
        ansi_scroll(f"PAGE {page + 1} OF {max(1, (len(products) + page_size - 1) // page_size)}", 0.005)
        ansi_scroll("* DECEMBER SPECIAL", 0.005)
        command = input("Item, F/B, C category, S search, D deals, K compatibility, A/V/R/O, M ! ").strip().upper()
        if command == "M":
            return
        if command == "F" and start + page_size < len(products):
            page += 1
            continue
        if command == "B" and page > 0:
            page -= 1
            continue
        if command == "C":
            category = input("Category [" + "/".join(cis_store.categories()) + "]: ").strip().upper()
            products = cis_store.search(category=category) or cis_store.CATALOG
            page = 0
            continue
        if command == "S":
            words = input("Catalog search words: ").strip()
            products = cis_store.search(words)
            page = 0
            continue
        if command == "D":
            products = cis_store.specials()
            page = 0
            continue
        if command == "K":
            system, matches = cis_store.compatible_products(input("Computer [IBM PC/XT, IBM PC AT, Macintosh Plus, Commodore 64, TRS-80]: "))
            if system:
                products = matches
                page = 0
                ansi_scroll(f"Showing catalog guidance for {system}.", 0.01)
            else:
                ansi_scroll("That computer is not in this catalog issue's compatibility index.", 0.01)
            continue
        if command == "A":
            sku = input("Item number: ").strip()
            quantity = input("Quantity 1-9: ").strip()
            ansi_scroll(cis_store.add_to_cart(sys.modules[__name__], sku, int(quantity) if quantity.isdigit() else 1), 0.01)
            continue
        if command == "R":
            ansi_scroll(cis_store.remove_from_cart(sys.modules[__name__], input("Item number: ").strip()), 0.01)
            continue
        if command == "V":
            lines, subtotal, shipping = cis_store.cart_summary(sys.modules[__name__])
            text_page("shopping", "CURRENT COMP-U-STORE ORDER", [*lines, "", f"MERCHANDISE ${subtotal:.2f}", f"SHIPPING    ${shipping:.2f}", f"TOTAL       ${subtotal + shipping:.2f}"] if lines else ["No items selected."])
            continue
        if command == "O":
            lines, subtotal, shipping = cis_store.cart_summary(sys.modules[__name__])
            if not lines:
                ansi_scroll("No items selected.", 0.01)
            elif input(f"Send fictional order for ${subtotal + shipping:.2f} [Y/N]? ").strip().upper() == "Y":
                order = cis_store.checkout(sys.modules[__name__])
                ansi_scroll(f'Order {order["number"]} recorded. EasyPlex confirmation will follow.', 0.01)
                hint = cis_experience.first_hint(sys.modules[__name__], "first_order", "Enter GO PROFILE to track fulfillment or GO CALENDAR to see pending status changes.")
                if hint: ansi_scroll(hint, 0.01)
            continue
        product = cis_store.find_product(command)
        if product:
            text_page("shopping", f'CATALOG ITEM {product["sku"]}', [*cis_store.product_details(product), "", "Use A from the catalog to add this item."])


def shopping_service(choice):
    if choice == "1":
        comp_u_store()
    elif choice == "2":
        listings = cis_dynamic.active_classifieds(sys.modules[__name__], service_data.get("classifieds", []))
        text_page("shopping", "ELECTRONIC CLASSIFIEDS", listings)
        action = input("P Post, I Inquire, S mark Sold, M Mine, or RETURN ! ").strip().upper()
        if action == "P":
            category = input("Category [COMPUTERS/MODEMS/SOFTWARE/PERIPHERALS/BOOKS/WANTED]: ").strip().upper()
            advertisement = input("Advertisement: ").strip()
            if advertisement:
                number = cis_dynamic.post_classified(sys.modules[__name__], advertisement, category)
                ansi_scroll(f"Classified advertisement #{number} posted for 21 days.", 0.01)
        elif action == "M":
            text_page("shopping", "MY CLASSIFIED ADVERTISEMENTS", cis_dynamic.member_classifieds(sys.modules[__name__]))
        elif action in ("I", "S"):
            number = input("Advertisement number: ").strip().lstrip("#")
            if number.isdigit():
                message = input("Inquiry message: ").strip() if action == "I" else ""
                result = cis_dynamic.classified_action(sys.modules[__name__], int(number), "inquire" if action == "I" else "sold", message)
                ansi_scroll(result, 0.01)
    elif choice == "3":
        text_page("shopping", "CONSUMER PRODUCT INFORMATION", [
            "MODEMS -- Compare protocol support and warranty service.",
            "MONITORS -- Verify display adapter compatibility.",
            "DISKETTES -- Store magnetic media away from heat and motors.",
            "EXPANSION BOARDS -- Verify slot type, switch settings, and power needs.",
            "SOFTWARE -- Confirm operating-system version, memory, and disk format.",
            "",
            "The Comp-U-Store K command searches the compatibility index.",
            "Owner reports reflect simulated members' experience, not laboratory tests.",
        ])
    elif choice == "4":
        text_page("shopping", "SHOPPING INSTRUCTIONS", [
            "Enter an item number for descriptions, availability, and owner reports.",
            "Use D for December specials and K for computer compatibility guidance.",
            "Orders in this historical simulation are not transmitted.",
            "Use Electronic Classifieds to contact another member by User ID.",
        ])
    elif choice == "5":
        cis_ownership.service(sys.modules[__name__])


def games_service(choice):
    if choice == "1":
        adventure_game()
    elif choice == "2":
        if not premium_service("$ MegaWars"):
            return
        megawars_game()
    elif choice == "3":
        trivia_tournament()
    elif choice == "4":
        text_page("games", "GAME INSTRUCTIONS", [
            "Most games use short command words or numbered choices.",
            "Adventure supports exploration, optional discoveries, SCORE, MAP, and SAVE.",
            "MegaWars adds missions, shields, missiles, ranks, docking, and a sector map.",
            "Trivia Tournament contains five-question rounds and persistent streak records.",
            "Enter M to return to the previous menu.",
            "$ identifies premium connect-time services.",
        ])
    elif choice == "5":
        game_records()
    elif choice == "6":
        cis_adventure_league.service(sys.modules[__name__])


TRIVIA_BANK = [
    ("What company introduced the PC/AT?", {"IBM", "INTERNATIONAL BUSINESS MACHINES"}, "IBM"),
    ("What does the M in MS-DOS identify?", {"MICROSOFT"}, "Microsoft"),
    ("How many bits are in one byte?", {"8", "EIGHT"}, "8"),
    ("Which modem command prefix means attention?", {"AT"}, "AT"),
    ("What removable disk size is commonly called a floppy?", {"5.25", "5 1/4", "FIVE AND A QUARTER"}, "5.25 inches"),
    ("Which language was named for Admiral Grace Hopper?", {"COBOL"}, "COBOL"),
    ("What does RAM stand for?", {"RANDOM ACCESS MEMORY"}, "Random Access Memory"),
    ("Which key combination commonly reboots an IBM PC?", {"CTRL ALT DEL", "CONTROL ALT DELETE", "CTRL-ALT-DEL"}, "Ctrl-Alt-Del"),
    ("What does ASCII standardize?", {"CHARACTERS", "CHARACTER CODES", "TEXT", "CHARACTER ENCODING"}, "character codes"),
    ("Which company produced the Macintosh?", {"APPLE", "APPLE COMPUTER"}, "Apple Computer"),
]


def trivia_tournament():
    """Play a persistent five-question trivia round."""
    user_id = current_user_id or "GUEST"
    state = cis_dynamic.load_state(sys.modules[__name__])
    records = state.setdefault("trivia_tournaments", {})
    record = records.setdefault(user_id, {"rounds": 0, "best": 0, "streak": 0, "best_streak": 0})
    seed = f"{user_id}:{cis_dynamic.simulation_day().isoformat()}:{record['rounds']}"
    questions = random.Random(seed).sample(TRIVIA_BANK, 5)
    correct_count = 0
    ansi_scroll("COMPUSERVE TRIVIA TOURNAMENT -- FIVE QUESTION ROUND", 0.01)
    for number, (question, accepted, display) in enumerate(questions, 1):
        answer = input(f"{number}/5 {question} ").strip().upper()
        if answer in ("M", "QUIT"):
            ansi_scroll("Round abandoned; completed answers remain on your lifetime record.", 0.01)
            break
        correct = answer in accepted
        score = state.setdefault("scores", {}).setdefault(user_id, {"correct": 0, "attempts": 0})
        score["attempts"] += 1
        score["correct"] += int(correct)
        if correct:
            correct_count += 1
            record["streak"] += 1
            record["best_streak"] = max(record["best_streak"], record["streak"])
            ansi_scroll("Correct.", 0.01)
        else:
            record["streak"] = 0
            ansi_scroll(f"Answer: {display}", 0.01)
        ansi_scroll(f"ROUND {correct_count}/{number}  LIFETIME {score['correct']}/{score['attempts']}", 0.01)
    else:
        record["rounds"] += 1
        record["best"] = max(record["best"], correct_count)
        bonus = correct_count * 10 + (25 if correct_count == 5 else 0)
        record["points"] = record.get("points", 0) + bonus
        ansi_scroll(f"ROUND COMPLETE: {correct_count}/5  AWARD {bonus} POINTS", 0.01)
        if correct_count == 5:
            cis_dynamic.record_activity(sys.modules[__name__], user_id, "GAME", "Completed a perfect Trivia Tournament round.")
    records[user_id] = record
    cis_dynamic.save_state(sys.modules[__name__], state)


def game_records():
    user_id = current_user_id or "GUEST"
    state = cis_dynamic.load_state(sys.modules[__name__])
    ship = state.get("megawars", {}).get(user_id, {})
    trivia = state.get("trivia_tournaments", {}).get(user_id, {})
    adventure = state.get("adventure_records", {}).get(user_id, {})
    league = state.get("adventure_league", {}).get(user_id, {})
    lines = [
        f"MEGAWARS RANK      {ship.get('rank', 'CADET')}",
        f"MEGAWARS VICTORIES {ship.get('victories', 0)}",
        f"MEGAWARS CREDITS   {ship.get('credits', 100)}",
        f"TRIVIA ROUNDS      {trivia.get('rounds', 0)}",
        f"TRIVIA BEST        {trivia.get('best', 0)}/5",
        f"TRIVIA BEST STREAK {trivia.get('best_streak', 0)}",
        f"TRIVIA POINTS      {trivia.get('points', 0)}",
        f"ADVENTURE WINS     {adventure.get('wins', 0)}",
        f"ADVENTURE BEST     {adventure.get('best_moves', '---')} moves",
        f"LEAGUE CHARACTER   {league.get('name', '---')}",
        f"LEAGUE LEVEL       {league.get('level', 0)}",
        f"LEAGUE GUILD       {league.get('guild') or '---'}",
    ]
    text_page("games", "PLAYER RECORDS", lines)


def adventure_game():
    rooms = {
        "terminal": ("You are beside a dusty public terminal. A locked door leads NORTH.", {"NORTH": "corridor"}),
        "corridor": ("A service corridor runs EAST to the computer room, WEST to storage, and NORTH to operations.", {"SOUTH": "terminal", "EAST": "computer", "WEST": "storage", "NORTH": "operations"}),
        "storage": ("Shelves hold cables, manuals, diagnostic tapes, and discarded circuit boards.", {"EAST": "corridor"}),
        "computer": ("Rows of disk drives stand silent. A control console reads POWER FAILURE.", {"WEST": "corridor", "NORTH": "tape_room"}),
        "operations": ("Shift logs cover the operations desk. One entry mentions a failed cooling alarm.", {"SOUTH": "corridor", "EAST": "cooling"}),
        "cooling": ("A stalled ventilation fan stands behind a safety grille.", {"WEST": "operations"}),
        "tape_room": ("Nine-track tape drives line the wall. Drive 3 is empty and marked DIAGNOSTIC.", {"SOUTH": "computer"}),
    }
    inventory = set()
    room_items = {"terminal": {"KEY"}, "storage": {"FUSE", "DIAGNOSTIC TAPE"}, "operations": {"SHIFT LOG"}, "cooling": {"SCREWDRIVER"}}
    room = "terminal"
    powered = False
    cooling_repaired = False
    diagnostic_loaded = False
    discoveries = set()
    moves = 0
    ansi_scroll("ADVENTURE: THE SILENT MAINFRAME", 0.01)
    ansi_scroll("Restore the computer and discover why it stopped. Enter HELP for commands.", 0.01)

    def describe():
        ansi_scroll(rooms[room][0], 0.01)
        for item in sorted(room_items.get(room, set())):
            ansi_scroll(f"You can see a {item.lower()} here.", 0.01)
        if room == "computer" and powered:
            ansi_scroll("The console is alive. Its prompt reads: TYPE BOOT TO START CIS.", 0.01)
        if room == "cooling" and cooling_repaired:
            ansi_scroll("The ventilation fan now turns smoothly.", 0.01)
        if room == "tape_room" and diagnostic_loaded:
            ansi_scroll("Drive 3 shows DIAGNOSTIC READY.", 0.01)

    describe()
    while True:
        command = input("? ", local_go=("NORTH", "SOUTH", "EAST", "WEST", "UP", "DOWN")).strip().upper()
        if command in ("M", "QUIT"):
            return
        moves += 1
        aliases = {"N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST"}
        command = aliases.get(command, command)
        if command in ("LOOK", "L"):
            describe()
        elif command in ("INVENTORY", "I"):
            ansi_scroll("You are carrying: " + (", ".join(sorted(inventory)).lower() if inventory else "nothing"), 0.01)
        elif command == "MAP":
            ansi_scroll("TERMINAL-N-CORRIDOR-W-STORAGE / E-COMPUTER-N-TAPE ROOM / N-OPERATIONS-E-COOLING", 0.01)
        elif command == "SCORE":
            ansi_scroll(f"{len(discoveries) * 20} discovery points in {moves} moves.", 0.01)
        elif command.startswith(("TAKE ", "GET ")):
            item = command.split(maxsplit=1)[1]
            if item in room_items.get(room, set()):
                room_items[room].remove(item)
                inventory.add(item)
                ansi_scroll("Taken.", 0.01)
            else:
                ansi_scroll("You do not see that here.", 0.01)
        elif command in rooms[room][1] or command.startswith("GO "):
            direction = command.removeprefix("GO ")
            destination = rooms[room][1].get(direction)
            if not destination:
                ansi_scroll("You cannot go that way.", 0.01)
            elif room == "terminal" and direction == "NORTH" and "KEY" not in inventory:
                ansi_scroll("The north door is locked.", 0.01)
            else:
                room = destination
                describe()
        elif command in ("OPEN DOOR", "UNLOCK DOOR"):
            ansi_scroll("The key turns. The north door is now ready to open." if "KEY" in inventory else "You need a key.", 0.01)
        elif command in ("INSTALL FUSE", "USE FUSE") and room == "computer":
            if "FUSE" in inventory:
                inventory.remove("FUSE")
                powered = True
                ansi_scroll("You replace the blown fuse. Fans spin and disk drives seek in sequence.", 0.01)
                describe()
            else:
                ansi_scroll("You have no replacement fuse.", 0.01)
        elif command in ("FIX FAN", "USE SCREWDRIVER", "REPAIR FAN") and room == "cooling":
            if "SCREWDRIVER" in inventory:
                cooling_repaired = True
                discoveries.add("cooling")
                ansi_scroll("You tighten the fan coupling. Cool air begins moving through the raised floor.", 0.01)
            else:
                ansi_scroll("The grille requires a screwdriver.", 0.01)
        elif command in ("LOAD TAPE", "USE DIAGNOSTIC TAPE") and room == "tape_room":
            if "DIAGNOSTIC TAPE" in inventory:
                inventory.remove("DIAGNOSTIC TAPE")
                diagnostic_loaded = True
                discoveries.add("diagnostic")
                ansi_scroll("The tape threads successfully. Drive 3 reports DIAGNOSTIC READY.", 0.01)
            else:
                ansi_scroll("You do not have the diagnostic tape.", 0.01)
        elif command == "BOOT" and room == "computer":
            if powered:
                ansi_scroll("COMPUSERVE INFORMATION SERVICE ONLINE", 0.01)
                ansi_scroll(f"YOU HAVE WON IN {moves} MOVES.", 0.01)
                if cooling_repaired and diagnostic_loaded:
                    ansi_scroll("FULL RESTORATION: diagnostics pass and cooling is stable. BONUS 50.", 0.01)
                if current_user_id:
                    state = cis_dynamic.load_state(sys.modules[__name__])
                    record = state.setdefault("adventure_records", {}).setdefault(current_user_id, {"wins": 0})
                    record["wins"] += 1
                    record["best_moves"] = min(record.get("best_moves", moves), moves)
                    record["full_restorations"] = record.get("full_restorations", 0) + int(cooling_repaired and diagnostic_loaded)
                    cis_dynamic.save_state(sys.modules[__name__], state)
                    cis_dynamic.record_activity(sys.modules[__name__], current_user_id, "GAME", f"Restored the Silent Mainframe in {moves} moves.")
                input("Press RETURN ! ")
                return
            else:
                ansi_scroll("The console has no power.", 0.01)
        elif command in ("EXAMINE CONSOLE", "READ CONSOLE") and room == "computer":
            ansi_scroll("A maintenance label says: REPLACE 5-AMP FUSE BEFORE BOOT.", 0.01)
        elif command in ("HELP", "H"):
            ansi_scroll("LOOK, N/S/E/W, TAKE item, INVENTORY, MAP, SCORE, EXAMINE item, USE item, BOOT, QUIT", 0.01)
        else:
            ansi_scroll("I do not understand.", 0.01)


def megawars_game():
    user_id = current_user_id or "GUEST"
    state = cis_dynamic.load_state(sys.modules[__name__])
    careers = state.setdefault("megawars", {})
    ship = careers.setdefault(user_id, {"sector": 1, "energy": 100, "credits": 100, "cargo": 0, "victories": 0, "turns": 20})
    defaults = {
        "shields": 50, "missiles": 2, "hull": 100, "experience": 0,
        "rank": "CADET", "missions": 0, "mission_target": None,
    }
    for key, value in defaults.items():
        ship.setdefault(key, value)
    enemy = 45 + ship["sector"] * 5
    enemy_name = random.Random(f"{user_id}:{ship['sector']}:{ship['victories']}").choice(
        ["ORION RAIDER", "CYGNUS CORSAIR", "DRACON CRUISER", "ROGUE MINELAYER"]
    )

    def update_rank():
        ranks = ((300, "COMMODORE"), (180, "CAPTAIN"), (90, "COMMANDER"), (40, "LIEUTENANT"), (0, "CADET"))
        ship["rank"] = next(title for threshold, title in ranks if ship["experience"] >= threshold)

    def save_ship():
        careers[user_id] = ship
        cis_dynamic.save_state(sys.modules[__name__], state)

    def status():
        ansi_scroll(f'{ship["rank"]}  SECTOR {ship["sector"]}  ENERGY {ship["energy"]}  SHIELDS {ship["shields"]}  HULL {ship["hull"]}', 0.01)
        ansi_scroll(f'CREDITS {ship["credits"]}  CARGO {ship["cargo"]}/5  MISSILES {ship["missiles"]}  VICTORIES {ship["victories"]}  TURNS {ship["turns"]}', 0.01)

    def suffer_attack():
        damage = random.randint(5, 18)
        absorbed = min(ship["shields"], damage)
        ship["shields"] -= absorbed
        remainder = damage - absorbed
        ship["energy"] = max(0, ship["energy"] - remainder)
        if remainder:
            ship["hull"] = max(0, ship["hull"] - max(1, remainder // 2))
        ansi_scroll(f"Enemy return fire: {absorbed} shield and {remainder} energy damage.", 0.01)

    def award_victory():
        reward = 35 + ship["sector"] * 10
        mission_bonus = 0
        if ship.get("mission_target") == ship["sector"]:
            mission_bonus = 75 + ship["sector"] * 5
            ship["missions"] += 1
            ship["mission_target"] = None
        ship["credits"] += reward + mission_bonus
        ship["victories"] += 1
        ship["experience"] += 15 + ship["sector"] * 2 + (20 if mission_bonus else 0)
        update_rank()
        ansi_scroll(f"Enemy destroyed. Salvage award: {reward} credits.", 0.01)
        if mission_bonus:
            ansi_scroll(f"STAR COMMAND MISSION COMPLETE. BONUS {mission_bonus} CREDITS.", 0.01)

    ansi_scroll("MEGAWARS III -- PERSISTENT COMMAND", 0.01)
    status()
    ansi_scroll(f"A hostile {enemy_name} is on scanners. HELP lists commands.", 0.01)
    while ship["energy"] > 0 and ship["hull"] > 0 and ship["turns"] > 0:
        command = input("COMMAND: ").strip().upper()
        if command == "FIRE":
            ship["turns"] -= 1
            hit = random.randint(12, 28)
            enemy -= hit
            ansi_scroll(f"Phasers hit for {hit} units.", 0.01)
            if enemy > 0:
                suffer_attack()
            else:
                award_victory()
                enemy = 0
                break
        elif command in ("MISSILE", "FIRE MISSILE"):
            if not ship["missiles"]:
                ansi_scroll("Missile racks are empty.", 0.01)
                continue
            ship["turns"] -= 1
            ship["missiles"] -= 1
            hit = random.randint(30, 48)
            enemy -= hit
            ansi_scroll(f"Missile detonation inflicts {hit} units.", 0.01)
            if enemy > 0:
                suffer_attack()
            else:
                award_victory()
                enemy = 0
                break
        elif command == "SCAN":
            ship["turns"] -= 1
            ansi_scroll(f"{enemy_name} energy approximately {max(enemy, 0)}. Mission target: {ship.get('mission_target') or 'NONE'}.", 0.01)
        elif command == "TRADE":
            if ship["credits"] >= 20 and ship["cargo"] < 5:
                ship["credits"] -= 20
                ship["cargo"] += 1
                ansi_scroll("One unit of computer parts loaded for 20 credits.", 0.01)
            elif ship["cargo"]:
                earned = ship["cargo"] * (25 + ship["sector"] * 3)
                ship["credits"] += earned
                ship["cargo"] = 0
                ansi_scroll(f"Cargo sold for {earned} credits.", 0.01)
            else:
                ansi_scroll("Insufficient credits or cargo hold full.", 0.01)
        elif command == "REPAIR":
            repair = min(100 - ship["energy"], ship["credits"] // 2)
            if repair:
                ship["energy"] += repair
                ship["credits"] -= repair * 2
                ansi_scroll(f"Starbase restored {repair} energy units.", 0.01)
            else:
                ansi_scroll("No repairs are available.", 0.01)
        elif command in ("SHIELDS", "CHARGE SHIELDS"):
            amount = min(50 - ship["shields"], ship["energy"] // 2)
            if amount:
                ship["shields"] += amount
                ship["energy"] -= amount * 2
                ansi_scroll(f"Transferred {amount * 2} energy to shields; shield strength {ship['shields']}.", 0.01)
            else:
                ansi_scroll("Shield batteries cannot accept a charge.", 0.01)
        elif command in ("DOCK", "STARBASE"):
            energy_need = 100 - ship["energy"]
            hull_need = 100 - ship["hull"]
            cost = energy_need + hull_need * 2
            if cost and ship["credits"] >= cost:
                ship["credits"] -= cost
                ship["energy"] = ship["hull"] = 100
                ship["shields"] = 50
                ansi_scroll(f"Starbase overhaul complete for {cost} credits.", 0.01)
            else:
                ansi_scroll("Dockmaster reports no affordable work is required." if cost else "All systems already nominal.", 0.01)
        elif command in ("BUY MISSILE", "BUY MISSILES"):
            if ship["credits"] >= 30 and ship["missiles"] < 6:
                ship["credits"] -= 30
                ship["missiles"] += 1
                ansi_scroll("One photon missile loaded for 30 credits.", 0.01)
            else:
                ansi_scroll("Missile purchase denied: check credits and rack capacity.", 0.01)
        elif command == "MISSION":
            if ship.get("mission_target"):
                ansi_scroll(f"Active order: destroy the hostile vessel in sector {ship['mission_target']}.", 0.01)
            else:
                ship["mission_target"] = ship["sector"] % 9 + 1
                ansi_scroll(f"STAR COMMAND assigns sector {ship['mission_target']}. Jump there and defeat the contact.", 0.01)
                save_ship()
        elif command == "MAP":
            ansi_scroll("SECTORS 1-9 FORM A JUMP RING: 1-2-3-4-5-6-7-8-9-1", 0.01)
            ansi_scroll(f"CURRENT {ship['sector']}  MISSION {ship.get('mission_target') or 'NONE'}  STARBASE SERVICE AVAILABLE", 0.01)
        elif command in ("JUMP", "JUMP NEXT"):
            ship["turns"] -= 1
            ship["sector"] = ship["sector"] % 9 + 1
            save_ship()
            ansi_scroll(f'Jump complete. Sector {ship["sector"]} reached; a new contact appears on scanners.', 0.01)
            enemy = 45 + ship["sector"] * 5
            enemy_name = random.Random(f"{user_id}:{ship['sector']}:{ship['victories']}").choice(["ORION RAIDER", "CYGNUS CORSAIR", "DRACON CRUISER", "ROGUE MINELAYER"])
        elif command == "STATUS":
            status()
            ansi_scroll(f"ENEMY ENERGY {max(enemy, 0)}", 0.01)
        elif command in ("RETREAT", "SAVE", "M"):
            save_ship()
            ansi_scroll("Command saved. Vessel holding position.", 0.01)
            return
        elif command in ("HELP", "H"):
            ansi_scroll("FIRE, MISSILE, SCAN, STATUS, MISSION, MAP, TRADE, REPAIR, SHIELDS, DOCK, BUY MISSILE, JUMP, SAVE.", 0.01)
        else:
            ansi_scroll("Unknown command. Enter HELP for command summary.", 0.01)
    save_ship()
    if enemy <= 0:
        cis_dynamic.record_activity(sys.modules[__name__], user_id, "GAME", f'MegaWars victory in sector {ship["sector"]}; {ship["victories"]} total.')
    elif ship["energy"] <= 0 or ship["hull"] <= 0:
        ansi_scroll("Your vessel is disabled. Starbase recovery will cost 50 credits.", 0.01)
        ship["credits"] = max(0, ship["credits"] - 50)
        ship["energy"] = 40
        ship["hull"] = 50
        ship["shields"] = 10
        save_ship()
    else:
        ansi_scroll("No tactical turns remain. Command state saved.", 0.01)
    input("Press RETURN ! ")

# --- CB Chat ---------------------------------------------------------------

fake_users = ["RoadRunner", "NightOwl", "ByteBender", "SilverFox", "ModemMan", "LadyLightning"]


def ensure_cb_handle():
    global current_handle, current_profile
    if current_handle is not None:
        return
    default_handle = current_profile.get("last_handle") if current_profile else None
    prompt = "Enter CB handle"
    if default_handle:
        prompt += f" (RETURN for {default_handle})"
    handle = input(prompt + ": ").strip()
    current_handle = handle or default_handle or "Guest"
    session_state.handle = current_handle
    current_profile["last_handle"] = current_handle
    save_profiles()

def get_channel_personality(channel):
    return cb_personalities.get(str(channel), "friendly")

def personality_line(personality):
    if personality == "friendly":
        return random.choice([
            "Nice to see everyone here tonight.",
            "Hope your connections are solid!",
            "Good crowd on this channel.",
            "Always good vibes in here."
        ])
    if personality == "chaotic":
        return random.choice([
            "What is even happening in here?",
            "This channel is pure chaos.",
            "Messages flying faster than 2400 baud.",
            "Someone lost control of their keyboard."
        ])
    if personality == "technical":
        return random.choice([
            "Anyone debugging IRQ conflicts?",
            "Let’s talk BIOS settings.",
            "Who’s tweaking their CONFIG.SYS tonight?",
            "Channel 3: where the tech nerds live."
        ])
    return ""

def cb_chat(channel):
    global current_handle, current_profile
    ensure_cb_handle()
    channel = cis_cb.normalize_channel(channel)
    exchange = 0
    status = current_profile.get("cb_status", "AVAILABLE")
    ignored = {item.casefold() for item in current_profile.get("cb_ignored", [])}
    room = cis_cb.room(channel)
    simulated_present = cis_dynamic.cb_presence(channel)
    clear()
    header_bar("cb")
    ansi_scroll(f"CB - {channel}: {cis_cb.description(channel)}", 0.02)
    ansi_scroll(f"Handle: {current_handle}  Status: {status}", 0.02)
    ansi_scroll(f"{len(simulated_present)} simulated members and {len(list_cb_presence(BASE_DIR, room)) + 1} live member(s) present.", 0.01)
    scrollback = recent_live_messages(BASE_DIR, room, 20)
    last_message_id = scrollback[-1][0] if scrollback else 0
    for _, sender, body, stamp in scrollback:
        if sender.casefold() not in ignored:
            ansi_scroll(f"{stamp[11:16]} <{sender}> {body}", 0.005)
    set_cb_presence(BASE_DIR, live_session_id, room, current_handle, status)
    post_live_message(BASE_DIR, room, "SYSTEM", f"*** {current_handle} joined {channel} ***")
    ansi_scroll("/HELP lists CB commands.", 0.01)
    try:
        while True:
            set_cb_presence(BASE_DIR, live_session_id, room, current_handle, status)
            ambient_bucket = int(time.time() // 60)
            if claim_cb_ambient(BASE_DIR, room, ambient_bucket):
                recent_text = [body for _, _, body, _ in recent_live_messages(BASE_DIR, room, 30)]
                for sender, body in cis_dynamic.cb_ambient_events(channel, ambient_bucket, recent_text):
                    post_live_message(BASE_DIR, room, sender, body)
            for message_id, sender, body, _ in read_live_messages(BASE_DIR, room, last_message_id):
                last_message_id = message_id
                if sender.casefold() not in ignored:
                    ansi_scroll(f"<{sender}> {body}", 0.01)
                    if startup_options.get("sound") and winsound and sender not in (current_handle, "SYSTEM"):
                        winsound.MessageBeep()
            command, argument = cis_cb.parse_command(input(cis_prompt("cb") + " "))
            if command == "EXIT":
                break
            if command == "WHO":
                rows = list_cb_presence(BASE_DIR, room)
                live = [f"{handle} [{member_status}]" for _, handle, member_status, _ in rows]
                ansi_scroll("On channel: " + ", ".join(live + [f"{handle} [SIM]" for handle in simulated_present]), 0.01)
            elif command == "CHANNELS":
                cb_channel_directory()
            elif command == "JOIN" and argument:
                post_live_message(BASE_DIR, room, "SYSTEM", f"*** {current_handle} left for {argument} ***")
                channel = cis_cb.normalize_channel(argument)
                room = cis_cb.room(channel)
                simulated_present = cis_dynamic.cb_presence(channel)
                set_cb_presence(BASE_DIR, live_session_id, room, current_handle, status)
                scrollback = recent_live_messages(BASE_DIR, room, 20)
                last_message_id = scrollback[-1][0] if scrollback else 0
                ansi_scroll(f"*** Joined {channel}: {cis_cb.description(channel)} ***", 0.01)
                for _, sender, body, stamp in scrollback:
                    if sender.casefold() not in ignored:
                        ansi_scroll(f"{stamp[11:16]} <{sender}> {body}", 0.005)
                post_live_message(BASE_DIR, room, "SYSTEM", f"*** {current_handle} joined {channel} ***")
            elif command == "MSG" and " " in argument:
                recipient, text = argument.split(" ", 1)
                storage_update_json_atomic(BASE_DIR, "cb_mail.json", lambda messages: list(messages or []) + [{"from": current_handle, "to": recipient[:40], "date": cis_dynamic.simulation_day().strftime("%m/%d/%y"), "text": text[:1000]}], default=[])
                ansi_scroll(f"Private message stored for {recipient}.", 0.01)
            elif command == "IGNORE" and argument:
                key = argument[:40]
                values = current_profile.setdefault("cb_ignored", [])
                match = next((item for item in values if item.casefold() == key.casefold()), None)
                if match:
                    values.remove(match); ignored.discard(key.casefold()); ansi_scroll(f"No longer ignoring {key}.", 0.01)
                else:
                    values.append(key); ignored.add(key.casefold()); ansi_scroll(f"Ignoring {key}.", 0.01)
                save_profiles()
            elif command == "INFO" and argument:
                info = cis_dynamic.cb_member_info(sys.modules[__name__], argument)
                if info:
                    for line in info:
                        ansi_scroll(line, 0.005)
                else:
                    ansi_scroll("Simulated member not found.", 0.01)
            elif command == "STATUS" and argument.upper() in ("AVAILABLE", "AWAY", "BUSY"):
                status = argument.upper(); current_profile["cb_status"] = status; save_profiles()
                set_cb_presence(BASE_DIR, live_session_id, room, current_handle, status)
                ansi_scroll(f"Status is now {status}.", 0.01)
            elif command == "HELP":
                cb_help()
            elif command == "SAY" and argument:
                last_message_id = post_live_message(BASE_DIR, room, current_handle, argument)
                ansi_scroll(f"<{current_handle}> {argument}", 0.01)
                response = cis_dynamic.cb_response(channel, argument, exchange, sys.modules[__name__])
                exchange += 1
                if response:
                    user, line = response
                    last_message_id = post_live_message(BASE_DIR, room, user, line)
                    ansi_scroll(f"<{user}> {line}", 0.01)
            elif command not in ("SAY",):
                ansi_scroll("Unknown CB command. Enter /HELP.", 0.01)
    finally:
        post_live_message(BASE_DIR, room, "SYSTEM", f"*** {current_handle} left {channel} ***")
        remove_cb_presence(BASE_DIR, live_session_id)


def cb_channel_directory():
    presence = list_cb_presence(BASE_DIR)
    counts = {}
    for room, _, _, _ in presence:
        counts[room] = counts.get(room, 0) + 1
    lines = [f'{key:<12} {counts.get(cis_cb.room(key), 0) + len(cis_dynamic.cb_presence(key)):>2}  {description}' for key, description in cis_cb.CHANNELS.items()]
    custom = sorted({room[3:].upper() for room, _, _, _ in presence if room.startswith("cb:") and room[3:].upper() not in cis_cb.CHANNELS})
    lines.extend(f'{key:<12} {counts.get(cis_cb.room(key), 0):>2}  Member-created channel' for key in custom)
    text_page("cb", "CB CHANNEL DIRECTORY", ["CHANNEL      ON  DESCRIPTION", *lines, "", "Use /JOIN name from any channel."])


def cb_private_messages():
    ensure_cb_handle()
    messages = load_json("cb_mail.json", default=[])
    if not isinstance(messages, list):
        raise RuntimeError("cb_mail.json must contain a JSON list")
    while True:
        clear()
        header_bar("cb")
        inbox = [m for m in messages if m.get("to", "").lower() == current_handle.lower()]
        ansi_scroll("CB PRIVATE MESSAGES", 0.01)
        for index, message in enumerate(inbox, 1):
            ansi_scroll(f'{index}  From {message["from"]}: {message["text"]}', 0.005)
        ansi_scroll("S  Send private message", 0.01)
        ansi_scroll("M  Return to CB menu", 0.01)
        choice = input("Enter choice ! ").strip().upper()
        if choice == "M":
            return
        if choice == "S":
            recipient = input("To HANDLE: ").strip()[:40]
            text = input("Message: ").strip()[:1000]
            if recipient and text:
                messages.append({
                    "from": current_handle, "to": recipient,
                    "date": SIMULATION_DATE, "text": text,
                })
                save_json_atomic("cb_mail.json", messages)
                ansi_scroll("Private message stored.", 0.01)

# --- Navigation --------------------------------------------------------------

def show_screen(screen_key):
    screen = screens[screen_key]
    clear()
    for line in menu_lines(
        "CompuServe", page_names.get(screen_key, ""), screen["title"],
        screen["options"], SCREEN_WIDTH,
    ):
        ansi_scroll(line, 0.01)
    if screen_key == "main" and current_user_id and not session_state.top_announcements_shown:
        for line in cis_dynamic.announcements(current_user_id, mail_waiting_count(current_user_id), sys.modules[__name__]):
            ansi_scroll(line, 0.005)
        session_state.top_announcements_shown = True


def destination_label(destination):
    if destination in screens:
        return screens[destination]["title"]
    if destination in FORUM_CATALOG:
        return FORUM_CATALOG[destination]['title']
    labels = {
        "profile": "Personal Service Summary", "new": "What's New",
        "calendar": "Personal Calendar", "notebook": "Personal Notebook",
        "downloads": "Download Center", "achievements": "Achievements",
        "sysop": "Sysop Console",
        "drafts": "Personal Draft Center",
        "timeline": "December 1988 Historical Timeline",
        "weather": "Live Weather Wire",
        "features": "Historical Features",
        "magazine": "Online Weekly Magazine",
        "case": "Special Desk Investigation",
        "people": "Member Relationships",
        "equipment": "Owned Equipment and Support",
        "shareware": "TERMLINK Shareware Project",
    }
    return FORUM_CATALOG.get(destination, {}).get("title", labels.get(destination, destination.upper()))


def today_in_1988_lines(fetch_weather=True):
    """Build the compact post-login briefing from existing service data."""
    today = cis_dynamic.simulation_day()
    records = cis_timeline.records_for_date(today)
    if not records:
        # Outside the curated 1988 archive, fall back to "on this day".
        month_day = today.isoformat()[5:]
        records = [record for record in cis_timeline.RECORDS
                   if record.get("date", "")[5:] == month_day]
    counts = {}
    for item in cis_discovery.activity_items(sys.modules[__name__]):
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    lines = [f'{today:%A, %B %d, %Y}'.upper(), "", "TODAY IN HISTORY"]
    lines.extend(f'  {record["id"]}  {record["title"]}' for record in records)
    if not records:
        lines.append("  No curated entry for today.")
    lines.extend(["", "YOUR SERVICE"])
    service_kinds = ("MAIL", "FORUM", "ORDER", "TRAVEL", "DRAFT", "NOTICE")
    summaries = [f"{kind} {counts[kind]}" for kind in service_kinds if counts.get(kind)]
    lines.append("  " + ("  |  ".join(summaries) if summaries else "No unread member activity."))

    city = current_profile.get("weather_city", "Chicago") if current_profile else "Chicago"
    lines.extend(["", "LIVE WEATHER WIRE"])
    if fetch_weather:
        try:
            report = cis_weather.live_weather(city, BASE_DIR, timeout=3)
            current = report.get("current", {})
            code = int(current.get("weather_code", -1))
            place = report.get("location", {}).get("name", city).upper()
            cached = " (CACHED)" if report.get("cached") else ""
            lines.append(f'  {place}: {cis_weather.WEATHER_CODES.get(code, "UNKNOWN")}, {current.get("temperature_2m", "?")} F{cached}')
        except cis_weather.LiveWeatherError:
            lines.append(f"  {city.upper()}: unavailable; use GO WEATHER to retry.")
    else:
        lines.append(f"  {city.upper()}: use GO WEATHER for current conditions.")

    references = service_data.get("reference", [])
    if references:
        fact = references[(today.day - 1) % len(references)]
        lines.extend(["", f'DID YOU KNOW?  {fact["term"]}', f'  {fact["text"]}'])
    if current_user_id and cis_dynamic.simulation_day().day >= 12:
        lines.extend(["", "SPECIAL DESK", *[f"  {line}" for line in cis_story.status_lines(sys.modules[__name__])[:2]]])
    lines.extend(["", "READ HISTORY  |  READ WEATHER  |  READ NEW  |  GO CASE  |  GO TOP"])
    return lines


def today_in_1988_dashboard(fetch_weather=True):
    clear()
    header_bar("main")
    title = f"TODAY IN {cis_dynamic.simulation_day().year}"
    ansi_scroll(title, 0.01)
    ansi_scroll("-" * len(title), 0.01)
    for line in today_in_1988_lines(fetch_weather):
        ansi_scroll(line, 0.005)
    input("Press ENTER for the main menu ! ")


def activity_center():
    while True:
        items = cis_discovery.activity_items(sys.modules[__name__])
        clear()
        header_bar("main")
        ansi_scroll("WHAT'S NEW", 0.01)
        ansi_scroll("-----------", 0.01)
        if not items:
            ansi_scroll("No unread or changed items.", 0.01)
        for index, item in enumerate(items[:30], 1):
            ansi_scroll(f'{index:>2}  {item["kind"]:<7} {item["summary"]}', 0.005)
        if len(items) > 30:
            ansi_scroll(f"{len(items) - 30} additional items; use MARK ALL READ to clear the list.", 0.005)
        selection = input("Item number, R refresh, MARK ALL READ, or M ! ").strip().upper()
        if selection == "M":
            return
        if selection == "R":
            continue
        if selection == "MARK ALL READ":
            cis_discovery.mark_all_activity_seen(sys.modules[__name__], items)
            ansi_scroll("Current activity marked as read.", 0.01)
            continue
        if selection.isdigit() and 1 <= int(selection) <= min(len(items), 30):
            cis_discovery.open_activity(sys.modules[__name__], items[int(selection) - 1])


def linked_record_browser(kind, record, database=None):
    """Browse timeline and offline reference links with a local back stack."""
    stack = [(kind, database, record)]
    while stack:
        kind, database, record = stack[-1]
        clear()
        header_bar("timeline" if kind == "timeline" else "reference")
        if kind == "timeline":
            title = record["title"]
            lines = cis_timeline.article_lines(record)
            links = []
            for record_id in record.get("related", []):
                linked_database, linked = cis_reference.find_record(record_id)
                if linked:
                    links.append(("reference", linked_database, linked, f"{record_id} {linked[1]}"))
        else:
            title = record[1]
            lines = cis_reference.article_lines(record, database)
            links = [
                ("timeline", None, item, f'{item["id"]} {item["date"]} {item["title"]}')
                for item in cis_timeline.records_related_to(record[0])
            ]
            links.extend(
                ("reference", database, item, f"{item[0]} {item[1]}")
                for item in cis_reference.related_records(database, record)
            )
        ansi_scroll(title, 0.01)
        ansi_scroll("-" * len(title), 0.01)
        for line in lines:
            ansi_scroll(line, 0.005)
        if links:
            ansi_scroll("", 0.005)
            ansi_scroll("LINKED RECORDS", 0.005)
            for index, link in enumerate(links, 1):
                ansi_scroll(f"{index:>2}  {link[3]}", 0.005)
        command = input("Linked number/ID, RELATED, TIMELINE, BACK, or M ! ").strip().upper()
        if command in ("", "M"):
            return
        if command == "BACK":
            stack.pop()
            continue
        if command in ("RELATED", "TIMELINE"):
            if not links:
                ansi_scroll("No linked records are available.", 0.01)
            continue
        chosen = links[int(command) - 1] if command.isdigit() and 1 <= int(command) <= len(links) else next((link for link in links if link[3].split()[0] == command), None)
        if chosen:
            stack.append((chosen[0], chosen[1], chosen[2]))


def timeline_record_page(record):
    linked_record_browser("timeline", record)


def reference_record_page(database, record):
    linked_record_browser("reference", record, database)


def feature_service(feature_id=None):
    feature = cis_features.find(feature_id or "")
    while feature is None:
        clear()
        header_bar("features")
        ansi_scroll("COMPUSERVE HISTORICAL FEATURES", 0.01)
        bookmarks = set(current_profile.get("feature_bookmarks", []))
        read = set(current_profile.get("features_read", []))
        for index, item in enumerate(cis_features.FEATURES, 1):
            status = "BOOKMARK" if item["id"] in bookmarks else "READ" if item["id"] in read else "NEW"
            ansi_scroll(f'{index:>2} {item["id"]} [{status:<8}] {item["title"]}', 0.005)
            ansi_scroll(f'   {item["deck"]}', 0.005)
        selection = input("Feature number/ID, or M ! ").strip().upper()
        if selection == "M":
            return
        feature = cis_features.FEATURES[int(selection) - 1] if selection.isdigit() and 1 <= int(selection) <= len(cis_features.FEATURES) else cis_features.find(selection)
    index = cis_features.progress(sys.modules[__name__], feature)
    while True:
        clear()
        header_bar("features")
        ansi_scroll(feature["title"], 0.01)
        for line in cis_features.chapter_lines(feature, index):
            ansi_scroll(line, 0.005)
        cis_features.save_progress(sys.modules[__name__], feature, index)
        command = input("N/P chapter, LINKS, BOOKMARK, DOWNLOAD, BACK, or M ! ").strip().upper()
        if command == "N" and index + 1 < len(feature["chapters"]):
            index += 1
        elif command == "P" and index > 0:
            index -= 1
        elif command == "LINKS":
            chapter = feature["chapters"][index]
            choices = [("timeline", None, cis_timeline.find(item)) for item in chapter["timeline"]]
            choices.extend(("reference", *cis_reference.find_record(item)) for item in chapter["references"])
            choices = [item for item in choices if item[2]]
            for number, (_, _, item) in enumerate(choices, 1):
                label = item["title"] if isinstance(item, dict) else item[1]
                ansi_scroll(f"{number:>2} {label}", 0.005)
            selection = input("Linked record number, or RETURN ! ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(choices):
                kind, database, item = choices[int(selection) - 1]
                linked_record_browser(kind, item, database)
        elif command == "BOOKMARK":
            ansi_scroll(cis_features.toggle_bookmark(sys.modules[__name__], feature), 0.01)
        elif command == "DOWNLOAD":
            ansi_scroll(f'Feature packet prepared: {cis_features.export(sys.modules[__name__], feature).name}', 0.01)
        elif command == "BACK":
            feature = None
            return feature_service()
        elif command == "M":
            return


def timeline_service():
    selected = cis_dynamic.simulation_day()
    while True:
        records = cis_timeline.records_for_date(selected)
        clear()
        header_bar("timeline")
        ansi_scroll(f'HISTORICAL TIMELINE - {selected:%B %d, %Y}'.upper(), 0.01)
        for index, record in enumerate(records, 1):
            marker = "CONTEXT" if record["kind"] == "CONTEXT" else record["category"]
            ansi_scroll(f'{index:>2}  {marker:<11} {record["title"]}', 0.005)
        if not records:
            ansi_scroll("No curated entries for this date.", 0.01)
        command = input("Item, F/B day, C date, S search, MARK id, MARKED, DOWNLOAD, or M ! ").strip()
        upper = command.upper()
        if upper == "M":
            return
        if upper in ("F", "B"):
            day = selected.day + (1 if upper == "F" else -1)
            selected = date(1988, 12, 1 if day > 31 else 31 if day < 1 else day)
            continue
        if upper == "C":
            value = input("December date [1-31 or MM/DD/88]: ").strip()
            try:
                day = int(value) if value.isdigit() else datetime.strptime(value, "%m/%d/%y").day
                selected = date(1988, 12, day)
            except ValueError:
                ansi_scroll("Enter a date in December 1988.", 0.01)
            continue
        if upper == "S":
            matches = cis_timeline.search(input("Timeline words: ").strip())
            text_page("timeline", "TIMELINE SEARCH RESULTS", [f'{index:>2} {record["id"]} {record["date"]} {record["title"]}' for index, record in enumerate(matches, 1)] or ["No matching timeline records."])
            selection = input("Record number/ID, or RETURN ! ").strip().upper()
            record = matches[int(selection) - 1] if selection.isdigit() and 1 <= int(selection) <= len(matches) else cis_timeline.find(selection)
            if record:
                timeline_record_page(record)
            continue
        if upper.startswith("MARK "):
            ansi_scroll(cis_timeline.mark(sys.modules[__name__], upper[5:].strip()), 0.01)
            continue
        if upper == "MARKED":
            text_page("timeline", "MARKED TIMELINE RECORDS", [f'{record["id"]} {record["date"]} {record["title"]}' for record in cis_timeline.marked(sys.modules[__name__])] or ["No timeline records marked."])
            continue
        if upper == "DOWNLOAD":
            packet = cis_timeline.export_marked(sys.modules[__name__])
            ansi_scroll(f"Timeline packet prepared: {packet.name}" if packet else "No timeline records marked.", 0.01)
            continue
        record = records[int(command) - 1] if command.isdigit() and 1 <= int(command) <= len(records) else cis_timeline.find(upper)
        if record:
            timeline_record_page(record)


def open_go_destination(target, stack):
    """Open a resolved GO target and report whether it was recognized."""
    if target in FORUM_CATALOG:
        forum_service(target)
    elif target == "sysop":
        sysop_console()
    elif target == "profile":
        text_page("support", "PERSONAL SERVICE SUMMARY", cis_dynamic.dashboard(sys.modules[__name__]))
        profile_command = input("CANCEL ORDER number, CANCEL RES confirmation, or RETURN ! ").strip()
        if profile_command:
            ansi_scroll(cis_dynamic.cancel_member_item(sys.modules[__name__], profile_command), 0.01)
    elif target == "new":
        activity_center()
    elif target == "calendar":
        text_page("support", "PERSONAL SIMULATION CALENDAR", cis_experience.calendar_lines(sys.modules[__name__]))
    elif target == "notebook":
        text_page("support", "PERSONAL NOTEBOOK", cis_experience.notebook_lines(sys.modules[__name__]))
    elif target == "downloads":
        text_page("support", "DOWNLOAD CENTER", cis_experience.download_lines(sys.modules[__name__]))
    elif target == "achievements":
        text_page("support", "MEMBER ACHIEVEMENTS", cis_experience.achievement_lines(sys.modules[__name__]))
    elif target == "drafts":
        draft_center()
    elif target == "timeline":
        timeline_service()
    elif target == "weather":
        live_weather_service()
    elif target == "features":
        feature_service()
    elif target == 'magazine':
        cis_magazine.service(sys.modules[__name__])
    elif target == "case":
        cis_story.service(sys.modules[__name__])
    elif target == "people":
        text_page("support", "MEMBER RELATIONSHIPS", cis_dynamic.relationship_lines(sys.modules[__name__]))
    elif target == "equipment":
        cis_ownership.service(sys.modules[__name__])
    elif target == "shareware":
        cis_shareware.service(sys.modules[__name__])
    elif target and target in screens:
        if stack[-1] != target:
            stack.append(target)
    else:
        return False
    session_state.remember_destination(target)
    return True


def choose_recent_destination():
    recent = session_state.recent_destinations
    clear()
    header_bar("main")
    ansi_scroll("RECENT DESTINATIONS", 0.01)
    if not recent:
        ansi_scroll("No destinations have been visited in this session.", 0.01)
        input("Press ENTER to return ! ")
        return None
    for index, destination in enumerate(recent, 1):
        ansi_scroll(f"{index:>2}  {destination_label(destination)}", 0.005)
    selection = input("Destination number, or M ! ").strip()
    if selection.isdigit() and 1 <= int(selection) <= len(recent):
        return recent[int(selection) - 1]
    return None


def navigate(show_briefing=False):
    with navigation_prompts(sys.modules[__name__]):
        initial_go = None
        if show_briefing:
            try:
                today_in_1988_dashboard()
            except GoNavigation as jump:
                initial_go = jump.command
        _navigate(initial_go)


def _navigate(initial_go=None):
    session_state.reset_navigation()
    session_state.last_choices.clear()
    stack = session_state.navigation_stack
    last_choice_by_screen = session_state.last_choices

    pending_go = initial_go
    while True:
        try:
            current = stack[-1]
            global go_prompt_screen
            go_prompt_screen = current
            if pending_go is not None:
                choice, pending_go = pending_go, None
            else:
                if current in ("ibmhw_lib1", "ibmhw_lib2", "ibmhw_lib3", "ibmhw_lib4") or current in cis_communities.LIBRARIES.values():
                    library_download_screen(current)
                    stack.pop()
                    continue
                show_screen(current)
                #choice = input("Select option or type GO command: ").strip()
                choice = input(cis_prompt("main") + " ").strip()
            command = choice.upper()

            if command == "READ HISTORY":
                timeline_service()
                continue
            if command in ("READ NEW", "READ ACTIVITY"):
                activity_center()
                continue
            if command == "READ WEATHER":
                live_weather_service()
                continue

            if command in ("OFF", "BYE"):
                show_logout_summary()
                break

            if command in ("CAPTURE ON", "CAP ON"):
                set_capture(True)
                continue
            if command in ("CAPTURE OFF", "CAP OFF"):
                set_capture(False)
                continue
            if command == "BACKUP":
                archive = create_data_backup()
                ansi_scroll(f"Backup complete: {archive.name}", 0.01)
                continue
            if command == "RESTORE":
                if input("Restore newest backup [Y/N]? ").strip().upper() == "Y":
                    archive = restore_latest_backup()
                    ansi_scroll(
                        f"Restored {archive.name}. Restart to reload data."
                        if archive else "No backup is available.",
                        0.01,
                    )
                continue
            if command == "VERSION":
                version_screen()
                continue
            if command == "STATUS":
                status_screen()
                continue
            if command in ("DIAG", "DIAGNOSTICS"):
                diagnostics_screen()
                continue

            if command in ("T", "TOP", "GO TOP", "G TOP"):
                session_state.reset_navigation()
                stack = session_state.navigation_stack
                continue

            if command in ("GO BACK", "G BACK"):
                if session_state.go_back() is None:
                    ansi_scroll("Already at the top menu.", 0.01)
                continue

            if command in ("GO RECENT", "G RECENT"):
                target = choose_recent_destination()
                if target:
                    open_go_destination(target, stack)
                continue

            if command in ("H", "HELP", "?", "GO COMMAND", "G COMMAND"):
                command_help(context=current)
                continue

            if command.startswith("HELP "):
                command_help(choice[5:], current)
                continue

            if command == "COMMANDS":
                command_help(context=current, commands_only=True)
                continue

            if command.startswith("FIND "):
                results = cis_discovery.search(sys.modules[__name__], choice[5:])
                text_page("command", "SERVICE SEARCH", [f"{index:>2} {result}" for index, result in enumerate(results, 1)])
                selection = input("Result number to open, or RETURN ! ").strip()
                if selection.isdigit() and 1 <= int(selection) <= len(results):
                    cis_discovery.open_result(sys.modules[__name__], results[int(selection) - 1])
                continue

            if command.startswith("NOTE "):
                parts = choice[5:].split("|", 1)
                title, body = (parts[0], parts[1]) if len(parts) == 2 else ("MEMBER NOTE", parts[0])
                ansi_scroll(cis_experience.add_note(sys.modules[__name__], title, body, current.upper()), 0.01)
                continue

            if command == "R":
                continue

            if command in ("F", "B"):
                ansi_scroll("No forward page." if command == "F" else "No previous page.", 0.01)
                continue

            if command in ("N", "P"):
                option_keys = list(screens[current]["options"])
                previous = last_choice_by_screen.get(current)
                index = option_keys.index(previous) if previous in option_keys else -1
                index += 1 if command == "N" else -1
                if 0 <= index < len(option_keys):
                    choice = option_keys[index]
                    command = choice
                else:
                    ansi_scroll("No next selection." if command == "N" else "No previous selection.", 0.01)
                    continue

            if command.startswith("S ") and command[2:].strip() in screens[current]["options"]:
                choice = command[2:].strip()
                command = choice

            if command == "M" or choice == "0" or command in ("EXIT", "QUIT", "/EXIT"):
                if len(stack) > 1:
                    stack.pop()
                else:
                    show_logout_summary()
                    break
                continue

            if command.startswith("GO ") or command.startswith("G "):
                destination = command.split(maxsplit=1)[1]
                target = resolve_go_destination(destination, current)
                if not open_go_destination(target, stack):
                    ansi_scroll("\nUnknown GO command.\n", 0.01)
                    time.sleep(0.3)
                continue


            if choice in screens[current]["options"]:
                last_choice_by_screen[current] = choice

            if current == "forums" and choice in FORUM_CHOICES:
                forum_id = FORUM_CHOICES[choice]
                session_state.remember_destination(forum_id)
                forum_service(forum_id)
                continue

            if current == "mail" and choice in ("1", "2", "3", "4"):
                mail_service(choice)
                continue

            if current == "cb" and choice in ["1", "2", "3"]:
                cb_chat(choice)
                continue

            if current == "cb" and choice == "5":
                cb_help()
                continue

            if current == "cb" and choice == "6":
                cb_channel_directory()
                continue

            if current == "cb" and choice == "4":
                cb_private_messages()
                continue

            if current == "news" and choice in ("1", "2", "3", "4"):
                category = {
                    "1": "World", "2": "Business", "3": "Technology", "4": "Science"
                }[choice]
                news_section(category)
                continue

            if current == "news" and choice == "5":
                period_news_edition()
                continue

            if current == "news" and choice == "6":
                refresh_current_news()
                continue
            if current == 'news' and choice == '7':
                cis_magazine.service(sys.modules[__name__])
                continue

            if current == "support" and choice in screens["support"]["options"]:
                customer_support(choice)
                continue

            service_handlers = {
                "finance": finance_service, "travel": travel_service,
                "reference": reference_service, "shopping": shopping_service,
                "games": games_service,
            }
            if current in service_handlers and choice in screens[current]["options"]:
                service_handlers[current](choice)
                continue

            selected_label = screens[current]["options"].get(choice, "")
            if selected_label.startswith("$"):
                premium_service(selected_label)
                continue

            options = screens[current]["options"]
            if choice in options:
                target = OPTION_TARGETS.get(current, {}).get(choice)
                if target in screens:
                    stack.append(target)
                    session_state.remember_destination(target)
                else:
                    ansi_scroll("\nScreen exists but is not implemented yet.\n", 0.01)
                    time.sleep(0.3)
            else:
                ansi_scroll("Huh", 0.01)
                time.sleep(0.3)
        except GoNavigation as jump:
            pending_go = jump.command

# --- Run Program -------------------------------------------------------------

def main():
    """Run one local or relayed CompuServe terminal session."""
    initialize_database()
    startup_configuration()
    if not startup_options["skip_dialing"] and not modem_dial_in():
        return 0
    if not login_screen():
        return 1
    with active_session(session_state):
        try:
            choose_temporal_destination()
            create_data_backup()
            if startup_options["refresh_news"]:
                refresh_current_news()
            navigate(show_briefing=True)
        finally:
            unregister_session(BASE_DIR, live_session_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
