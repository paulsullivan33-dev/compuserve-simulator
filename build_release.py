"""Build a deterministic, dependency-free release archive."""

import hashlib
import json
from pathlib import Path
import zipfile

from cis_version import VERSION
from release_payload import policy, payload


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
    return [Path(name) for name in policy(BASE_DIR)['files']]


def build_release():
    """Create the ZIP and embed hashes for every shipped file."""
    DIST_DIR.mkdir(exist_ok=True)
    target = DIST_DIR / ARCHIVE_NAME
    files = release_files()
    contents = {path: payload(BASE_DIR, path) for path in files}
    manifest = {
        "name": "Classic CompuServe Simulation",
        "version": VERSION,
        "files": {
            path.as_posix(): hashlib.sha256(contents[path]).hexdigest()
            for path in files
        },
    }
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in files:
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if relative.suffix.lower() == ".sh" else 0o644) << 16
            archive.writestr(info, contents[relative], compresslevel=9)
        info = zipfile.ZipInfo("RELEASE_MANIFEST.json", FIXED_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        archive.writestr(info, manifest_bytes, compresslevel=9)
    return target


if __name__ == "__main__":
    print(build_release())
