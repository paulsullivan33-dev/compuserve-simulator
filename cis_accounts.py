"""Account creation, password management, and authentication."""
import os
import re
from datetime import datetime, timedelta, timezone

import cis_activity

from cis_session import read_input as input

# Failed-password lockouts expire on their own; a manual sysop unlock
# (cis_sysop.unlock_account) is only needed to clear one early.
LOCKOUT_MINUTES = 15

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
    profile.pop("locked_at", None)
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


def _activity(app, kind, user_id=None, detail=None):
    """Record an auth-related event in the activity log (never raises)."""
    cis_activity.log_event(
        kind,
        session_id=getattr(app, "live_session_id", None),
        client_ip=os.environ.get("CIS_CLIENT_IP") or None,
        user_id=user_id,
        detail=detail,
    )


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
        _activity(app, "register_abandoned", user_id=user_id)
        return None
    _send_welcome_mail(app, user_id)
    _activity(app, "register", user_id=user_id, detail={"method": "new"})
    return user_id


def _lockout_expired(profile):
    """True when a failed-password lock may be lifted without a sysop.

    Locks recorded before lock timestamps existed (or with an unreadable
    timestamp) are treated as expired so they clear on the next attempt.
    """
    locked_at = profile.get("locked_at")
    if not locked_at:
        return True
    try:
        locked_time = datetime.fromisoformat(locked_at)
    except (TypeError, ValueError):
        return True
    if locked_time.tzinfo is None:
        locked_time = locked_time.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - locked_time >= timedelta(minutes=LOCKOUT_MINUTES)


def authenticate(app, user_id):
    profile = app.profiles.get(user_id)
    if profile is None:
        if input("User ID is not registered. Create account [Y/N]? ").strip().upper() != "Y":
            return False
        profile = _new_profile(app)
        app.profiles[user_id] = profile
        if not set_password(app, profile):
            app.profiles.pop(user_id, None)
            _activity(app, "register_abandoned", user_id=user_id)
            return False
        _send_welcome_mail(app, user_id)
        _activity(app, "register", user_id=user_id, detail={"method": "unknown_id"})
        return True
    if profile.get("disabled"):
        _activity(app, "login_denied", user_id=user_id, detail={"reason": "disabled"})
        app.ansi_scroll("Account disabled. Contact the SysOp.", 0.01)
        return False
    if profile.get("locked"):
        if _lockout_expired(profile):
            profile["locked"] = False
            profile.pop("locked_at", None)
            profile["failed_logins"] = 0
            app.save_profiles()
            _activity(app, "account_unlocked", user_id=user_id,
                      detail={"reason": "lockout_expired"})
        else:
            _activity(app, "login_denied", user_id=user_id, detail={"reason": "locked"})
            app.ansi_scroll("Account locked. Contact the SysOp.", 0.01)
            return False
    if not profile.get("password_hash"):
        app.ansi_scroll("A local password must be established for this legacy account.", 0.01)
        return set_password(app, profile)
    for attempt in range(1, 4):
        if app.verify_password(app.password_input("Password: "), profile["password_hash"]):
            profile["failed_logins"] = 0
            app.save_profiles()
            return True
        _activity(app, "login_failed", user_id=user_id, detail={"attempt": attempt})
        app.ansi_scroll("Invalid password.", 0.01)
    profile["failed_logins"] = profile.get("failed_logins", 0) + 3
    profile["locked"] = True
    profile["locked_at"] = datetime.now(timezone.utc).isoformat()
    app.save_profiles()
    _activity(app, "account_locked", user_id=user_id)
    app.ansi_scroll("Account locked after three failed attempts.", 0.01)
    return False
