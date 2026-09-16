"""Classic Eliza Rogerian psychotherapist engine for the CompuServe simulator.

A faithful-but-original reimplementation of the classic Eliza pattern-matching
therapist: ranked keywords, decomposition patterns with ``*`` wildcards,
reassembly rule lists chosen by deterministic round-robin, pronoun reflection
(I<->you, my<->your, me<->you, am<->are, ...), a memory queue that surfaces
"earlier you said ..." callbacks, and quit-word detection.

Pure content-plus-logic module: no I/O, no filesystem access, no external
dependencies. State is a plain JSON-serializable dict so a session can persist
it (e.g. in SQLite) between turns.

Public API:
  new_state() -> fresh state dict (JSON-serializable)
  respond(text, state) -> (reply, new_state) tuple
  is_quit(text) -> bool (True for bye/quit/exit/goodbye as standalone words)
  OPENING -> greeting line a session may print before the first turn
"""

import re

OPENING = "How do you do. Please tell me your problem."

GOODBYES = [
    "Goodbye. It was nice talking to you.",
    "Goodbye. I hope our talk helped a little.",
    "We are out of time for today. Goodbye.",
]

# Fallbacks when no keyword matches and no memory callback fires.
NOTHING_MATCHED = [
    "Please go on.",
    "I see.",
    "Can you elaborate on that?",
    "What does that suggest to you?",
    "I understand.",
    "Tell me more about that.",
    "Does that trouble you?",
    "Go on, I am listening.",
]

# Memory callback templates; (1) is the remembered fragment.
MEMORY_TEMPLATES = [
    "Earlier you mentioned (1). Tell me more about that.",
    "You said before that (1). How does that make you feel?",
    "Let us go back to what you said about (1).",
]

# A stored memory fires on a no-keyword turn when turns % MEMORY_EVERY == 0.
MEMORY_EVERY = 3

QUIT_RE = re.compile(r"\b(bye|quit|exit|goodbye)\b", re.IGNORECASE)

# Word-level pronoun reflection, applied in a single pass (no chaining).
REFLECTIONS = {
    "i": "you",
    "you": "i",
    "me": "you",
    "my": "your",
    "your": "my",
    "yours": "mine",
    "mine": "yours",
    "am": "are",
    "are": "am",
    "was": "were",
    "were": "was",
    "myself": "yourself",
    "yourself": "myself",
    "we": "you",
    "us": "you",
    "our": "your",
    "ours": "yours",
}

# Contractions expanded before punctuation is stripped, so "I'm sad"
# behaves like "I am sad".
CONTRACTIONS = {
    "I'M": "I AM",
    "YOU'RE": "YOU ARE",
    "HE'S": "HE IS",
    "SHE'S": "SHE IS",
    "IT'S": "IT IS",
    "THAT'S": "THAT IS",
    "THERE'S": "THERE IS",
    "WHAT'S": "WHAT IS",
    "WHO'S": "WHO IS",
}

# ---------------------------------------------------------------------------
# Rule table: (keyword, rank, [(decomposition, [reassembly rules], memory)])
# decomposition is a space-separated pattern where "*" matches zero or more
# words; captured groups are 1-based and referenced as (1), (2), ... in rules.
# memory is None or (group_index, prefix) -- the reflected capture is stored
# for later "earlier you said ..." callbacks.
# ---------------------------------------------------------------------------

