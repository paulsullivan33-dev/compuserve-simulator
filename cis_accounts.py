"""Account creation, password management, and authentication."""
from cis_session import read_input as input


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


def authenticate(app, user_id):
    profile = app.profiles.get(user_id)
    if profile is None:
        if input("User ID is not registered. Create account [Y/N]? ").strip().upper() != "Y":
            return False
        profile = {"last_handle": None, "baud": app.connection_baud, "columns": app.SCREEN_WIDTH, "joined_forums": []}
        app.profiles[user_id] = profile
        if not set_password(app, profile):
            app.profiles.pop(user_id, None)
            return False
        app.cis_dynamic.schedule_event(app, "mail", {"to": user_id, "from": "COMPUSERVE", "subject": "WELCOME TO COMPUSERVE", "body": "Welcome to the CompuServe Information Service. Enter GO COMMAND for commands, GO NEW for current activity, or enter GO HELP, choose 1 Tour/Find a Topic, then 1 Tour for a guided first-call tour. Your Calendar, Notebook, Download Center, achievements, travel arrangements, catalog orders, and fictional portfolio remain available on later calls."})
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
