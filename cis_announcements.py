"""Scheduled, targeted Sysop announcements."""

from datetime import datetime, time


PRIORITIES = {"NORMAL", "IMPORTANT", "EMERGENCY"}


def _parse_date(value, end=False):
    value = value.strip()
    if not value or value.upper() in ({"NOW"} if not end else {"NONE"}):
        return None
    selected = datetime.strptime(value, "%m/%d/%y").date()
    return datetime.combine(selected, time.max if end else time.min).isoformat(timespec="minutes")


def create(app, title, body, priority="NORMAL", target="ALL", starts="NOW", expires="NONE"):
    priority = priority.strip().upper() or "NORMAL"
    if priority not in PRIORITIES:
        raise ValueError("Priority must be NORMAL, IMPORTANT, or EMERGENCY.")
    start_at, expires_at = _parse_date(starts), _parse_date(expires, end=True)
    result = {}

    def add(state):
        records = state.setdefault("announcements", [])
        number = max((record.get("id", 0) for record in records), default=0) + 1
        record = {"id": number, "title": title.strip()[:120], "body": body.strip()[:5000], "priority": priority, "target": target.strip().upper() or "ALL", "starts_at": start_at, "expires_at": expires_at, "created_at": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes"), "expired": False, "read_by": []}
        records.append(record)
        result.update(record)

    if not title.strip() or not body.strip():
        raise ValueError("An announcement requires a title and message.")
    app.update_json_atomic("dynamic_state.json", {}, add)
    return result


def active(app, user_id, include_read=True):
    now = app.cis_dynamic.simulation_datetime()
    records = app.cis_dynamic.load_state(app).get("announcements", [])
    result = []
    for record in records:
        start = datetime.fromisoformat(record["starts_at"]) if record.get("starts_at") else None
        end = datetime.fromisoformat(record["expires_at"]) if record.get("expires_at") else None
        target = record.get("target", "ALL")
        if record.get("expired") or (start and now < start) or (end and now > end):
            continue
        if target not in ("ALL", user_id):
            continue
        if not include_read and user_id in record.get("read_by", []):
            continue
        result.append(record)
    return sorted(result, key=lambda item: ({"EMERGENCY": 0, "IMPORTANT": 1}.get(item.get("priority"), 2), item.get("id", 0)))


def mark_read(app, announcement_id, user_id):
    found = {"value": False}

    def update(state):
        record = next((item for item in state.setdefault("announcements", []) if item.get("id") == announcement_id), None)
        if record:
            readers = record.setdefault("read_by", [])
            if user_id not in readers:
                readers.append(user_id)
            found["value"] = True

    app.update_json_atomic("dynamic_state.json", {}, update)
    return found["value"]


def expire(app, announcement_id):
    changed = {"value": False}

    def update(state):
        record = next((item for item in state.setdefault("announcements", []) if item.get("id") == announcement_id), None)
        if record:
            record["expired"] = True
            changed["value"] = True

    app.update_json_atomic("dynamic_state.json", {}, update)
    return changed["value"]


def all_records(app):
    return list(app.cis_dynamic.load_state(app).get("announcements", []))


def article_lines(record):
    return [f'PRIORITY: {record.get("priority", "NORMAL")}', f'TARGET: {record.get("target", "ALL")}', f'POSTED: {record.get("created_at", "")}', *( [f'EXPIRES: {record["expires_at"]}'] if record.get("expires_at") else []), "", record.get("body", "")]