KEYWORDS = [
    ("HELLO", 11, [
        ("*", [
            "How do you do. Please tell me your problem.",
            "Hello. What brings you here today?",
            "Hi. Tell me what is on your mind.",
        ], None),
    ]),
    ("I AM", 10, [
        ("* I AM", [
            "Why do you tell me that about yourself?",
            "What makes you say that?",
        ], None),
        ("* I AM *", [
            "Why do you say you are (2)?",
            "How long have you been (2)?",
            "Do you enjoy being (2)?",
            "Does it bother you to be (2)?",
        ], None),
    ]),
    ("I FEEL", 10, [
        ("* I FEEL *", [
            "Do you often feel (2)?",
            "What do you think feeling (2) accomplishes?",
            "Tell me more about feeling (2).",
            "When do you usually feel (2)?",
        ], None),
    ]),
    ("CAN YOU", 10, [
        ("* CAN YOU *", [
            "You believe I can (2), don't you?",
            "You want me to be able to (2).",
            "Perhaps you would like to be able to (2) yourself.",
            "Have you asked anyone else if they can (2)?",
        ], None),
    ]),
    ("CAN I", 10, [
        ("* CAN I *", [
            "Whether or not you can (2) depends on you more than on me.",
            "Do you want to be able to (2)?",
            "Perhaps you don't really want to (2).",
        ], None),
    ]),
    ("I THINK", 10, [
        ("* I THINK *", [
            "Do you really think so?",
            "But you are not sure you (2).",
            "Do you doubt that you (2)?",
            "What makes you think (2)?",
        ], None),
    ]),
    ("I WANT", 9, [
        ("* I WANT *", [
            "What would you do if you got (2)?",
            "Why do you want (2)?",
            "Suppose you got (2). What then?",
            "What if you never got (2)?",
            "What would getting (2) mean to you?",
        ], None),
    ]),
    ("I NEED", 9, [
        ("* I NEED *", [
            "Would it really help you to get (2)?",
            "Are you sure you need (2)?",
            "What would getting (2) mean to you?",
            "Is (2) something you have always needed?",
        ], None),
    ]),
    ("BECAUSE", 9, [
        ("* BECAUSE *", [
            "Is that the real reason?",
            "Don't any other reasons come to mind?",
            "Does that reason seem to explain anything else?",
            "What other reasons might there be?",
        ], None),
    ]),
    ("WHY", 9, [
        ("* WHY *", [
            "Why do you ask?",
            "Does that question interest you?",
            "What is it you really want to know?",
            "What answer would please you most?",
            "What do you think?",
        ], None),
    ]),
    ("YOU ARE", 9, [
        ("* YOU ARE *", [
            "What makes you think I am (2)?",
            "Does it please you to believe I am (2)?",
            "Do you sometimes wish you were (2)?",
            "Perhaps you would like to be (2).",
        ], None),
    ]),
    ("SAD", 9, [
        ("*", [
            "I am sorry to hear that. Tell me what is making you sad.",
            "Do you think talking about it will help you feel less sad?",
            "Have you felt this way for long?",
        ], None),
    ]),
    ("HAPPY", 9, [
        ("*", [
            "What is making you happy right now?",
            "Can you explain why you are suddenly happy?",
            "Does someone in particular make you happy?",
        ], None),
    ]),
    ("DONT", 8, [
        ("* DONT *", [
            "Don't you really (2)?",
            "Why don't you (2)?",
            "Do you wish to be able to (2)?",
            "Does that trouble you?",
        ], None),
    ]),
    ("CANT", 8, [
        ("* CANT *", [
            "Do you think you should be able to (2)?",
            "If you could (2), what would you do?",
            "Have you really tried to (2)?",
            "What is stopping you from (2)?",
        ], None),
    ]),
    ("WONT", 8, [
        ("* WONT *", [
            "Why won't you (2)?",
            "Is that a decision or a habit?",
            "What would happen if you did (2)?",
        ], None),
    ]),
    ("MOTHER", 8, [
        ("*", [
            "Tell me more about your mother.",
            "Does your mother know how you feel?",
            "How do you get along with your mother?",
            "What comes to mind when you think of your mother?",
        ], None),
    ]),
    ("FATHER", 8, [
        ("*", [
            "Tell me more about your father.",
            "Does your father know how you feel?",
            "How do you get along with your father?",
            "Do you feel close to your father?",
        ], None),
    ]),
    ("AFRAID", 8, [
        ("*", [
            "What are you afraid of?",
            "Does it trouble you to be afraid?",
            "Have you been afraid for long?",
            "What do you think causes your fear?",
        ], None),
    ]),
    ("ANGRY", 8, [
        ("*", [
            "What makes you angry?",
            "Does being angry help you?",
            "Who are you angry with?",
            "How long have you felt this anger?",
        ], None),
    ]),
    ("ALONE", 8, [
        ("*", [
            "Do you often feel alone?",
            "What is it like being alone?",
            "Is being alone what bothers you?",
            "When do you feel most alone?",
        ], None),
    ]),
    ("DREAM", 8, [
        ("*", [
            "What does that dream suggest to you?",
            "Do you dream often?",
            "What persons appear in your dreams?",
            "Do you believe dreams have something to do with your problem?",
        ], None),
    ]),
    ("REMEMBER", 8, [
        ("* REMEMBER *", [
            "Do you often think of (2)?",
            "Does thinking of (2) bring anything else to mind?",
            "What in the present situation reminds you of (2)?",
            "What else does (2) remind you of?",
        ], (2, "")),
    ]),
    ("WHAT", 8, [
        ("*", [
            "Why do you ask?",
            "Does that question interest you?",
            "What do you think?",
            "What comes to mind when you ask that?",
        ], None),
    ]),
    ("HOW", 8, [
        ("*", [
            "How do you suppose?",
            "Perhaps you can answer your own question.",
            "What is it you are really asking?",
            "Why do you ask how?",
        ], None),
    ]),
    ("SORRY", 7, [
        ("*", [
            "There is no need to apologize.",
            "What feelings do you have when you apologize?",
            "Apologies are not necessary here.",
            "What makes you say you are sorry?",
        ], None),
    ]),
    ("LOVE", 7, [
        ("* LOVE *", [
            "What does love mean to you?",
            "Do you love someone in particular?",
            "Tell me more about this feeling of love.",
            "Does love trouble you?",
        ], None),
    ]),
    ("HATE", 7, [
        ("* HATE *", [
            "What is it that you hate?",
            "Does hating (2) bother you?",
            "Why do you say you hate (2)?",
            "How long have you hated (2)?",
        ], None),
    ]),
    ("IF", 7, [
        ("* IF *", [
            "Do you think it is likely that (1)?",
            "Do you wish that (1)?",
            "What do you think about (1)?",
            "Really -- if (1)?",
        ], None),
    ]),
    ("NAME", 7, [
        ("*", [
            "I am not interested in names.",
            "I have told you before, I don't care about names. Please continue.",
            "Names don't matter much here. Go on.",
        ], None),
    ]),
    ("FAMILY", 7, [
        ("*", [
            "Tell me more about your family.",
            "Do you get along with your family?",
            "Is your family important to you?",
            "Who in your family is on your mind?",
        ], None),
    ]),
    ("PROBLEM", 7, [
        ("*", [
            "What does this problem remind you of?",
            "Do you think this problem will resolve itself?",
            "Tell me more about this problem.",
            "How long has this problem troubled you?",
        ], None),
    ]),
    ("SEX", 7, [
        ("*", [
            "Do you ever think about sex?",
            "Have you told anyone about these feelings?",
            "What is on your mind when you mention sex?",
            "Does talking about sex make you uncomfortable?",
        ], None),
    ]),
    ("CHILD", 6, [
        ("*", [
            "Did you have a happy childhood?",
            "What is your favorite childhood memory?",
            "Did you have close friends as a child?",
            "How were you treated as a child?",
        ], None),
    ]),
    ("FRIEND", 6, [
        ("* FRIEND *", [
            "Tell me about your friends.",
            "Do your friends worry you?",
            "Do your friends know you are here?",
            "Are your friends important to you?",
        ], None),
    ]),
    ("COMPUTER", 6, [
        ("*", [
            "Do computers worry you?",
            "Why do you mention computers?",
            "What do you think machines have to do with your problem?",
            "Don't you think computers can help people?",
        ], None),
    ]),
    ("MACHINE", 6, [
        ("*", [
            "What do you think of machines?",
            "Why do you mention machines?",
            "Do machines frighten you?",
            "Do you ever wonder what machines dream about?",
        ], None),
    ]),
    ("EVERYONE", 6, [
        ("*", [
            "Who, for example?",
            "Are you thinking of a particular person?",
            "Who, may I ask?",
            "Someone special, perhaps?",
            "You have a particular person in mind, don't you?",
        ], None),
    ]),
    ("EVERYBODY", 6, [
        ("*", [
            "Who, for example?",
            "Are you thinking of a particular person?",
            "Who, may I ask?",
            "Someone special, perhaps?",
            "You have a particular person in mind, don't you?",
        ], None),
    ]),
    ("NOBODY", 6, [
        ("*", [
            "Who, for example?",
            "Are you thinking of a particular person?",
            "Who, may I ask?",
            "Someone special, perhaps?",
            "You have a particular person in mind, don't you?",
        ], None),
    ]),
    ("ALWAYS", 6, [
        ("*", [
            "Can you think of a specific example?",
            "When?",
            "What incident are you thinking of?",
            "Really, always?",
        ], None),
    ]),
    ("NEVER", 6, [
        ("*", [
            "Never?",
            "Can you think of an exception?",
            "What would it take to change that?",
            "Really, never?",
        ], None),
    ]),
    ("YES", 5, [
        ("*", [
            "You seem quite certain.",
            "Are you sure?",
            "I see.",
            "I understand.",
        ], None),
    ]),
    ("NO", 5, [
        ("*", [
            "Are you saying no just to be negative?",
            "You are being a bit negative.",
            "Why not?",
            "Why 'no'?",
        ], None),
    ]),
    ("MAYBE", 5, [
        ("*", [
            "You don't seem very certain.",
            "Why the uncertain tone?",
            "Can't you be more positive?",
            "You aren't sure?",
            "Don't you know?",
        ], None),
    ]),
    ("MY", 2, [
        ("* MY *", [
            "Tell me more about your (2).",
            "Why do you say your (2)?",
            "Does that suggest anything else which belongs to you?",
            "Is it important to you that your (2)?",
        ], (2, "your ")),
    ]),
]

