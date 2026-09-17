"""Dependency-free release and installation smoke checks."""

import json
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import build_release
import cis_business
import cis_dynamic
import cis_experience
import cis_magazine
import compuserve


def run():
    root = Path(__file__).resolve().parent
    required = {"compuserve.py", "event_worker.py", "install-linux.sh", "screens.json", "go_commands.json", "store_catalog.json", "reference_databases.json", "cis_communities.py", "computer_communities.json"}
    shipped = {path.as_posix() for path in build_release.release_files()}
    required.update({'cis_magazine.py', 'magazine_issues.json', 'cis_web_files.py'})
    required.update({'cis_poster.py', 'poster_words.json'})
    missing = sorted(required - shipped)
    if missing:
        raise RuntimeError("Release omits: " + ", ".join(missing))
    forbidden_prefixes = ("old_versions/", "tests/", "tools/")
    forbidden = sorted(name for name in shipped if name.startswith(forbidden_prefixes))
    if forbidden:
        raise RuntimeError("Release includes development files: " + ", ".join(forbidden))
    for name in ("screens.json", "go_commands.json", "store_catalog.json", "reference_databases.json"):
        json.loads((root / name).read_text(encoding="utf-8"))
    installer = (root / "install-linux.sh").read_text(encoding="utf-8")
    for marker in (
        "python3", "$APP_NAME-events.timer", "event_worker.py", "start-linux.sh",
        "verify_manifest", "backup_live_database", "rollback_application",
        "systemctl --user is-active", ".installed-version",
    ):
        if marker not in installer:
            raise RuntimeError(f"Linux installer lacks {marker}")
    with tempfile.TemporaryDirectory() as directory:
        original_base, original_user = compuserve.BASE_DIR, compuserve.current_user_id
        try:
            compuserve.BASE_DIR = Path(directory); compuserve.current_user_id = "70000,SMOKE"
            cis_experience.add_note(compuserve, "SMOKE", "Member workflow")
            quotes = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
            result = cis_business.trade(compuserve, "BUY", "IBM", 1, quotes)
            if "RECORDED" not in result or not cis_experience.notebook_lines(compuserve):
                raise RuntimeError("Scripted member workflow failed")
        finally:
            compuserve.BASE_DIR, compuserve.current_user_id = original_base, original_user
    return "Release assets, Linux service files, JSON data, and member workflow passed."


def verify_archive(path):
    path = Path(path)
    with tempfile.TemporaryDirectory() as directory, zipfile.ZipFile(path) as archive:
        destination = Path(directory); archive.extractall(destination)
        manifest = json.loads(archive.read("RELEASE_MANIFEST.json"))
        for name, expected in manifest["files"].items():
            actual = hashlib.sha256((destination / name).read_bytes()).hexdigest()
            if actual != expected: raise RuntimeError(f"Manifest mismatch: {name}")
        completed = subprocess.run([sys.executable, "smoke_test.py"], cwd=destination, text=True, capture_output=True, check=True)
    return f"{len(manifest['files'])} manifest files verified; clean-copy smoke test passed: {completed.stdout.strip()}"


if __name__ == "__main__":
    print(run())
