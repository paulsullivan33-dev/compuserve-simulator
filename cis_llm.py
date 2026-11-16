"""Optional local-model replies for chat and service feedback.

An add-on: when no configuration file exists, every call here returns None
without touching the network, and the simulator keeps its scripted replies.
Operators who have an Ollama server turn it on by creating ``llm_config.json``
beside ``compuserve.py`` (or naming another file in the ``CIS_LLM_CONFIG``
environment variable). ``llm_config.example.json`` documents the format.
The real file is local configuration: it is ignored by git and never shipped
in a release.

Each *role* names one place a service answers a member (CB chat, customer
service feedback, and so on) and gives the Ollama model and the system prompt
for it. A role that is missing or disabled falls back to the scripted reply.

Nothing here raises to the caller. A slow, missing or failing model server
returns None, and so does a call made too soon after the previous one from
the same session. Replies are cleaned for a 1988 terminal: plain ASCII, no
control or escape characters, one paragraph, and cut to the role's length.

Only the standard library is used (urllib), so there are no new dependencies.

Check a configuration from the command line:  python cis_llm.py --check
"""
from __future__ import annotations

import contextvars
import json
import os
import re
import sys
import threading
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_NAME = "llm_config.json"
EXAMPLE_NAME = "llm_config.example.json"

ROLES = {
    "cb_chat": "CB Simulator: a simulated member answers a live user's message",
    "customer_service": "Customer Service: a reply to member feedback (GO FEEDBACK)",
    "representative": "Ask a representative (Travel, Finance, Store): the EasyPlex answer",
    "warranty": "Equipment warranty case: the vendor's EasyPlex acknowledgement",
}

DEFAULTS = {
    "ollama_url": "http://localhost:11434",
    "timeout_seconds": 20,
    "min_seconds_between_calls": 2,
    "max_input_chars": 1000,
    "keep_alive": "15m",
}
ROLE_DEFAULTS = {
    "enabled": True,
    "max_chars": 400,
    "temperature": 0.8,
    "context_lines": 10,
    "multiline": False,     # True keeps paragraph breaks (for EasyPlex mail replies)
}

_lock = threading.Lock()
_last_call = {}          # role -> monotonic time of the last model call
_cache = {"path": None, "mtime": None, "config": None}


def config_path():
    override = os.environ.get("CIS_LLM_CONFIG")
    return Path(override) if override else ROOT / CONFIG_NAME


def load_config(path=None):
    """The merged configuration, or None when the add-on is off.

    Raises ValueError for a file that exists but is unusable, so --check can
    say why; reply() turns that into None.
    """
    path = Path(path) if path else config_path()
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("the configuration must be a JSON object")
    if raw.get("enabled") is False:
        return None
    config = dict(DEFAULTS)
    config.update({key: value for key, value in raw.items() if key in DEFAULTS})
    roles = raw.get("roles")
    if not isinstance(roles, dict) or not roles:
        raise ValueError('"roles" must be an object naming at least one role')
    config["roles"] = {}
    for name, role in roles.items():
        if name not in ROLES:
            raise ValueError(f'unknown role "{name}"; known roles: {", ".join(sorted(ROLES))}')
        if not isinstance(role, dict):
            raise ValueError(f'role "{name}" must be an object')
        merged = dict(ROLE_DEFAULTS)
        merged.update(role)
        for key in ("model", "prompt"):
            if not isinstance(merged.get(key), str) or not merged[key].strip():
                raise ValueError(f'role "{name}" needs a non-empty "{key}"')
        config["roles"][name] = merged
    if not isinstance(config["keep_alive"], (str, int)):
        raise ValueError('"keep_alive" must be a duration such as "15m", or seconds')
    for key in ("timeout_seconds", "min_seconds_between_calls", "max_input_chars"):
        if not isinstance(config[key], (int, float)) or config[key] < 0:
            raise ValueError(f'"{key}" must be a number of 0 or more')
    return config


def _current_config():
    """Cached by file modification time, so edits apply without a restart."""
    path = config_path()
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    config = _cache["config"]
    if _cache["path"] != path or _cache["mtime"] != mtime:
        try:
            config = load_config(path)
        except (OSError, ValueError):
            config = None
        _cache.update(path=path, mtime=mtime, config=config)
    return config


def role_config(role):
    config = _current_config()
    if not config:
        return None, None
    settings = config["roles"].get(role)
    if not settings or not settings.get("enabled", True):
        return None, None
    return config, settings


def enabled(role):
    return role_config(role)[1] is not None


class _Blank(dict):
    def __missing__(self, key):
        return ""


