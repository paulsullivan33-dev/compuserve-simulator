# Architecture

`compuserve.py` owns the terminal session lifecycle and command router. Modules named
`cis_*.py` implement individual services and accept the application module as their
runtime context. `cis_storage.py` provides transactional SQLite persistence while the
JSON files in the project root provide immutable content and legacy seed data.

The browser and Telnet gateways each launch one isolated simulator process per
terminal session. Those processes communicate through SQLite for shared presence,
messages, and persistent member data.

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
