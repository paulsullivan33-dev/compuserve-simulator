#!/usr/bin/env bash
set -euo pipefail

APP_NAME="compuserve"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${CIS_INSTALL_DIR:-$HOME/compuserve}"
PYTHON_BIN="${CIS_PYTHON:-python3}"
INSTALL_SERVICE=0
INSTALL_TELNET_SERVICE=0
UPGRADE_MODE=0
NONINTERACTIVE=0
STAGING_DIR=""
ROLLBACK_DIR=""
NEW_FILES_LIST=""
DEPLOYMENT_ACTIVE=0
TARGET_VERSION="unknown"
CURRENT_VERSION="not installed"

usage() {
    echo "Usage: $0 [--install-dir PATH] [--systemd-user] [--telnet] [--upgrade] [--non-interactive]"
    echo
    echo "Environment overrides: CIS_INSTALL_DIR, CIS_PYTHON"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install-dir)
            [[ $# -ge 2 ]] || { echo "--install-dir requires a path" >&2; exit 2; }
            INSTALL_DIR="$2"
            shift 2
            ;;
        --systemd-user)
            INSTALL_SERVICE=1
            shift
            ;;
        --telnet)
            INSTALL_TELNET_SERVICE=1
            shift
            ;;
        --upgrade)
            UPGRADE_MODE=1
            shift
            ;;
        --non-interactive)
            NONINTERACTIVE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

cleanup() {
    [[ -z "$STAGING_DIR" || ! -d "$STAGING_DIR" ]] || rm -rf -- "$STAGING_DIR"
}
trap cleanup EXIT

rollback_application() {
    [[ $DEPLOYMENT_ACTIVE -eq 1 && -n "$ROLLBACK_DIR" && -d "$ROLLBACK_DIR" ]] || return 0
    echo "Update failed; restoring application files from $ROLLBACK_DIR" >&2
    DEPLOYMENT_ACTIVE=0
    if [[ -n "$NEW_FILES_LIST" && -f "$NEW_FILES_LIST" ]]; then
        while IFS= read -r -d '' relative; do
            rm -f -- "$INSTALL_DIR/$relative"
        done < "$NEW_FILES_LIST"
    fi
    copy_application_tree "$ROLLBACK_DIR" "$INSTALL_DIR"
    set +e
    if [[ $INSTALL_SERVICE -eq 1 ]]; then
        systemctl --user daemon-reload
        systemctl --user restart "$APP_NAME.service"
    fi
    if [[ $INSTALL_TELNET_SERVICE -eq 1 ]]; then
        systemctl --user daemon-reload
        systemctl --user restart "$APP_NAME-telnet.service"
    fi
    set -e
}

on_error() {
    local status=$?
    rollback_application
    exit "$status"
}
trap on_error ERR

command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
    echo "Python 3 was not found. Install python3 and python3-venv first." >&2
    exit 1
}

"$PYTHON_BIN" -c 'import sqlite3, sys; assert sys.version_info >= (3, 10)' 2>/dev/null || {
    echo "Python 3.10 or newer with SQLite support is required." >&2
    exit 1
}

read_version() {
    local directory="$1"
    [[ -f "$directory/cis_version.py" ]] || return 1
    "$PYTHON_BIN" -c 'import runpy, sys; print(runpy.run_path(sys.argv[1])["VERSION"])' "$directory/cis_version.py"
}

verify_manifest() {
    local directory="$1"
    [[ -f "$directory/RELEASE_MANIFEST.json" ]] || return 0
    "$PYTHON_BIN" - "$directory" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()
manifest = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
for relative, expected in manifest.get("files", {}).items():
    candidate = (root / relative).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise SystemExit(f"Release manifest file is missing or unsafe: {relative}")
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"Release manifest mismatch: {relative}")
print(f"Verified {len(manifest.get('files', {}))} release files")
PY
}

