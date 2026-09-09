import json
import random
from pathlib import Path
from tempfile import NamedTemporaryFile

INPUT_FILE = Path(__file__).resolve().parent / "fake_lines.json"

# Word pools for random chat-like sentences
NOUNS = [
    "idea", "project", "thing", "message", "plan", "update", "note",
    "situation", "moment", "question", "thought", "problem", "option"
]

VERBS = [
    "check", "see", "try", "fix", "look at", "figure out", "explain",
    "review", "start", "finish", "consider", "adjust", "update"
]

ADJECTIVES = [
    "weird", "quick", "random", "strange", "simple", "odd",
    "unexpected", "helpful", "interesting", "small", "new"
]

PHRASES = [
    "if you want", "when you get a second", "before we move on",
    "just letting you know", "in case it matters", "for now",
    "whenever you're ready", "if that works for you"
]

def generate_chat_sentence():
    noun = random.choice(NOUNS)
    verb = random.choice(VERBS)
    adj = random.choice(ADJECTIVES)
    phrase = random.choice(PHRASES)

    # Build a natural-sounding chat reply
    return f"Let me {verb} that {adj} {noun} {phrase}."

def append_random_chat_line():
    # Load existing JSON array or start fresh
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except FileNotFoundError:
        data = []
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Refusing to overwrite malformed JSON: {INPUT_FILE}") from exc

    # Generate one random chat-like reply
    new_line = generate_chat_sentence()

    # Append it
    data.append(new_line)

    # Write back out
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=INPUT_FILE.parent, delete=False, suffix=".tmp"
    ) as f:
        temporary = Path(f.name)
        json.dump(data, f, indent=4)
    temporary.replace(INPUT_FILE)

    print(f"Appended: {new_line}")

if __name__ == "__main__":
    append_random_chat_line()
