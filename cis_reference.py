"""Search and presentation helpers for the period-style reference databases."""

from cis_web_files import offer_download

import json
import os
import re
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cis_storage import read_reference_cache, write_reference_cache

DATA_PATH = Path(__file__).resolve().with_name("reference_databases.json")
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
OPENALEX_API = "https://api.openalex.org/works"
LIVE_RESULT_LIMIT = 10
LIVE_TIMEOUT = 5


class LiveReferenceError(RuntimeError):
    """A live reference provider could not complete a search."""


def _clean_live_text(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def search_live_reference(query, limit=LIVE_RESULT_LIMIT, timeout=LIVE_TIMEOUT, opener=urlopen, base_dir=None):
    """Search Wikipedia and return provider-neutral live reference records."""
    query = query.strip()
    if not query:
        return []
    if base_dir is not None:
        cached = read_reference_cache(base_dir, "wikipedia", query)
        if cached is not None:
            return [{**record, "cached": True} for record in cached]
    limit = max(1, min(int(limit), LIVE_RESULT_LIMIT))
    parameters = urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 0,
        "gsrlimit": limit,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "exchars": 1200,
        "inprop": "url",
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
    })
    request = Request(
        f"{WIKIPEDIA_API}?{parameters}",
        headers={"User-Agent": "ClassicCompuServe/1.0 (live reference search)"},
    )
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        if base_dir is not None:
            stale = read_reference_cache(base_dir, "wikipedia", query, allow_expired=True)
            if stale is not None:
                return [{**record, "cached": True, "stale": True} for record in stale]
        raise LiveReferenceError(f"Live reference service unavailable: {exc}") from exc
    if payload.get("error"):
        raise LiveReferenceError("Live reference provider rejected the search.")
    pages = payload.get("query", {}).get("pages", [])
    records = []
    for page in pages:
        page_id = page.get("pageid")
        title = _clean_live_text(page.get("title"))
        if not isinstance(page_id, int) or not title:
            continue
        records.append({
            "id": f"W{page_id}",
            "title": title,
            "summary": _clean_live_text(page.get("extract")) or "No introductory summary is available.",
            "url": str(page.get("fullurl") or ""),
            "source": "Wikipedia",
            "cached": False,
        })
    if base_dir is not None:
        write_reference_cache(base_dir, "wikipedia", query, records)
    return records


def _abstract_text(index):
    if not isinstance(index, dict):
        return "No abstract is available."
    positioned = [(position, word) for word, positions in index.items() for position in positions if isinstance(position, int)]
    return _clean_live_text(" ".join(word for _, word in sorted(positioned))) or "No abstract is available."


def search_openalex_reference(query, limit=LIVE_RESULT_LIMIT, timeout=LIVE_TIMEOUT, opener=urlopen, base_dir=None):
    """Search scholarly works in OpenAlex, optionally limited to pre-1989 works."""
    query = query.strip()
    before_year = None
    match = re.match(r"^BEFORE\s+(\d{4})\s+(.+)$", query, re.IGNORECASE)
    if match:
        before_year, query = int(match.group(1)), match.group(2).strip()
    if not query:
        return []
    limit = max(1, min(int(limit), LIVE_RESULT_LIMIT))
    cache_query = f"before:{before_year or 'any'}:{query}"
    if base_dir is not None:
        cached = read_reference_cache(base_dir, "openalex", cache_query)
        if cached is not None:
            return [{**record, "cached": True} for record in cached]
    parameters = {
        "search": query,
        "per_page": limit,
        "select": "id,doi,display_name,publication_year,authorships,primary_location,abstract_inverted_index,cited_by_count,open_access,type",
    }
    if before_year:
        parameters["filter"] = f"publication_year:<{before_year}"
    api_key = os.environ.get("OPENALEX_API_KEY")
    if api_key:
        parameters["api_key"] = api_key
    request = Request(f"{OPENALEX_API}?{urlencode(parameters)}", headers={"User-Agent": "ClassicCompuServe/1.0 (academic reference search)"})
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        if base_dir is not None:
            stale = read_reference_cache(base_dir, "openalex", cache_query, allow_expired=True)
            if stale is not None:
                return [{**record, "cached": True, "stale": True} for record in stale]
        raise LiveReferenceError(f"Live academic service unavailable: {exc}") from exc
    if payload.get("error"):
        raise LiveReferenceError("OpenAlex rejected the academic search.")
    records = []
    for work in payload.get("results", []):
        openalex_id = str(work.get("id") or "").rsplit("/", 1)[-1]
        title = _clean_live_text(work.get("display_name"))
        if not openalex_id.startswith("W") or not title:
            continue
        authors = [_clean_live_text(item.get("author", {}).get("display_name")) for item in work.get("authorships", [])]
        source = (work.get("primary_location") or {}).get("source") or {}
        access = work.get("open_access") or {}
        records.append({
            "id": "OA" + openalex_id[1:], "title": title,
            "summary": _abstract_text(work.get("abstract_inverted_index"))[:2000],
            "url": str(work.get("id") or ""), "source": "OpenAlex", "cached": False,
            "authors": ", ".join(author for author in authors if author) or "Author information unavailable",
            "publication_year": work.get("publication_year"),
            "publication": _clean_live_text(source.get("display_name")) or "Source unavailable",
            "doi": str(work.get("doi") or "").removeprefix("https://doi.org/"),
            "citations": int(work.get("cited_by_count") or 0),
            "open_access": bool(access.get("is_oa")), "work_type": work.get("type") or "work",
        })
    if base_dir is not None:
        write_reference_cache(base_dir, "openalex", cache_query, records)
    return records


