"""Curated, offline multi-chapter historical features."""

from cis_web_files import offer_download

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().with_name("historical_features.json")


def _load():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    features = data.get("features", [])
    identifiers = set()
    for feature in features:
        if not {"id", "title", "deck", "chapters"}.issubset(feature) or feature["id"] in identifiers or not feature["chapters"]:
            raise RuntimeError("Historical feature data is invalid or contains duplicate IDs.")
        identifiers.add(feature["id"])
        for chapter in feature["chapters"]:
            if not {"title", "text", "timeline", "references"}.issubset(chapter):
                raise RuntimeError(f'Historical feature {feature["id"]} contains an invalid chapter.')
    return data


CATALOG = _load()
FEATURES = CATALOG["features"]


def find(feature_id):
    key = feature_id.strip().upper()
    return next((feature for feature in FEATURES if feature["id"] == key), None)


def progress(app, feature):
    return int(app.current_profile.get("feature_progress", {}).get(feature["id"], 0))


def save_progress(app, feature, chapter_index):
    values = app.current_profile.setdefault("feature_progress", {})
    values[feature["id"]] = max(0, min(chapter_index, len(feature["chapters"]) - 1))
    read = app.current_profile.setdefault("features_read", [])
    if chapter_index == len(feature["chapters"]) - 1 and feature["id"] not in read:
        read.append(feature["id"])
    app.save_profiles()


def toggle_bookmark(app, feature):
    bookmarks = app.current_profile.setdefault("feature_bookmarks", [])
    if feature["id"] in bookmarks:
        bookmarks.remove(feature["id"])
        message = "Bookmark removed."
    else:
        bookmarks.append(feature["id"])
        message = "Feature bookmarked."
    app.save_profiles()
    return message


def chapter_lines(feature, index):
    chapter = feature["chapters"][index]
    return [f'FEATURE {feature["id"]}', f'CHAPTER {index + 1} OF {len(feature["chapters"])}', "", chapter["title"], chapter["text"], "", "TIMELINE: " + ", ".join(chapter["timeline"]), "REFERENCE: " + ", ".join(chapter["references"])]


def export(app, feature):
    destination = app.BASE_DIR / "downloads" / f'{feature["id"]}.TXT'
    destination.parent.mkdir(exist_ok=True)
    lines = [CATALOG["title"].upper(), feature["title"], feature["deck"], ""]
    for index in range(len(feature["chapters"])):
        lines.extend(chapter_lines(feature, index) + ["", "-" * 72, ""])
    destination.write_text("\r\n".join(lines), encoding="ascii", errors="replace")
    offer_download(destination)
    return destination

