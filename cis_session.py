from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    user_id: str | None = None
    profile: dict[str, Any] = field(default_factory=dict)
    handle: str | None = None
    started_at: float | None = None
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
