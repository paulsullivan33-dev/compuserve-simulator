"""Connection-time and simulated billing calculations."""

from cis_web_files import offer_download

from datetime import datetime
from pathlib import Path


def is_prime_time(now=None):
    now = now or datetime.now()
    return now.weekday() < 5 and 8 <= now.hour < 18


def connection_rate_per_hour(baud, rates, now=None):
    base = rates[baud]
    return base * 1.75 if is_prime_time(now) else base


def estimated_cost(seconds, baud, rates, now=None):
    return (seconds / 3600.0) * connection_rate_per_hour(baud, rates, now)


def format_elapsed(seconds):
    return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def record_session(app, seconds, baud, connect_charge, premium_charge):
    entry = {"id": app.live_session_id, "user_id": app.current_user_id, "date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes"), "seconds": int(seconds), "baud": int(baud), "connect_charge": round(connect_charge, 4), "premium_charge": round(premium_charge, 4)}

    def add(state):
        sessions = state.setdefault("usage_sessions", [])
        if not any(item.get("id") == entry["id"] for item in sessions):
            sessions.append(entry)
            del sessions[:-1000]

    app.update_json_atomic("dynamic_state.json", {}, add)
    return entry


def statement_lines(app, include_current=True):
    period = app.cis_dynamic.simulation_datetime().strftime("%Y-%m")
    sessions = [item for item in app.cis_dynamic.load_state(app).get("usage_sessions", []) if item.get("user_id") == app.current_user_id and str(item.get("date", "")).startswith(period)]
    if include_current and not any(item.get("id") == app.live_session_id for item in sessions):
        seconds = app.get_elapsed_seconds()
        sessions.append({"id": "CURRENT", "date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes"), "seconds": seconds, "baud": app.connection_baud, "connect_charge": app.get_estimated_cost(seconds), "premium_charge": app.premium_charges})
    minutes = sum((item.get("seconds", 0) + 59) // 60 for item in sessions)
    connect = sum(item.get("connect_charge", 0) for item in sessions)
    premium = sum(item.get("premium_charge", 0) for item in sessions)
    lines = ["COMPUSERVE INFORMATION SERVICE", "FICTIONAL MEMBER USAGE STATEMENT", f"MEMBER: {app.current_user_id}", f"STATEMENT PERIOD: {period}", "", "DATE/TIME         BAUD  CONNECT   PREMIUM   TIME"]
    for item in sessions[-50:]:
        lines.append(f'{item.get("date", "")[:16]:<16} {item.get("baud", 0):>4}  ${item.get("connect_charge", 0):>7.2f}  ${item.get("premium_charge", 0):>7.2f}  {format_elapsed(item.get("seconds", 0))}')
    lines.extend(["", f"SESSIONS                  {len(sessions):>8}", f"MINUTES ONLINE            {minutes:>8}", f"CONNECT CHARGES           ${connect:>7.2f}", f"PREMIUM CHARGES           ${premium:>7.2f}", f"TOTAL FICTIONAL CHARGES   ${connect + premium:>7.2f}", "", "Telephone toll charges are not included.", "This statement is part of a historical simulation."])
    return lines


def export_statement(app):
    destination = Path(app.BASE_DIR) / "downloads" / f'BILL{(app.current_user_id or "GUEST").replace(",", "")}.TXT'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text("\r\n".join(statement_lines(app)), encoding="ascii", errors="replace")
    offer_download(destination)
    return destination