copy_application_tree() {
    local source_root="$1"
    local destination_root="$2"
    while IFS= read -r -d '' source; do
        local relative="${source#"$source_root"/}"
        case "$relative" in
            .venv/*|backups/*|captures/*|dist/*|downloads/*|uploads/*|__pycache__/*|compuserve.db|compuserve.db-shm|compuserve.db-wal)
                continue
                ;;
        esac
        local destination="$destination_root/$relative"
        # Existing legacy data may not have been imported into SQLite yet.
        # Release starter data must never replace it during an upgrade.
        if [[ "$destination_root" == "$INSTALL_DIR" && -f "$destination" ]]; then
            case "$relative" in
                profiles.json|forums.json|easyplex.json|cb_mail.json|feedback.json|orders.json|library_files.json|news.json|terminal_config.json|dynamic_state.json)
                    continue
                    ;;
            esac
        fi
        if [[ -d "$source" ]]; then
            mkdir -p "$destination"
        else
            mkdir -p "$(dirname "$destination")"
            cp -p "$source" "$destination"
        fi
    done < <(find "$source_root" -mindepth 1 -print0)
}

backup_live_database() {
    local database="$INSTALL_DIR/compuserve.db"
    [[ -f "$database" ]] || return 0
    mkdir -p "$INSTALL_DIR/backups"
    local backup="$INSTALL_DIR/backups/CIS-PRE-INSTALL-$(date -u +%Y%m%d-%H%M%S).db"
    "$PYTHON_BIN" - "$database" "$backup" <<'PY'
import sqlite3
import sys

source_path, backup_path = sys.argv[1:]
with sqlite3.connect(source_path) as source, sqlite3.connect(backup_path) as target:
    source.backup(target)
with sqlite3.connect(backup_path) as backup:
    result = backup.execute("PRAGMA quick_check").fetchone()[0]
if result != "ok":
    raise SystemExit(f"Pre-install backup failed integrity check: {result}")
print(f"Verified database backup: {backup_path}")
PY
}

verify_manifest "$SOURCE_DIR"
TARGET_VERSION="$(read_version "$SOURCE_DIR" || echo unknown)"
if [[ -f "$INSTALL_DIR/cis_version.py" ]]; then
    CURRENT_VERSION="$(read_version "$INSTALL_DIR" || echo unknown)"
fi
echo "Current version: $CURRENT_VERSION"
echo "Target version:  $TARGET_VERSION"

if [[ $UPGRADE_MODE -eq 1 && ! -f "$INSTALL_DIR/cis_version.py" ]]; then
    echo "--upgrade requires an existing installation at $INSTALL_DIR" >&2
    exit 1
fi

if [[ $UPGRADE_MODE -eq 1 && $NONINTERACTIVE -eq 0 ]]; then
    read -r -p "Upgrade this installation? [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]] || { echo "Upgrade cancelled."; exit 0; }
fi

mkdir -p "$INSTALL_DIR"
SOURCE_REAL="$(cd "$SOURCE_DIR" && pwd -P)"
INSTALL_REAL="$(cd "$INSTALL_DIR" && pwd -P)"

if [[ $UPGRADE_MODE -eq 1 && "$SOURCE_REAL" == "$INSTALL_REAL" ]]; then
    echo "--upgrade must be run from a newly extracted release outside the live installation" >&2
    exit 1
fi

if [[ "$SOURCE_REAL" != "$INSTALL_REAL" ]]; then
    echo "Staging application files"
    STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/compuserve-update.XXXXXX")"
    copy_application_tree "$SOURCE_DIR" "$STAGING_DIR"
    "$PYTHON_BIN" -m compileall -q -x '(^|/)(old_versions)(/|$)' "$STAGING_DIR"
    if [[ -f "$STAGING_DIR/smoke_test.py" ]]; then
        (cd "$STAGING_DIR" && "$PYTHON_BIN" smoke_test.py)
    fi
    rm -f -- "$STAGING_DIR/compuserve.db" "$STAGING_DIR/compuserve.db-shm" "$STAGING_DIR/compuserve.db-wal"
    rm -rf -- "$STAGING_DIR/backups" "$STAGING_DIR/captures" "$STAGING_DIR/downloads" "$STAGING_DIR/uploads"

    backup_live_database
    if [[ -f "$INSTALL_DIR/cis_version.py" ]]; then
        ROLLBACK_DIR="$INSTALL_DIR/backups/application-$CURRENT_VERSION-$(date -u +%Y%m%d-%H%M%S)"
        mkdir -p "$ROLLBACK_DIR"
        copy_application_tree "$INSTALL_DIR" "$ROLLBACK_DIR"
        NEW_FILES_LIST="$ROLLBACK_DIR.new-files"
        : > "$NEW_FILES_LIST"
        while IFS= read -r -d '' staged; do
            relative="${staged#"$STAGING_DIR"/}"
            if [[ -f "$staged" && ! -e "$INSTALL_DIR/$relative" ]]; then
                printf '%s\0' "$relative" >> "$NEW_FILES_LIST"
            fi
        done < <(find "$STAGING_DIR" -mindepth 1 -print0)
        echo "Application rollback copy: $ROLLBACK_DIR"
    fi

    echo "Installing staged application files into $INSTALL_DIR"
    DEPLOYMENT_ACTIVE=1
    copy_application_tree "$STAGING_DIR" "$INSTALL_DIR"
else
    echo "Installing in place at $INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR/backups" "$INSTALL_DIR/captures" "$INSTALL_DIR/downloads" "$INSTALL_DIR/uploads"

if [[ ! -x "$INSTALL_DIR/.venv/bin/python" ]]; then
    echo "Creating Python virtual environment"
    "$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv" || {
        echo "Unable to create the virtual environment. On Ubuntu/Debian run:" >&2
        echo "  sudo apt install python3-venv" >&2
        exit 1
    }
fi

if ! "$INSTALL_DIR/.venv/bin/python" -m pip --version >/dev/null 2>&1; then
    echo "The virtual environment has no pip; attempting to repair it"
    if ! "$INSTALL_DIR/.venv/bin/python" -m ensurepip --upgrade; then
        echo >&2
        echo "Python's venv/pip components are not installed. On Ubuntu/Debian run:" >&2
        echo "  sudo apt update" >&2
        echo "  sudo apt install python3-venv python3-pip" >&2
        echo "Then remove the incomplete environment and run this installer again:" >&2
        echo "  rm -rf \"$INSTALL_DIR/.venv\"" >&2
        if [[ $INSTALL_SERVICE -eq 1 ]]; then
            echo "  $0 --systemd-user" >&2
        else
            echo "  $0" >&2
        fi
        exit 1
    fi
fi

echo "Installing Python dependencies"
"$INSTALL_DIR/.venv/bin/python" -m pip install --disable-pip-version-check -r "$INSTALL_DIR/requirements-web.txt"

cat > "$INSTALL_DIR/start-linux.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/web_app.py"
EOF
chmod 750 "$INSTALL_DIR/start-linux.sh"

cat > "$INSTALL_DIR/start-telnet-linux.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/telnet_app.py"
EOF
chmod 750 "$INSTALL_DIR/start-telnet-linux.sh"

if [[ $INSTALL_SERVICE -eq 1 ]]; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    cat > "$SERVICE_DIR/$APP_NAME.service" <<EOF
[Unit]
Description=Classic CompuServe Web Terminal
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start-linux.sh
Restart=on-failure
RestartSec=3
Environment=CIS_WEB_HOST=0.0.0.0
Environment=CIS_WEB_PORT=8000

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$APP_NAME.service"
    systemctl --user restart "$APP_NAME.service"
    systemctl --user is-active --quiet "$APP_NAME.service"
    echo "User service enabled: $APP_NAME.service"

    cat > "$SERVICE_DIR/$APP_NAME-events.service" <<EOF
[Unit]
Description=Classic CompuServe Due Event Processor

[Service]
Type=oneshot
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/event_worker.py
EOF

    cat > "$SERVICE_DIR/$APP_NAME-events.timer" <<EOF
[Unit]
Description=Process Classic CompuServe events every five minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=30s
Persistent=true

[Install]
WantedBy=timers.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$APP_NAME-events.timer"
    systemctl --user restart "$APP_NAME-events.timer"
    systemctl --user is-active --quiet "$APP_NAME-events.timer"
    echo "Event timer enabled: $APP_NAME-events.timer"
fi

if [[ $INSTALL_TELNET_SERVICE -eq 1 ]]; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    cat > "$SERVICE_DIR/$APP_NAME-telnet.service" <<EOF
[Unit]
Description=Classic CompuServe Telnet Terminal
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start-telnet-linux.sh
Restart=on-failure
RestartSec=3
Environment=CIS_TELNET_HOST=0.0.0.0
Environment=CIS_TELNET_PORT=2323

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "$APP_NAME-telnet.service"
    systemctl --user restart "$APP_NAME-telnet.service"
    systemctl --user is-active --quiet "$APP_NAME-telnet.service"
    echo "User service enabled: $APP_NAME-telnet.service"
fi

printf '%s\n' "$TARGET_VERSION" > "$INSTALL_DIR/.installed-version"
DEPLOYMENT_ACTIVE=0

echo
echo "Installation complete."
echo "Application directory: $INSTALL_DIR"
if [[ $INSTALL_SERVICE -eq 0 ]]; then
    echo "Start it with: $INSTALL_DIR/start-linux.sh"
fi
echo "Open: http://SERVER-IP:8000"
if [[ $INSTALL_TELNET_SERVICE -eq 1 ]]; then
    echo "Terminal: telnet SERVER-IP 2323"
fi
