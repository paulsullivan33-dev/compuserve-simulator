PRESETS = {
    "C64": {"baud": 1200, "columns": 40, "display_mode": "scroll"},
    "IBM": {"baud": 1200, "columns": 80, "display_mode": "scroll"},
    "MAC": {"baud": 2400, "columns": 80, "display_mode": "screen"},
}

DEFAULTS = {
    "baud": 1200,
    "columns": 80,
    "display_mode": "scroll",
    "skip_dialing": False,
    "connection_mode": "clean",
    "sound": False,
    "page_pause": False,
    "refresh_news": False,
    "fast_mode": False,
    "customized": False,
}


def merged_settings(saved=None):
    settings = dict(DEFAULTS)
    if isinstance(saved, dict):
        settings.update({key: value for key, value in saved.items() if key in DEFAULTS})
    return settings


def apply_preset(settings, preset):
    values = PRESETS.get(preset.upper())
    if not values:
        return False
    settings.update(values)
    settings["customized"] = True
    return True
