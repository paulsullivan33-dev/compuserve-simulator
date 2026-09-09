import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen
from xml.etree import ElementTree

BASE_DIR = Path(__file__).resolve().parent
USER_AGENT = "CompuServeNewsEmulator/1.0"
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_FIELD_LENGTH = 20_000


def _clean(value, limit=MAX_FIELD_LENGTH):
    if value is None:
        return None
    return str(value)[:limit]


def _local_name(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element, names):
    for child in element:
        if _local_name(child.tag) in names:
            return "".join(child.itertext()).strip()
    return None


def _parse_entries(content):
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as exc:
        raise RuntimeError(f"invalid XML: {exc}") from exc

    entries = []
    for element in root.iter():
        if _local_name(element.tag) not in ("item", "entry"):
            continue
        link = _child_text(element, {"link"})
        if not link:
            for child in element:
                if _local_name(child.tag) == "link" and child.get("href"):
                    link = child.get("href")
                    break
        entries.append({
            "title": _child_text(element, {"title"}),
            "link": link,
            "published": _child_text(element, {"published", "pubdate", "updated"}),
            "summary": _child_text(element, {"summary", "description", "content"}) or "",
        })
    return entries


def fetch_feed(url, timeout=10):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status >= 400:
            raise RuntimeError(f"HTTP {status}")
        content = response.read(MAX_RESPONSE_BYTES + 1)
    if len(content) > MAX_RESPONSE_BYTES:
        raise RuntimeError("feed exceeds the 5 MiB size limit")

    entries = _parse_entries(content)
    if not entries:
        raise RuntimeError("feed contains no entries")
    return entries


def collect_news(config, source_field=None):
    result = {}
    failures = []
    for category, configured_sources in config.items():
        sources = (
            configured_sources
            if isinstance(configured_sources, dict)
            else {None: configured_sources}
        )
        result[category] = []
        for source, url in sources.items():
            try:
                entries = fetch_feed(url)
            except Exception as exc:
                failures.append(f"{category}/{source or 'feed'}: {exc}")
                continue
            for entry in entries:
                item = {
                    "title": _clean(entry.get("title")),
                    "link": _clean(entry.get("link"), 2_000),
                    "published": _clean(entry.get("published"), 200),
                    "summary": _clean(entry.get("summary", "")),
                }
                if source_field and source:
                    item[source_field] = source
                result[category].append(item)
    if not any(result.values()):
        details = "; ".join(failures) or "no configured sources"
        raise RuntimeError(f"No feeds succeeded; existing output was preserved. {details}")
    return result, failures


def write_json_atomic(filename, data):
    destination = BASE_DIR / filename
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=BASE_DIR, delete=False, suffix=".tmp"
    ) as file:
        temporary = Path(file.name)
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.flush()
        os.fsync(file.fileno())
    try:
        temporary.replace(destination)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def build_news_file(config, output_filename, source_field=None):
    data, failures = collect_news(config, source_field=source_field)
    write_json_atomic(output_filename, data)
    for failure in failures:
        print(f"Warning: {failure}")
    return BASE_DIR / output_filename
