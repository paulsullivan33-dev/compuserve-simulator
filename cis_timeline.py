"""Curated offline December 1988 historical timeline."""

from cis_web_files import offer_download

import json
from datetime import date
from pathlib import Path


DATA_PATH = Path(__file__).resolve().with_name("historical_timeline.json")


def _load():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    records = data.get("records", [])
    identifiers = set()
    covered_days = set()
    for record in records:
        required = {"id", "date", "category", "kind", "title", "summary", "source", "source_url", "related"}
        if not required.issubset(record) or record["id"] in identifiers:
            raise RuntimeError("Historical timeline contains an invalid or duplicate record.")
        when = date.fromisoformat(record["date"])
        if when.year != 1988 or when.month != 12 or record["kind"] not in ("EVENT", "CONTEXT"):
            raise RuntimeError("Timeline records must describe December 1988 events or context.")
        identifiers.add(record["id"])
        covered_days.add(when.day)
    if covered_days != set(range(1, 32)):
        missing = ", ".join(str(day) for day in sorted(set(range(1, 32)) - covered_days))
        raise RuntimeError(f"Historical timeline is missing December day(s): {missing}.")
    return data


TIMELINE = _load()
RECORDS = TIMELINE["records"]


def records_for_date(value):
    key = value.isoformat() if hasattr(value, "isoformat") else str(value)
    return [record for record in RECORDS if record["date"] == key]


def search(query):
    terms = [term.casefold() for term in query.split() if term]
    if not terms:
        return []
    return [record for record in RECORDS if all(term in " ".join(str(record.get(key, "")) for key in ("category", "title", "summary", "source")).casefold() for term in terms)]


def find(record_id):
    return next((record for record in RECORDS if record["id"] == record_id.strip().upper()), None)


def records_related_to(reference_id):
    """Return timeline records that explicitly cite an offline reference record."""
    key = reference_id.strip().upper()
    return [record for record in RECORDS if key in record.get("related", [])]


def article_lines(record):
    lines = [f'RECORD {record["id"]}', f'DATE: {record["date"]}', f'CATEGORY: {record["category"]}', f'TYPE: {record["kind"]}', "", record["title"], record["summary"], "", f'SOURCE: {record["source"]}']
    if record.get("source_url"):
        lines.append("SOURCE URL: " + record["source_url"])
    if record.get("related"):
        lines.extend(["", "RELATED REFERENCE RECORDS: " + ", ".join(record["related"])])
    if record["kind"] == "CONTEXT":
        lines.extend(["", "PERIOD CONTEXT -- NOT AN EVENT ASSIGNED TO THIS EXACT DAY."])
    return lines


def mark(app, record_id):
    record = find(record_id)
    if not record:
        return "Timeline record not found."
    state = app.cis_dynamic.load_state(app)
    marks = state.setdefault("timeline_marks", {}).setdefault(app.current_user_id or "GUEST", [])
    if record_id not in marks:
        marks.append(record_id)
        app.cis_dynamic.save_state(app, state)
    return f"Timeline record {record_id} marked."


def marked(app):
    state = app.cis_dynamic.load_state(app)
    return [record for record_id in state.get("timeline_marks", {}).get(app.current_user_id or "GUEST", []) for record in [find(record_id)] if record]


def export_marked(app):
    records = marked(app)
    if not records:
        return None
    destination = app.BASE_DIR / "downloads" / f'TIME{(app.current_user_id or "GUEST").replace(",", "")}.TXT'
    destination.parent.mkdir(exist_ok=True)
    lines = [TIMELINE["title"].upper(), f'MARKED RECORDS FOR {app.current_user_id or "GUEST"}', ""]
    for record in records:
        article = article_lines(record)
        related = []
        for record_id in record.get("related", []):
            _, reference = app.cis_reference.find_record(record_id)
            related.append(f"{record_id} {reference[1]}" if reference else record_id)
        if related:
            article.extend(["", "RELATED REFERENCE INDEX", *related])
        lines.extend(article + ["", "-" * 72, ""])
    destination.write_text("\r\n".join(lines), encoding="ascii", errors="replace")
    offer_download(destination)
    return destination