def _ascii(text):
    swaps = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "--",
             "…": "...", " ": " "}
    text = "".join(swaps.get(ch, ch) for ch in text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return text


def clean(text, max_chars, speaker=None, multiline=False):
    """Make model output safe and period-appropriate for a terminal.

    multiline keeps paragraph breaks (for mail); otherwise one line.
    """
    text = re.sub(r"<think>.*?</think>", " ", text or "", flags=re.S | re.I)
    text = _ascii(text)
    text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", " ", text)       # ANSI sequences
    text = re.sub(r"^\s*subject:[^\n]*\n", "", text, flags=re.I)  # a model-written mail header
    text = re.sub(r"[*_`#]+", "", text)                           # markdown
    paragraphs = re.split(r"\n\s*\n", text) if multiline else [text]
    paragraphs = [" ".join(re.sub(r"[\x00-\x1f\x7f]", " ", part).split()) for part in paragraphs]
    text = "\n\n".join(part for part in paragraphs if part)
    if speaker:
        text = re.sub(rf"^(<?{re.escape(speaker)}>?\s*[:>-]\s*)", "", text, flags=re.I)
    text = text.strip().strip('"').strip()
    if len(text) > max_chars:
        cut = text[:max_chars]
        end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
        text = cut[:end + 1] if end >= max_chars // 2 else cut.rsplit(" ", 1)[0] + "..."
    return text or None


def _post(url, body, timeout):
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def build_messages(settings, text, persona, context, max_input):
    system = settings["prompt"].format_map(_Blank({k: str(v) for k, v in (persona or {}).items()}))
    lines = []
    keep = int(settings.get("context_lines", 10))
    if context and keep:
        lines.append("Recent conversation:")
        lines.extend(str(line)[:300] for line in list(context)[-keep:])
        lines.append("")
    who = (persona or {}).get("member")
    lines.append(f"Message from {who}:" if who else "Message:")
    lines.append(str(text)[:max_input])
    return [{"role": "system", "content": system}, {"role": "user", "content": "\n".join(lines)}]


def reply(role, text, persona=None, context=None, post=None, clock=time.monotonic):
    """A model reply for `role`, or None to use the scripted reply instead.

    persona: values for {placeholders} in the role's prompt, e.g. handle,
             channel, member, department, product. "member" also labels the
             message in the request.
    context: recent lines (chat scrollback), oldest first.
    """
    try:
        config, settings = role_config(role)
        if not config or not settings or not str(text or "").strip():
            return None
        with _lock:
            now = clock()
            last = _last_call.get(role)
            if last is not None and now - last < config["min_seconds_between_calls"]:
                return None
            _last_call[role] = now
        body = {
            "model": settings["model"],
            "messages": build_messages(settings, text, persona, context, int(config["max_input_chars"])),
            "stream": False,
            "think": False,
            "keep_alive": settings.get("keep_alive", config["keep_alive"]),
            "options": {"temperature": settings.get("temperature", 0.8),
                        "num_predict": max(32, int(settings["max_chars"]) // 2)},
        }
        timeout = settings.get("timeout_seconds", config["timeout_seconds"])
        data = (post or _post)(config["ollama_url"].rstrip("/") + "/api/chat", body, timeout)
        content = (data.get("message") or {}).get("content", "")
        return clean(content, int(settings["max_chars"]), speaker=(persona or {}).get("handle"),
                     multiline=bool(settings.get("multiline")))
    except Exception:
        return None


def reply_later(role, text, apply, persona=None, context=None):
    """Ask the model in the background; call apply(answer) only with a usable answer.

    For replies that arrive later anyway (EasyPlex mail): the caller schedules
    the scripted version first, and apply() swaps in the model's text if it is
    ready before delivery. The member never waits. Returns the started thread,
    or None when the role is off. The thread is a daemon, so a session that
    ends first simply keeps the scripted text.
    """
    if not enabled(role):
        return None
    session = contextvars.copy_context()

    def work():
        answer = reply(role, text, persona=persona, context=context)
        if answer:
            try:
                apply(answer)
            except Exception:
                pass

    thread = threading.Thread(target=session.run, args=(work,), name=f"cis-llm-{role}", daemon=True)
    thread.start()
    return thread


def check(path=None, get=None):
    """Lines describing the configuration and whether its models exist."""
    path = Path(path) if path else config_path()
    if not path.is_file():
        return [f"{path}: not found -- local-model replies are off (scripted replies are used).",
                f"To turn them on, copy {EXAMPLE_NAME} to {CONFIG_NAME} and edit it."]
    try:
        config = load_config(path)
    except (OSError, ValueError) as error:
        return [f"{path}: NOT USABLE -- {error}. Scripted replies are used until it is fixed."]
    if config is None:
        return [f"{path}: \"enabled\" is false -- local-model replies are off."]
    lines = [f"{path}: server {config['ollama_url']}"]
    available = None
    try:
        fetch = get or (lambda url: json.loads(urllib.request.urlopen(url, timeout=10).read().decode("utf-8")))
        tags = fetch(config["ollama_url"].rstrip("/") + "/api/tags")
        available = {model.get("name") for model in tags.get("models", [])}
    except Exception as error:
        lines.append(f"  server not reachable ({type(error).__name__}); replies will fall back to scripts")
    for name in ROLES:
        settings = config["roles"].get(name)
        if not settings:
            lines.append(f"  {name:<17} not configured (scripted)")
            continue
        state = "on " if settings.get("enabled", True) else "off"
        found = "" if available is None else ("  model OK" if settings["model"] in available or
                                              f"{settings['model']}:latest" in available else "  MODEL NOT FOUND")
        lines.append(f"  {name:<17} {state} {settings['model']}{found}")
    return lines


if __name__ == "__main__":
    if sys.argv[1:] != ["--check"]:
        print("usage: python cis_llm.py --check")
        sys.exit(2)
    print("\n".join(check()))