def live_result_line(record):
    suffix = f' ({record["publication_year"]})' if record.get("publication_year") else ""
    return f'{record["id"]}  {record["title"]}{suffix}'


def live_article_lines(record):
    lines = [
        f'RECORD {record["id"]}',
        f'SOURCE: {record["source"].upper()} LIVE REFERENCE',
        "",
        record["title"].upper(),
        record["summary"],
        "",
        "LIVE NETWORK REFERENCE -- MODERN CONTENT.",
        "THIS RECORD IS OUTSIDE THE DECEMBER 1988 SIMULATION.",
    ]
    if record.get("cached"):
        lines.append("CACHED COPY" + (" -- PROVIDER CURRENTLY UNAVAILABLE." if record.get("stale") else "."))
    if record.get("authors"):
        lines[4:4] = [f'AUTHORS: {record["authors"]}', f'SOURCE: {record.get("publication", "")}', f'YEAR: {record.get("publication_year", "")}', f'TYPE: {str(record.get("work_type", "")).upper()}', f'CITATIONS: {record.get("citations", 0)}', f'OPEN ACCESS: {"YES" if record.get("open_access") else "NO"}', *( [f'DOI: {record["doi"]}'] if record.get("doi") else []), ""]
    if record.get("url"):
        lines.extend(["", "SOURCE URL: " + record["url"]])
    return lines

def _load_databases():
    with DATA_PATH.open("r", encoding="utf-8") as source:
        databases = json.load(source)
    required = {"academic", "medical", "science", "library"}
    if set(databases) != required:
        raise RuntimeError("Reference database file must contain the four declared databases.")
    identifiers = set()
    for name, definition in databases.items():
        if not isinstance(definition.get("title"), str) or len(definition.get("records", [])) != 50:
            raise RuntimeError(f"Reference database {name} must contain a title and exactly 50 records.")
        for record in definition["records"]:
            if not isinstance(record, list) or len(record) != 4 or not all(isinstance(field, str) and field for field in record):
                raise RuntimeError(f"Reference database {name} contains an invalid record.")
            if record[0] in identifiers:
                raise RuntimeError(f"Duplicate reference record identifier: {record[0]}")
            identifiers.add(record[0])
    if len(identifiers) != 200:
        raise RuntimeError("Reference database file must contain exactly 200 unique records.")
    return databases

DATABASES = _load_databases()

