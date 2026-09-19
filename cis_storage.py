import json
import os
import sqlite3
import threading
from contextlib import contextmanager, closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile


DATABASE_FILENAME = "compuserve.db"
DEFAULT_BACKUP_RETENTION = 10
DEFAULT_UPGRADE_BACKUP_RETENTION = 5
MUTABLE_DATA_FILES = frozenset({
    "profiles.json", "forums.json", "easyplex.json", "cb_mail.json",
    "feedback.json", "orders.json", "library_files.json", "news.json",
    "terminal_config.json",
    "dynamic_state.json",
})


@contextmanager
def _connect(base_dir):
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(base_dir / DATABASE_FILENAME, timeout=5)
    try:
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            connection.execute("PRAGMA journal_mode = WAL")
        except sqlite3.OperationalError as exc:
            # Another new session may be enabling WAL at the same instant. Once
            # that transaction completes this connection can safely continue.
            if "locked" not in str(exc).lower():
                raise
        connection.execute("CREATE TABLE IF NOT EXISTS documents (filename TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS live_sessions (session_id TEXT PRIMARY KEY, user_id TEXT, handle TEXT, transport TEXT NOT NULL, connected_at TEXT NOT NULL, last_seen TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS live_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, sender TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS cb_presence (session_id TEXT PRIMARY KEY, room TEXT NOT NULL, handle TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS cb_ambient_claims (room TEXT NOT NULL, bucket INTEGER NOT NULL, PRIMARY KEY(room, bucket))")
        connection.execute("CREATE TABLE IF NOT EXISTS reference_cache (provider TEXT NOT NULL, query TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(provider, query))")
        connection.execute("CREATE INDEX IF NOT EXISTS live_messages_room_id ON live_messages(room, id)")
        connection.execute("INSERT OR IGNORE INTO metadata(key, value) VALUES ('storage_schema', '1')")
        connection.commit()
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _serialize(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


_write_locks_guard = threading.Lock()
_write_locks = {}


def _write_lock(base_dir):
    """Return the process-wide reentrant lock for one database file.

    SQLite serializes writers on its own, but threads racing BEGIN IMMEDIATE
    against each other can still exhaust the busy timeout under load and
    surface "database is locked". Holding this lock across each
    read-modify-write transaction removes that in-process contention
    entirely; the busy timeout remains as the backstop for other processes.
    """
    key = str(Path(base_dir).resolve() / DATABASE_FILENAME)
    with _write_locks_guard:
        lock = _write_locks.get(key)
        if lock is None:
            lock = threading.RLock()
            _write_locks[key] = lock
        return lock


def _backup_database(base_dir, destination):
    """Create a consistent SQLite backup and verify that it can be read."""
    with _connect(base_dir) as source, closing(sqlite3.connect(destination)) as target:
        source.backup(target)
    with closing(sqlite3.connect(destination)) as backup:
        result = backup.execute("PRAGMA quick_check").fetchone()[0]
    if result != "ok":
        Path(destination).unlink(missing_ok=True)
        raise RuntimeError(f"Backup integrity check failed: {result}")


def _prune_backups(backup_dir, pattern, keep):
    """Retain the newest matching backups; a negative value disables pruning."""
    if keep < 0:
        return
    for old_backup in sorted(Path(backup_dir).glob(pattern), reverse=True)[keep:]:
        old_backup.unlink()


def _read_document(base_dir, filename):
    with _connect(base_dir) as database:
        row = database.execute("SELECT payload FROM documents WHERE filename = ?", (filename,)).fetchone()
    return None if row is None else json.loads(row[0])


def _write_document(base_dir, filename, data):
    with _connect(base_dir) as database:
        database.execute(
            "INSERT INTO documents(filename, payload, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(filename) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
            (filename, _serialize(data), datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )


def migrate_json_to_sqlite(base_dir, filenames=MUTABLE_DATA_FILES):
    """Import each legacy mutable JSON file once, preserving it as a rollback copy."""
    base_dir = Path(base_dir)
    imported = []
    with _connect(base_dir) as database:
        existing = {row[0] for row in database.execute("SELECT filename FROM documents")}
        for filename in sorted(filenames):
            path = base_dir / filename
            if filename in existing or not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Cannot import {path}: {exc}") from exc
            database.execute(
                "INSERT INTO documents(filename, payload, updated_at) VALUES (?, ?, ?)",
                (filename, _serialize(data), datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
            imported.append(filename)
    return imported


def recover_json_from_backup(base_dir, filename):
    """Legacy ZIP recovery for immutable JSON files from older releases."""
    import zipfile
    backup_dir = Path(base_dir) / "backups"
    archives = sorted(backup_dir.glob("CIS-*.zip"), reverse=True) if backup_dir.exists() else []
    for archive in archives:
        try:
            with zipfile.ZipFile(archive) as backup:
                if filename in backup.namelist():
                    return backup.read(filename).decode("utf-8")
        except (OSError, zipfile.BadZipFile, UnicodeDecodeError):
            continue
    return None


def load_json(base_dir, filename, default=None):
    base_dir = Path(base_dir)
    if filename in MUTABLE_DATA_FILES:
        migrate_json_to_sqlite(base_dir, (filename,))
        data = _read_document(base_dir, filename)
        if data is not None:
            return data
        if default is not None:
            return default
        raise RuntimeError(f"Required data is missing from {base_dir / DATABASE_FILENAME}: {filename}")

    path = base_dir / filename
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        if default is not None:
            return default
        raise RuntimeError(f"Required data file is missing: {path}")
    except json.JSONDecodeError as exc:
        recovered = recover_json_from_backup(base_dir, filename)
        if recovered is None:
            raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc
        data = json.loads(recovered)
        damaged = path.with_name(path.name + datetime.now().strftime(".%Y%m%d%H%M%S.corrupt"))
        path.replace(damaged)
        path.write_text(recovered, encoding="utf-8")
        return data


def write_json_atomic(base_dir, filename, data):
    if filename in MUTABLE_DATA_FILES:
        _write_document(base_dir, filename, data)
        return
    base_dir = Path(base_dir)
    destination = base_dir / filename
    with NamedTemporaryFile("w", encoding="utf-8", dir=base_dir, delete=False, suffix=".tmp") as file:
        temporary = Path(file.name)
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.flush()
        os.fsync(file.fileno())
    try:
        temporary.replace(destination)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def update_json_atomic(base_dir, filename, default, mutator):
    """Read-modify-write one mutable document under a SQLite write lock."""
    if filename not in MUTABLE_DATA_FILES:
        raise ValueError(f"Transactional updates require a mutable document: {filename}")
    base_dir = Path(base_dir)
    with _write_lock(base_dir):
        migrate_json_to_sqlite(base_dir, (filename,))
        with _connect(base_dir) as database:
            database.execute("BEGIN IMMEDIATE")
            row = database.execute("SELECT payload FROM documents WHERE filename = ?", (filename,)).fetchone()
            data = json.loads(row[0]) if row else default
            result = mutator(data)
            database.execute(
                "INSERT INTO documents(filename, payload, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(filename) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
                (filename, _serialize(data), datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
    return result


def install_content_pack(base_dir, pack_id, mutators):
    """Install additive content once, atomically with its completion marker."""
    if not set(mutators) <= MUTABLE_DATA_FILES:
        raise ValueError('Content packs can only update mutable documents')
    with _write_lock(base_dir):
        migrate_json_to_sqlite(base_dir, mutators)
        with _connect(base_dir) as database:
            database.execute('BEGIN IMMEDIATE')
            marker = 'content-pack:' + pack_id
            if database.execute('SELECT value FROM metadata WHERE key = ?', (marker,)).fetchone():
                return False
            for filename, mutator in mutators.items():
                row = database.execute('SELECT payload FROM documents WHERE filename = ?', (filename,)).fetchone()
                data = mutator(json.loads(row[0]) if row else {})
                database.execute(
                    'INSERT INTO documents(filename, payload, updated_at) VALUES (?, ?, ?) '
                    'ON CONFLICT(filename) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at',
                    (filename, _serialize(data), datetime.now(timezone.utc).isoformat(timespec='seconds')),
                )
            database.execute('INSERT INTO metadata(key, value) VALUES (?, ?)', (marker, 'installed'))
    return True


def create_backup(base_dir, mutable_files=None, keep=DEFAULT_BACKUP_RETENTION):
    base_dir = Path(base_dir)
    migrate_json_to_sqlite(base_dir, mutable_files or MUTABLE_DATA_FILES)
    backup_dir = base_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    destination = backup_dir / datetime.now().strftime("CIS-%Y%m%d-%H%M%S-%f.db")
    _backup_database(base_dir, destination)
    _prune_backups(backup_dir, "CIS-*.db", keep)
    return destination


def restore_latest(base_dir, mutable_files=None):
    base_dir = Path(base_dir)
    backup_dir = base_dir / "backups"
    backups = sorted(backup_dir.glob("CIS-*.db"), reverse=True) if backup_dir.exists() else []
    if not backups:
        return None
    allowed = set(mutable_files or MUTABLE_DATA_FILES)
    with closing(sqlite3.connect(backups[0])) as source:
        rows = source.execute("SELECT filename, payload, updated_at FROM documents").fetchall()
    validated = [(name, payload, updated) for name, payload, updated in rows if name in allowed]
    for _, payload, _ in validated:
        json.loads(payload)
    with _connect(base_dir) as target:
        for filename, payload, updated_at in validated:
            target.execute(
                "INSERT INTO documents(filename, payload, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(filename) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
                (filename, payload, updated_at),
            )
    return backups[0]


def upgrade_database(base_dir, target_version, keep=DEFAULT_UPGRADE_BACKUP_RETENTION):
    """Run document-schema upgrades once, transactionally, with a pre-upgrade copy."""
    base_dir = Path(base_dir)
    migrate_json_to_sqlite(base_dir)
    with _connect(base_dir) as database:
        row = database.execute("SELECT value FROM metadata WHERE key = 'app_schema'").fetchone()
        current = int(row[0]) if row else 0
    if current >= target_version:
        return current, None

    backup_dir = base_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / f"PRE-UPGRADE-{current}-TO-{target_version}-{datetime.now():%Y%m%d-%H%M%S-%f}.db"
    _backup_database(base_dir, backup)
    _prune_backups(backup_dir, "PRE-UPGRADE-*.db", keep)

    with _connect(base_dir) as database:
        rows = {name: json.loads(payload) for name, payload in database.execute("SELECT filename, payload FROM documents")}
        dynamic = rows.get("dynamic_state.json", {})
        classifieds = dynamic.get("classifieds", []) if isinstance(dynamic, dict) else []
        used = {item.get("id") for item in classifieds if isinstance(item, dict) and isinstance(item.get("id"), int)}
        next_id = max(used, default=0) + 1
        for item in classifieds:
            if not isinstance(item, dict):
                continue
            if not isinstance(item.get("id"), int):
                item["id"] = next_id
                next_id += 1
            text = item.get("text", "")
            item.setdefault("seller", text.rsplit("USER ", 1)[-1] if "USER " in text else "COMPUSERVE")
            item.setdefault("status", "ACTIVE")
        if isinstance(dynamic, dict):
            dynamic["next_classified_id"] = max((i.get("id", 0) for i in classifieds if isinstance(i, dict)), default=0) + 1
            rows["dynamic_state.json"] = dynamic
        profiles = rows.get("profiles.json", {})
        if isinstance(profiles, dict):
            for profile in profiles.values():
                if isinstance(profile, dict):
                    profile.setdefault("watched_threads", [])
                    profile.setdefault("mail_folders", [])
                    profile.setdefault("address_book", {})
        forums = rows.get("forums.json", {})
        if isinstance(forums, dict):
            for messages in forums.values():
                for message in messages if isinstance(messages, list) else []:
                    if isinstance(message, dict):
                        message.setdefault("parent_id", None)
        mail = rows.get("easyplex.json", [])
        if isinstance(mail, list):
            for message in mail:
                if isinstance(message, dict):
                    message.setdefault("folder", "INBOX")
        orders = rows.get("orders.json", [])
        if isinstance(orders, list):
            for order in orders:
                if isinstance(order, dict):
                    order.setdefault("status", "RECEIVED")
        if isinstance(dynamic, dict):
            for item in dynamic.get("classifieds", []):
                if isinstance(item, dict):
                    item.setdefault("category", "GENERAL")
            for reservation in dynamic.get("reservations", []):
                if isinstance(reservation, dict):
                    reservation.setdefault("status", "CONFIRMED")
        rows["easyplex.json"] = mail
        rows["orders.json"] = orders
        for filename in ("dynamic_state.json", "profiles.json", "forums.json", "easyplex.json", "orders.json"):
            if filename in rows:
                database.execute("UPDATE documents SET payload = ?, updated_at = ? WHERE filename = ?", (_serialize(rows[filename]), datetime.now(timezone.utc).isoformat(timespec="seconds"), filename))
        database.execute("INSERT INTO metadata(key, value) VALUES ('app_schema', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(target_version),))
    return target_version, backup


def database_status(base_dir):
    base_dir = Path(base_dir)
    path = base_dir / DATABASE_FILENAME
    with _connect(base_dir) as database:
        integrity = database.execute("PRAGMA integrity_check").fetchone()[0]
        row = database.execute("SELECT value FROM metadata WHERE key = 'app_schema'").fetchone()
        documents = database.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    return {"integrity": integrity, "schema": int(row[0]) if row else 0, "documents": documents, "bytes": path.stat().st_size if path.exists() else 0}


def register_session(base_dir, session_id, user_id, handle, transport):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        database.execute("INSERT INTO live_sessions(session_id, user_id, handle, transport, connected_at, last_seen) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET user_id=excluded.user_id, handle=excluded.handle, transport=excluded.transport, last_seen=excluded.last_seen", (session_id, user_id, handle, transport, now, now))


def unregister_session(base_dir, session_id):
    with _connect(base_dir) as database:
        database.execute("DELETE FROM live_sessions WHERE session_id = ?", (session_id,))


def list_sessions(base_dir):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        database.execute("DELETE FROM live_sessions WHERE last_seen < ?", (cutoff,))
        return database.execute("SELECT session_id, user_id, handle, transport, connected_at FROM live_sessions ORDER BY connected_at").fetchall()


def post_live_message(base_dir, room, sender, body):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        cursor = database.execute("INSERT INTO live_messages(room, sender, body, created_at) VALUES (?, ?, ?, ?)", (room, sender[:40], body[:1000], now))
        return cursor.lastrowid


def read_live_messages(base_dir, room, after_id=0, limit=50):
    with _connect(base_dir) as database:
        return database.execute("SELECT id, sender, body, created_at FROM live_messages WHERE room = ? AND id > ? ORDER BY id LIMIT ?", (room, after_id, limit)).fetchall()


def recent_live_messages(base_dir, room, limit=20):
    with _connect(base_dir) as database:
        rows = database.execute("SELECT id, sender, body, created_at FROM live_messages WHERE room = ? ORDER BY id DESC LIMIT ?", (room, limit)).fetchall()
        return list(reversed(rows))


def set_cb_presence(base_dir, session_id, room, handle, status="AVAILABLE"):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        database.execute("INSERT INTO cb_presence(session_id, room, handle, status, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET room=excluded.room, handle=excluded.handle, status=excluded.status, updated_at=excluded.updated_at", (session_id, room, handle[:40], status[:16], now))


def remove_cb_presence(base_dir, session_id):
    with _connect(base_dir) as database:
        database.execute("DELETE FROM cb_presence WHERE session_id = ?", (session_id,))


def list_cb_presence(base_dir, room=None):
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        database.execute("DELETE FROM cb_presence WHERE updated_at < ?", (cutoff,))
        if room is None:
            return database.execute("SELECT room, handle, status, updated_at FROM cb_presence ORDER BY room, handle").fetchall()
        return database.execute("SELECT room, handle, status, updated_at FROM cb_presence WHERE room = ? ORDER BY handle", (room,)).fetchall()


def claim_cb_ambient(base_dir, room, bucket):
    """Allow only one connected process to generate a room's ambient batch."""
    with _connect(base_dir) as database:
        cursor = database.execute("INSERT OR IGNORE INTO cb_ambient_claims(room, bucket) VALUES (?, ?)", (room, int(bucket)))
        database.execute("DELETE FROM cb_ambient_claims WHERE bucket < ?", (int(bucket) - 1440,))
        return cursor.rowcount == 1


def write_reference_cache(base_dir, provider, query, records):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(base_dir) as database:
        database.execute(
            "INSERT INTO reference_cache(provider, query, payload, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(provider, query) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at",
            (provider.lower(), query.strip().casefold(), _serialize(records), now),
        )


def read_reference_cache(base_dir, provider, query, max_age_hours=24, allow_expired=False):
    with _connect(base_dir) as database:
        row = database.execute(
            "SELECT payload, updated_at FROM reference_cache WHERE provider = ? AND query = ?",
            (provider.lower(), query.strip().casefold()),
        ).fetchone()
    if not row:
        return None
    updated = datetime.fromisoformat(row[1])
    if not allow_expired and updated < datetime.now(timezone.utc) - timedelta(hours=max_age_hours):
        return None
    return json.loads(row[0])
