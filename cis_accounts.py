"""Account creation, password management, and authentication."""
import re

from cis_session import read_input as input

WELCOME_BODY = (
    "Welcome to the CompuServe Information Service. Enter GO COMMAND for commands, "
    "GO NEW for current activity, or enter GO HELP, choose 1 Tour/Find a Topic, then "
    "1 Tour for a guided first-call tour. Your Calendar, Notebook, Download Center, "
    "achievements, travel arrangements, catalog orders, and fictional portfolio remain "
    "available on later calls."
)


def load_profile(app, user_id):
    if user_id not in app.profiles:
        app.profiles[user_id] = {"last_handle": None}
    app.current_profile = app.profiles[user_id]
    return app.current_profile


def set_password(app, profile, prompt="New password: "):
    first = app.password_input(prompt)
    second = app.password_input("Retype password: ")
    if first != second:
        app.ansi_scroll("Passwords do not match.", 0.01)
        return False
    try:
        profile["password_hash"] = app.hash_password(first)
    except ValueError as exc:
        app.ansi_scroll(str(exc), 0.01)
        return False
    profile.update({"failed_logins": 0, "locked": False})
    app.save_profiles()
    return True


def _new_profile(app):
    return {"last_handle": None, "baud": app.connection_baud, "columns": app.SCREEN_WIDTH, "joined_forums": []}


def _send_welcome_mail(app, user_id):
    app.cis_dynamic.schedule_event(app, "mail", {"to": user_id, "from": "COMPUSERVE", "subject": "WELCOME TO COMPUSERVE", "body": WELCOME_BODY})


def next_user_id(app):
    """Allocate the next free numeric User ID (form 70000,0001)."""
    taken = set()
    for uid in app.profiles:
        match = re.fullmatch(r"(\d{5}),(\d{4})", uid)
        if match:
            taken.add(int(match.group(1) + match.group(2)))
    candidate = 710000001  # 71000,0001: first ID in the new-account pool
    while candidate in taken:
        candidate += 1
    digits = f"{candidate:09d}"
    return f"{digits[:5]},{digits[5:]}"


def register_new_account(app):
    """Give a first-time visitor a User ID and let them set a password.

    Returns the new User ID, or None if they abandoned password setup.
    """
    user_id = next_user_id(app)
    app.ansi_scroll(f"Your new User ID is {user_id}.", 0.01)
    app.ansi_scroll("Choose a password for this account.", 0.01)
    profile = _new_profile(app)
    app.profiles[user_id] = profile
    if not set_password(app, profile):
        app.profiles.pop(user_id, None)
        return None
    _send_welcome_mail(app, user_id)
    return user_id


def authenticate(app, user_id):
    profile = app.profiles.get(user_id)
    if profile is None:
        if input("User ID is not registered. Create account [Y/N]? ").strip().upper() != "Y":
            return False
        profile = _new_profile(app)
        app.profiles[user_id] = profile
        if not set_password(app, profile):
            app.profiles.pop(user_id, None)
            return False
        _send_welcome_mail(app, user_id)
        return True
    if profile.get("disabled"):
        app.ansi_scroll("Account disabled. Contact the SysOp.", 0.01)
        return False
    if profile.get("locked"):
        app.ansi_scroll("Account locked. Contact the SysOp.", 0.01)
        return False
    if not profile.get("password_hash"):
        app.ansi_scroll("A local password must be established for this legacy account.", 0.01)
        return set_password(app, profile)
    for _ in range(3):
        if app.verify_password(app.password_input("Password: "), profile["password_hash"]):
            profile["failed_logins"] = 0
            app.save_profiles()
            return True
        app.ansi_scroll("Invalid password.", 0.01)
    profile["failed_logins"] = profile.get("failed_logins", 0) + 3
    profile["locked"] = True
    app.save_profiles()
    app.ansi_scroll("Account locked after three failed attempts.", 0.01)
    return False