SUBJECTS = {
    "academic": {
        "COMPUTING": ("computer", "electronic", "microprocessor", "robotics"),
        "GEOGRAPHY": ("geography", "continent", "europe", "asia"),
        "HISTORY": ("history", "war", "revolution"),
        "SCIENCE": ("science", "physics", "biology", "astronomy"),
        "GOVERNMENT": ("government", "law", "diplomacy", "treaty"),
    },
    "medical": {
        "EMERGENCY": ("emergency", "first aid", "injury"),
        "HEART-BLOOD": ("heart", "blood", "cardiovascular", "circulation"),
        "INFECTION": ("infection", "virus", "bacteria"),
        "NEUROLOGY": ("brain", "neurology", "seizure"),
        "PREVENTION": ("vaccine", "prevention", "screening"),
    },
    "science": {
        "COMPUTERS": ("computer", "software", "database", "processor"),
        "COMMUNICATIONS": ("communications", "network", "radio", "telephone"),
        "EARTH-CLIMATE": ("climate", "geology", "atmosphere", "ocean"),
        "ELECTRONICS": ("electronics", "semiconductor", "signal"),
        "SPACE": ("space", "astronomy", "spacecraft"),
    },
    "library": {
        "COMMUNICATIONS": ("modem", "serial", "terminal", "telephone"),
        "DOS-SOFTWARE": ("dos", "software", "files", "wordperfect"),
        "HARDWARE": ("computer", "disk", "printer", "display"),
        "ONLINE-SERVICE": ("compuserve", "forum", "library", "download"),
        "SAFETY-BACKUP": ("backup", "safety", "recovery", "security"),
    },
}

def _record_text(record):
    return " ".join(record).upper()

def _terms(expression):
    return [token for token in re.findall(r"[A-Z0-9][A-Z0-9'.-]*", expression.upper()) if token not in {"AND", "OR", "NOT"}]

def _matches_boolean(haystack, expression):
    groups = re.split(r"\s+OR\s+", expression.upper().strip())
    for group in groups:
        excluded = re.findall(r"(?:^|\s)NOT\s+([A-Z0-9][A-Z0-9'.-]*)", group)
        positive_text = re.sub(r"(?:^|\s)NOT\s+[A-Z0-9][A-Z0-9'.-]*", " ", group)
        positive = [token for token in re.findall(r"[A-Z0-9][A-Z0-9'.-]*", positive_text) if token != "AND"]
        if positive and all(term in haystack for term in positive) and not any(term in haystack for term in excluded):
            return True
    return False

def search(database, query):
    records = DATABASES[database]["records"]
    expression = query.strip().upper()
    if not expression:
        return sorted(records, key=lambda record: record[1])
    direct = next((record for record in records if record[0] == expression), None)
    if direct:
        return [direct]
    words = _terms(expression)
    phrase = " ".join(words)
    boolean = any(f" {operator} " in f" {expression} " for operator in ("AND", "OR", "NOT"))
    ranked = []
    for record in records:
        haystack = _record_text(record)
        matched = sum(word in haystack for word in words)
        accepted = _matches_boolean(haystack, expression) if boolean else matched > 0
        if accepted:
            title = record[1].upper()
            ranked.append((matched, phrase in haystack, phrase in title, record))
    return [record for _, _, _, record in sorted(ranked, key=lambda item: (-item[0], -item[1], -item[2], item[3][1]))]

def find_record(record_id):
    record_id = record_id.strip().upper()
    for database, definition in DATABASES.items():
        record = next((item for item in definition["records"] if item[0] == record_id), None)
        if record:
            return database, record
    return None, None

def subject_records(database, subject):
    terms = SUBJECTS.get(database, {}).get(subject.strip().upper())
    if not terms:
        return []
    return [record for record in DATABASES[database]["records"] if any(term.upper() in _record_text(record) for term in terms)]

def suggest_records(text, count=3):
    words = set(_terms(text))
    ranked = []
    for database, definition in DATABASES.items():
        for record in definition["records"]:
            descriptors = set(_terms(record[1] + " " + record[3]))
            overlap = len(words.intersection(descriptors))
            if overlap:
                ranked.append((overlap, database, record))
    return [(database, record) for _, database, record in sorted(ranked, key=lambda item: (-item[0], item[2][1]))[:count]]

def record_search(app, database, query, result_count):
    user_id = app.current_user_id or "GUEST"
    state = app.cis_dynamic.load_state(app)
    history = state.setdefault("reference_history", {}).setdefault(user_id, [])
    history.append({"database": database, "query": query[:120], "results": result_count, "date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")})
    state["reference_history"][user_id] = history[-20:]
    app.cis_dynamic.save_state(app, state)

