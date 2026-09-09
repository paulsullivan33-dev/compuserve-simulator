def account_rows(profiles):
    rows = []
    for user_id, profile in sorted(profiles.items()):
        state = "DISABLED" if profile.get("disabled") else "LOCKED" if profile.get("locked") else "ACTIVE"
        role = "SYSOP" if profile.get("is_sysop") else "MEMBER"
        rows.append((user_id, role, state))
    return rows


def unlock_account(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return False
    profile["locked"] = False
    profile["failed_logins"] = 0
    return True


def toggle_disabled(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return None
    profile["disabled"] = not profile.get("disabled", False)
    return profile["disabled"]


def reset_password(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return False
    profile.pop("password_hash", None)
    profile["locked"] = False
    profile["failed_logins"] = 0
    return True


def pending_uploads(library_files):
    return [
        (section, file)
        for section, files in library_files.items()
        for file in files
        if file.get("status") == "pending"
    ]


def set_upload_status(library_files, number, status):
    if status not in ("approved", "rejected"):
        raise ValueError("Invalid upload status")
    for files in library_files.values():
        for file in files:
            if file.get("number") == number:
                file["status"] = status
                return True
    return False
