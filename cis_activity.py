"""Append-only activity log for the CompuServe simulator.

Both the telnet gateway (telnet_app.py) and the sim subprocess
(compuserve.py) record events here so the sysop can review who connected,
who logged in, and who failed — e.g. ``tail -f activity.log`` or
``python3 cis_activity.py --tail 50``.

One JSON object per line. Writes are best-effort and never raise, so
logging can never break a session. Concurrent writers are safe: every
event is a single O_APPEND write.

The log location defaults to ``activity.log`` next to this file and can be
moved with the ``CIS_ACTIVITY_LOG`` environment variable.
"""

import json
import os
import time

DEFAULT_NAME = "activity.log"


def log_path():
    """Return the activity log path (CIS_ACTIVITY_LOG or ./activity.log)."""
    override = os.environ.get("CIS_ACTIVITY_LOG")
    if override:
        return override
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_NAME)


def log_event(kind, *, session_id=None, client_ip=None, user_id=None, detail=None):
    """Append one activity event. Never raises.

    kind: short snake_case name, e.g. "session_connected", "login_failed".
    detail: optional JSON-serializable extra info (never a password).
    """
    try:
        event = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            "event": kind,
        }
        if session_id:
            event["session_id"] = session_id
        if client_ip:
            event["client_ip"] = client_ip
        if user_id:
            event["user_id"] = user_id
        if detail is not None:
            event["detail"] = detail
        with open(log_path(), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, default=str) + "\n")
    except Exception:
        pass


def read_events(path=None, limit=200):
    """Return the most recent events as dicts (newest last). Skips bad lines."""
    events = []
    try:
        with open(path or log_path(), encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return events[-limit:]


def _format(event):
    parts = [event.get("ts", "?"), event.get("event", "?")]
    if event.get("user_id"):
        parts.append("user=" + str(event["user_id"]))
    if event.get("client_ip"):
        parts.append("ip=" + str(event["client_ip"]))
    if event.get("session_id"):
        parts.append("session=" + str(event["session_id"])[:8])
    if event.get("detail") is not None:
        parts.append("detail=" + json.dumps(event["detail"], default=str))
    return " ".join(parts)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Review the CompuServe activity log.")
    parser.add_argument("--tail", type=int, default=50, help="show the last N events")
    parser.add_argument("--event", help="only show this event kind")
    args = parser.parse_args(argv)
    events = read_events(limit=args.tail if args.tail > 0 else 10**9)
    if args.event:
        events = [e for e in events if e.get("event") == args.event]
    for event in events:
        print(_format(event))


if __name__ == "__main__":
    main()