def search_history(app):
    state = app.cis_dynamic.load_state(app)
    return list(state.get("reference_history", {}).get(app.current_user_id or "GUEST", []))

def clear_history(app):
    state = app.cis_dynamic.load_state(app)
    state.setdefault("reference_history", {})[app.current_user_id or "GUEST"] = []
    app.cis_dynamic.save_state(app, state)

def mark_record(app, record_id):
    database, record = find_record(record_id)
    if not record:
        return "Record not found."
    state = app.cis_dynamic.load_state(app)
    marks = state.setdefault("reference_marks", {}).setdefault(app.current_user_id or "GUEST", [])
    if record[0] not in marks:
        marks.append(record[0])
        app.cis_dynamic.save_state(app, state)
    return f"Record {record[0]} marked."

def marked_records(app):
    state = app.cis_dynamic.load_state(app)
    identifiers = state.get("reference_marks", {}).get(app.current_user_id or "GUEST", [])
    return [(database, record) for record_id in identifiers for database, record in [find_record(record_id)] if record]

def mark_live_record(app, record):
    state = app.cis_dynamic.load_state(app)
    marks = state.setdefault("live_reference_marks", {}).setdefault(app.current_user_id or "GUEST", [])
    stored = {key: record.get(key) for key in ("id", "title", "summary", "url", "source", "authors", "publication_year", "publication", "doi", "citations", "open_access", "work_type")}
    existing = next((index for index, item in enumerate(marks) if item.get("id") == stored["id"]), None)
    if existing is None:
        marks.append(stored)
    else:
        marks[existing] = stored
    app.cis_dynamic.save_state(app, state)
    return f'Record {stored["id"]} marked.'

def marked_live_records(app):
    state = app.cis_dynamic.load_state(app)
    return list(state.get("live_reference_marks", {}).get(app.current_user_id or "GUEST", []))

def export_marked(app):
    marked = marked_records(app)
    live_marked = marked_live_records(app)
    if not marked and not live_marked:
        return None
    user_id = app.current_user_id or "GUEST"
    filename = f"REF{user_id.split(',')[-1] if ',' in user_id else 'GUEST'}.TXT"
    destination = app.BASE_DIR / "downloads" / filename
    destination.parent.mkdir(exist_ok=True)
    lines = ["COMPUSERVE REFERENCE DATA BASES", f"MARKED RECORD PACKET FOR {user_id}", "DECEMBER 1988 HISTORICAL SIMULATION", "",]
    for database, record in marked:
        lines.extend(article_lines(record, database) + ["", "-" * 72, ""])
    for record in live_marked:
        lines.extend(live_article_lines(record) + ["", "-" * 72, ""])
    destination.write_text("\r\n".join(lines), encoding="ascii", errors="replace")
    if getattr(app, "current_user_id", None):
        app.cis_dynamic.record_activity(app, app.current_user_id, "REFERENCE", f"Prepared {filename} with {len(marked) + len(live_marked)} marked records.")
    offer_download(destination)
    return destination

def related_records(database, record, count=3):
    keywords = set(_terms(record[3]))
    ranked = []
    for candidate in DATABASES[database]["records"]:
        if candidate[0] == record[0]:
            continue
        overlap = len(keywords.intersection(_terms(candidate[3])))
        if overlap:
            ranked.append((overlap, candidate))
    return [candidate for _, candidate in sorted(ranked, key=lambda item: (-item[0], item[1][1]))[:count]]

def result_line(record):
    return f"{record[0]}  {record[1]}"

def article_lines(record, database):
    lines = [f"RECORD {record[0]}", f"DATABASE: {DATABASES[database]['title']}", "", record[1], record[2]]
    if database == "medical":
        lines.extend(["", "GENERAL INFORMATION ONLY -- NOT A DIAGNOSIS.", "CONTACT A PHYSICIAN OR EMERGENCY SERVICE WHEN APPROPRIATE."])
    elif database == "science":
        lines.extend(["", "DESCRIPTORS: " + record[3].upper(), "Use the cited descriptors to refine another search."])
    related = related_records(database, record)
    if related:
        lines.extend(["", "SEE ALSO: " + ", ".join(f"{item[0]} {item[1]}" for item in related)])
    return lines

