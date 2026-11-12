# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An independent historical simulation of the text-mode CompuServe Information Service circa 1988 — a Python terminal app with optional browser (FastAPI) and Telnet gateways. Not affiliated with CompuServe/AOL; all transactions are fictional.

## Commands

Setup:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
```

Run:

```powershell
py -3 compuserve.py                 # local console
.venv\Scripts\python.exe web_app.py # browser terminal (after installing [web] extra)
```

Tests (run before building a release; matches CI in `.github/workflows/tests.yml`):

```powershell
.venv\Scripts\python.exe -m unittest -v test_compuserve.py
.venv\Scripts\python.exe -m unittest -q test_compuserve test_expansion test_communications_store
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m compileall -q -x "old_versions|build|dist|.venv" .
.venv\Scripts\python.exe smoke_test.py
.venv\Scripts\python.exe -m pip install "setuptools>=75" wheel
.venv\Scripts\python.exe tests/check_installed_package.py
.venv\Scripts\python.exe build_release.py
.venv\Scripts\python.exe -c "import build_release, smoke_test; print(smoke_test.verify_archive(build_release.build_release()))"
```

Run a single test: `.venv\Scripts\python.exe -m unittest test_compuserve.SomeTestCase.test_something` (standard unittest module/class/method dotted path works against `test_compuserve.py`, `test_expansion.py`, `test_communications_store.py`, or anything under `tests/`).

Lint: `ruff` is configured in `pyproject.toml` (`select = ["E", "F", "W"]`, line-length 120, `old_versions` excluded).

`tests/check_installed_package.py` builds a real wheel, installs it in a temp dir outside the checkout, and imports every runtime module — it catches packaging omissions that unit tests won't.

## Architecture

`compuserve.py` owns the terminal session lifecycle and command router. Modules named `cis_*.py` implement individual services and treat `compuserve.py` (or the coordinator's state) as their runtime context. `cis_storage.py` provides transactional SQLite persistence (`compuserve.db`); JSON files in the project root are immutable content and legacy seed data — except the files listed in `cis_storage.MUTABLE_DATA_FILES`, which are runtime-mutable and stored through `cis_storage`.

The browser (`web_app.py`) and Telnet (`telnet_app.py`) gateways each launch one isolated simulator process per terminal session. Those processes share state (presence, live messages, member data) only through SQLite — there is no in-process sharing across sessions. Session-scoped mutable state (nav stack, simulation date, etc.) lives in `cis_session.SessionState` and is accessed via a `ContextVar` (`cis_session.current_session_state()` / `session_simulation_date()`), not module-level globals, because one OS process can only assume one session at a time but the pattern must stay safe under that model.

### Content modules

Newer content ships as pure content-plus-logic modules (e.g. `cis_hamnet.py`, `cis_guitar.py`, `cis_nightstation.py`, `cis_crossword.py`). A module declares its section spec, seed posts or puzzle data, and public functions that accept an optional simulated `day`; the coordinator in `compuserve.py` wires those into `FORUM_CATALOG`, menu handlers, and `go_commands.json`. Never hardcode absolute filesystem paths in a module or its tests — derive the repo root via `Path(__file__).resolve().parent`.

`cis_archive.archive_service` scopes the "December 1988 archive" label across a service and its nested pages, resetting even when GO navigation interrupts it. `cis_discovery.archive_notice` labels other fixed collections (forums, libraries) the same way. Featured-date and live news are never implicitly archive-labeled — publication-sensitive services must gate stories by the full simulated date themselves. `cis_discovery.start_suggestions` supplies the three date-aware `GO START` choices; the standard navigation router opens their destinations.

GO navigation (`GO <destination>`, or bare `G`) is intercepted in `cis_session.read_input` and raises `cis_session.GoNavigation` to unwind the current prompt without treating the input as submitted data — service code doesn't handle GO parsing itself.

### Packaging

`pyproject.toml`'s `[tool.setuptools] py-modules` lists every runtime module explicitly — **when adding a new `cis_*.py` (or any new top-level runtime module), add it there** or it will be missing from wheels/sdists. `build_support.BuildPy` copies seed JSON and browser assets beside those modules in wheels; `MANIFEST.in` carries the same resources into source distributions. `release_assets.json` is the asset list for release ZIPs, wheels, and sdists — add new distributable resources there too (never member data, databases, exports, or credentials; its `defaults` section holds clean starter state substituted in at build time). Unknown JSON files are excluded from builds, and stale unlisted JSON in a wheel build directory fails the build.

Keep `cis_version.py`, `pyproject.toml`'s version, and the local package version in `uv.lock` in sync when bumping a release.

### Main boundaries

- **Terminal application:** `compuserve.py`, `cis_terminal.py`, `cis_session.py`
- **Services:** the remaining `cis_*.py` modules
- **Persistence:** `cis_storage.py`, `cis_migrations.py`, `compuserve.db`
- **Transports:** `web_app.py`, `telnet_app.py`, and the local console
- **Historical content:** root JSON files and `downloads/`
- **Operations:** `event_worker.py`, `build_release.py`, `install-linux.sh`

### Direction of travel

New features should live in focused service modules instead of enlarging `compuserve.py`. Session-specific mutable values should gradually move into `SessionState`; persistent shared values belong behind `cis_storage.py`. Runtime artifacts (databases, backups, captures, uploads/downloads, virtualenvs, release archives) must never be added to source control or release archives — `.gitignore` already excludes them; don't fight it.

## Conventions

- Use UTF-8 explicitly for text files. `.gitattributes` keeps Python/JSON/shell scripts in LF and Windows `.cmd` scripts in CRLF — don't normalize across that line.
- Use `Path.is_absolute()` for path checks rather than assuming a leading slash (Windows compatibility).
- Tests comparing text should normalize line endings without changing the content assertion itself.
- Tests should isolate persistence with a temporary directory — never point tests at the real `compuserve.db` or root JSON files.
- Linux installs/upgrades go through the release ZIP and `install-linux.sh --install-dir ... --upgrade --systemd-user` (add `--telnet` or `--non-interactive` as needed); it verifies the release manifest, stages and smoke-tests, backs up the database, preserves runtime directories, and restores prior files on a failed install or health check.