# Highest rank first; definition order breaks ties (sort is stable).
_SORTED_KEYWORDS = sorted(KEYWORDS, key=lambda entry: -entry[1])


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def new_state():
    """Return a fresh, JSON-serializable Eliza session state."""
    return {
        "turns": 0,
        "counters": {},
        "memory": [],
        "memory_index": 0,
        "fallback_index": 0,
        "goodbye_index": 0,
    }


def _copy_state(state):
    base = new_state()
    if state:
        base.update(state)
    base["counters"] = dict(base.get("counters") or {})
    base["memory"] = list(base.get("memory") or [])
    return base


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------

def _normalize(text):
    text = (text or "").upper()
    for contraction, expansion in CONTRACTIONS.items():
        text = re.sub(r"\b" + contraction + r"\b", expansion, text)
    text = text.replace("'", "")
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_keyword(tokens, keyword):
    words = keyword.split()
    for i in range(len(tokens) - len(words) + 1):
        if tokens[i:i + len(words)] == words:
            return True
    return False


def _match(pattern_tokens, input_tokens):
    """Match pattern tokens (with "*" wildcards) against input tokens.

    Returns a list of captured word lists (one per "*"), or None.
    """
    if not pattern_tokens:
        return [] if not input_tokens else None
    if pattern_tokens[0] == "*":
        rest = pattern_tokens[1:]
        for i in range(len(input_tokens) + 1):
            sub = _match(rest, input_tokens[i:])
            if sub is not None:
                return [input_tokens[:i]] + sub
        return None
    if not input_tokens:
        return None
    if pattern_tokens[0] == input_tokens[0]:
        return _match(pattern_tokens[1:], input_tokens[1:])
    return None


