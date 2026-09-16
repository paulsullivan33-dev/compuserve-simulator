# Architecture

`compuserve.py` owns the terminal session lifecycle and command router. Modules named
`cis_*.py` implement individual services and accept the application module as their
runtime context. `cis_storage.py` provides transactional SQLite persistence while the
JSON files in the project root provide immutable content and legacy seed data.

The browser and Telnet gateways each launch one isolated simulator process per
terminal session. Those processes communicate through SQLite for shared presence,
messages, and persistent member data.

## Content modules

Newer content ships as pure content-plus-logic modules (for example
`cis_hamnet.py`, `cis_guitar.py`, `cis_nightstation.py`, `cis_crossword.py`).
A module declares its section spec, seed posts or puzzle data, and public
functions that accept an optional simulated `day`; the coordinator in
`compuserve.py` wires those into `FORUM_CATALOG`, menu handlers, and
`go_commands.json`. Never hardcode absolute filesystem paths in a module or its
tests; derive the repo root from `Path(__file__).resolve().parent`.

`cis_archive.archive_service` scopes the December 1988 archive label across a
service and its nested pages, resetting even when GO navigation interrupts it.
`cis_discovery.archive_notice` also labels fixed collections such as forums and
libraries. Featured-date and live news are not implicitly labelled as archive
pages. Publication-sensitive services must still gate stories by the full date.
`cis_discovery.start_suggestions` supplies the three date-aware GO START choices;
the standard navigation router opens their destinations.

## Packaging

`pyproject.toml` lists every runtime module. `build_support.BuildPy` copies seed
JSON and browser files beside those modules in wheels; `MANIFEST.in` carries
those resources into source distributions. When adding a runtime module, update
the module list. `tests/check_installed_package.py` checks wheel contents and
runs isolated imports, content loading, entry-point resolution and database
initialization after a real pip installation outside the checkout.

The deterministic release ZIP includes its build configuration and excludes
Git metadata, build output, tests and runtime files. Superseded patch and bundle
handoffs were removed in 1.17.0; their history remains in Git.

## Main boundaries

- **Terminal application:** `compuserve.py`, `cis_terminal.py`, `cis_session.py`
- **Services:** the remaining `cis_*.py` modules
- **Persistence:** `cis_storage.py`, `cis_migrations.py`, `compuserve.db`
- **Transports:** `web_app.py`, `telnet_app.py`, and the local console
- **Historical content:** root JSON files and `downloads/`
- **Operations:** `event_worker.py`, `build_release.py`, and `install-linux.sh`

## Direction of travel

New features should live in focused service modules instead of enlarging
`compuserve.py`. Session-specific mutable values should gradually move into
`SessionState`; persistent shared values belong behind `cis_storage.py`. Runtime
artifacts should not be added to release archives.
