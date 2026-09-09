CURRENT_SCHEMA_VERSION = 10


def migrate_data(filename, data):
    changed = False
    if filename == "profiles.json" and isinstance(data, dict):
        for profile in data.values():
            if not isinstance(profile, dict):
                continue
            defaults = {
                "joined_forums": [], "failed_logins": 0,
                "locked": False, "disabled": False,
            }
            for key, value in defaults.items():
                if key not in profile:
                    profile[key] = value.copy() if isinstance(value, list) else value
                    changed = True
    elif filename == "library_files.json" and isinstance(data, dict):
        for files in data.values():
            for file in files:
                if "status" not in file:
                    file["status"] = "approved"
                    changed = True
    elif filename == "easyplex.json" and isinstance(data, list):
        for message in data:
            if "read" not in message:
                message["read"] = False
                changed = True
    return data, changed