def _reflect(words):
    return " ".join(REFLECTIONS.get(word, word) for word in words).lower()


_GROUP_RE = re.compile(r"\((\d+)\)")


def _substitute(rule, captures):
    def repl(match):
        index = int(match.group(1)) - 1
        if 0 <= index < len(captures):
            return _reflect(captures[index])
        return ""

    return _GROUP_RE.sub(repl, rule)


def _round_robin(state, key, options):
    index = state["counters"].get(key, 0)
    choice = options[index % len(options)]
    state["counters"][key] = index + 1
    return choice


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_quit(text):
    """True when text contains bye/quit/exit/goodbye as a standalone word."""
    return bool(QUIT_RE.search(text or ""))


def respond(text, state):
    """Respond to one line of user input.

    Returns (reply, new_state). The input state is never mutated.
    """
    new = _copy_state(state)
    new["turns"] += 1

    if is_quit(text):
        index = new["goodbye_index"]
        reply = GOODBYES[index % len(GOODBYES)]
        new["goodbye_index"] = index + 1
        return reply, new

    tokens = _normalize(text).split()

    for keyword, _rank, patterns in _SORTED_KEYWORDS:
        if not _contains_keyword(tokens, keyword):
            continue
        for decomp, rules, memory in patterns:
            captures = _match(decomp.split(), tokens)
            if captures is None:
                continue
            reply = _substitute(_round_robin(new, keyword, rules), captures)
            if memory is not None:
                group_index, prefix = memory
                if 0 < group_index <= len(captures):
                    new["memory"].append(prefix + _reflect(captures[group_index - 1]))
            return reply, new

    # No keyword matched: surface a stored memory on a regular cadence,
    # otherwise fall back to a neutral prompt.
    if new["memory"] and (new["turns"] - 1) % MEMORY_EVERY == 0:
        template = MEMORY_TEMPLATES[new["memory_index"] % len(MEMORY_TEMPLATES)]
        new["memory_index"] += 1
        item = new["memory"].pop(0)
        return template.replace("(1)", item), new

    index = new["fallback_index"]
    reply = NOTHING_MATCHED[index % len(NOTHING_MATCHED)]
    new["fallback_index"] = index + 1
    return reply, new
