"""Best-effort ntfy notifications for CompuServe session events.

Configured with the CIS_NTFY_URL environment variable holding a full ntfy
topic URL, e.g. https://ntfy.sh/compuserve-0618. When the variable is
unset, every function below is a silent no-op.

Nothing here ever raises: a dead notification server must not break a
login, delay a logout, or crash the sim. Only the standard library is
used (urllib), so there are no new dependencies.
"""

import os
import threading
import urllib.request

# Long enough for ntfy.sh under load, short enough that a hung server
# never stalls session teardown for more than a few seconds.
TIMEOUT_S = 5


def ntfy_url():
    """The configured ntfy topic URL, or None when notifications are off."""
    return os.environ.get("CIS_NTFY_URL") or None


def send(title, message, tags=(), timeout=TIMEOUT_S):
    """POST one notification. Returns True if the server accepted it.

    Synchronous with a short timeout -- safe to call on the logout path,
    where the process is about to exit and a daemon thread might never
    get to run.
    """
    url = ntfy_url()
    if not url:
        return False
    try:
        req = urllib.request.Request(
            url, data=message.encode("utf-8"), method="POST"
        )
        req.add_header("Title", title)
        if tags:
            req.add_header("Tags", ",".join(tags))
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        return True
    except Exception:
        return False


def send_async(title, message, tags=()):
    """Fire-and-forget in a daemon thread.

    Use on the login path, where the process lives on (so the thread is
    guaranteed to finish) and a slow ntfy server must not delay the
    "Access granted" scroll.
    """
    if not ntfy_url():
        return
    thread = threading.Thread(
        target=send, args=(title, message, tags), daemon=True
    )
    thread.start()


def format_duration(seconds):
    """Compact human duration: 45s, 3m 07s, 2h 05m."""
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {seconds:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m"
