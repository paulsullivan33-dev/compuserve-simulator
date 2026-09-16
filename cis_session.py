from contextvars import ContextVar
from contextlib import contextmanager
import builtins
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class SessionState:
    user_id: str | None = None
    profile: dict[str, Any] = field(default_factory=dict)
    handle: str | None = None
    started_at: float | None = None
    simulation_date: date | None = None
    top_announcements_shown: bool = False
    navigation_stack: list[str] = field(default_factory=lambda: ["main"])
    last_choices: dict[str, str] = field(default_factory=dict)
    recent_destinations: list[str] = field(default_factory=list)

    @property
    def current_screen(self):
        return self.navigation_stack[-1]

    def reset_navigation(self):
        self.navigation_stack[:] = ["main"]

    def push(self, screen):
        self.navigation_stack.append(screen)

    def pop(self):
        if len(self.navigation_stack) > 1:
            return self.navigation_stack.pop()
        return None

    def remember_choice(self, screen, choice):
        self.last_choices[screen] = choice

    def previous_choice(self, screen):
        return self.last_choices.get(screen)

    def remember_destination(self, destination, limit=10):
        if not destination or destination in ("back", "recent"):
            return
        self.recent_destinations[:] = [item for item in self.recent_destinations if item != destination]
        self.recent_destinations.insert(0, destination)
        del self.recent_destinations[limit:]

    def go_back(self):
        return self.pop()


# Active only while a signed-in member is navigating services.

_prompt_app = ContextVar("compuserve_prompt_app", default=None)

# The SessionState of the currently running session. Each OS process serves a
# single session (local console, FastAPI web terminal, and telnet gateway all
# spawn one compuserve.py per session), so this is session-scoped in practice.
# Date-aware modules read it via current_session_state() / session_simulation_date()
# instead of consulting module-level globals.
_session_state = ContextVar("compuserve_session_state", default=None)


@contextmanager
def active_session(state):
    """Mark ``state`` as the session of record for the enclosed block."""
    token = _session_state.set(state)
    try:
        yield
    finally:
        _session_state.reset(token)


def current_session_state():
    """Return the SessionState for the running session, or None outside one."""
    return _session_state.get()


def session_simulation_date():
    """Return the active session's chosen simulation date, or None.

    None means "present day": callers should fall back to their default
    behavior (the CIS_SIMULATION_DATE override, then the service's
    standard simulated calendar).
    """
    state = _session_state.get()
    return state.simulation_date if state is not None else None


class GoNavigation(Exception):
    """Unwind a service prompt without treating navigation as submitted data."""

    def __init__(self, command):
        self.command = command
        super().__init__(command)


@contextmanager
def navigation_prompts(app):
    token = _prompt_app.set(app)
    try:
        yield
    finally:
        _prompt_app.reset(token)


def read_input(prompt="", *, local_go=()):
    while True:
        app = _prompt_app.get()
        reset_pause = getattr(app, "reset_page_pause", None)
        if callable(reset_pause):
            reset_pause()
        value = builtins.input(prompt)
        match = re.fullmatch(r"(?:GO|G)(?:\s+(.*))?", value.strip(), re.IGNORECASE)
        if app is None or not match:
            return value
        destination = (match.group(1) or "").strip().upper()
        if destination in local_go:
            return value
        context = getattr(app, "go_prompt_screen", app.session_state.current_screen)
        target = app.resolve_go_destination(destination, context) if destination else None
        if destination in ("TOP", "COMMAND", "BACK", "RECENT"):
            raise GoNavigation("GO " + destination)
        if target:
            # Resolve relative page numbers at the originating prompt.
            raise GoNavigation("GO " + destination if not destination.isdigit() else "GO " + app.page_names.get(target, destination))
        app.ansi_scroll("Unknown GO destination. Enter GO followed by a service name or page address.", 0.01)
