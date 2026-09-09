"""Shared CB channel metadata and command parsing."""

CHANNELS = {
    "1": "The Lobby - general conversation",
    "2": "The Lounge - friendly social chat",
    "3": "Technical Exchange - computers and communications",
}


def normalize_channel(value):
    value = " ".join(value.strip().upper().split())[:24]
    return value or "1"


def room(channel):
    return "cb:" + normalize_channel(channel).casefold()


def description(channel):
    key = normalize_channel(channel)
    return CHANNELS.get(key, f"Member-created channel: {key}")


def parse_command(line):
    text = line.strip()
    if not text.startswith("/"):
        return "SAY", text
    command, _, argument = text[1:].partition(" ")
    return command.upper(), argument.strip()
