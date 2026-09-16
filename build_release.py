"""Build a deterministic, dependency-free release archive."""

import hashlib
import json
from pathlib import Path
import zipfile

from cis_version import VERSION


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
ARCHIVE_NAME = f"classic-compuserve-{VERSION}.zip"
FIXED_TIMESTAMP = (1988, 12, 15, 12, 0, 0)
INCLUDED_SUFFIXES = {".py", ".json", ".md", ".cmd", ".sh", ".toml", ".txt", ".html", ".css", ".js", ".in"}
EXCLUDED_NAMES = {"test_compuserve.py"}
EXCLUDED_DIRECTORIES = {
    ".git", ".github", "build", ".venv", "__pycache__", "backups", "captures", "dist", "downloads", "old_versions",
    "testdata", "tests", "tools", "uploads",
    "compuserve.db", "compuserve.db-shm", "compuserve.db-wal"
}


def release_files():
    """Return stable, relative paths for files shipped to players."""
    result = []
    for path in BASE_DIR.rglob("*"):
        relative = path.relative_to(BASE_DIR)
        if not path.is_file() or path.name in EXCLUDED_NAMES:
            continue
        if any(part in EXCLUDED_DIRECTORIES or part.endswith(".egg-info") for part in relative.parts):
            continue
        if path.suffix.lower() in INCLUDED_SUFFIXES:
            result.append(relative)
    return sorted(result, key=lambda item: item.as_posix().lower())


def build_release():
    """Create the ZIP and embed hashes for every shipped file."""
    DIST_DIR.mkdir(exist_ok=True)
    target = DIST_DIR / ARCHIVE_NAME
    files = release_files()
    manifest = {
        "name": "Classic CompuServe Simulation",
        "version": VERSION,
        "files": {
            path.as_posix(): hashlib.sha256((BASE_DIR / path).read_bytes()).hexdigest()
            for path in files
        },
    }
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in files:
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if relative.suffix.lower() == ".sh" else 0o644) << 16
            archive.writestr(info, (BASE_DIR / relative).read_bytes(), compresslevel=9)
        info = zipfile.ZipInfo("RELEASE_MANIFEST.json", FIXED_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        payload = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        archive.writestr(info, payload, compresslevel=9)
    return target


if __name__ == "__main__":
    print(build_release())
