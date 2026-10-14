# SysOp and maintenance

## Local SysOp maintenance

Log in with a profile marked as SysOp and enter `GO SYSOP`. The console can unlock or
disable accounts, reset forgotten passwords, approve or reject uploads, review feedback
and simulated orders, post IBMHW announcements, and create or restore backups. A reset
removes the old hash; the member establishes a replacement password at next login.
Simulation World Controls can publish or clear persistent market, weather, travel, and
catalog bulletins that appear in their corresponding services.
SysOp option 11 manages scheduled system announcements. Announcements support normal,
important, and emergency priorities; may target all members or one User ID; may start
on a future simulation date; and may expire automatically. Active announcements appear
on the main page, while unread announcements are selectable in `GO NEW` and retain
per-member read status.
The Dynamic Event Monitor also accepts `REPAIR STATE` to validate and repair malformed
new-service containers, events, portfolios, notebooks, and reservations while retaining
a short repair log.


## Operating-system commands

SysOp option 12 runs non-interactive shell commands as the OS account running the
simulator. Both the console and command handler require a signed-in SysOp profile.
Enter a blank line or `M` to return. Commands have a 60-second timeout; displayed
output is capped at 500 lines. This display cap does not limit captured output in
memory. The timeout applies to the shell process; commands that spawn background
processes may leave those processes running.

Use a dedicated, unprivileged service account with access only to the simulator's
required files. Remote SysOps inherit that account's permissions. The provided
systemd unit restricts filesystem writes and privilege escalation; adapt its
`User`, `WorkingDirectory`, `ExecStart`, and `ReadWritePaths` before installation.

Command starts and completion, timeout, or launch-error outcomes are recorded as
`sysop_os_command` activity events with member and session identifiers. Command
text and output are omitted because they can contain credentials. Activity logging
is best-effort, so a log write failure does not prevent execution.

## Telnet, activity logs, and notifications

Run `python telnet_app.py` to start the gateway. Its environment settings are:

| Setting | Default | Purpose |
| --- | --- | --- |
| `CIS_TELNET_HOST` | `0.0.0.0` | Listen address |
| `CIS_TELNET_PORT` | `2323` | Listen port |
| `CIS_TELNET_MAX_SESSIONS` | `20` | Concurrent connections |
| `CIS_TELNET_MAX_SESSIONS_PER_IP` | `3` | Connections from one address |
| `CIS_TELNET_IDLE_TIMEOUT` | `900` | Input idle timeout in seconds |
| `CIS_ACTIVITY_LOG` | `activity.log` beside the module | JSON-lines activity log |
| `CIS_NTFY_URL` | unset | Full ntfy topic URL; unset disables notifications |
| `CIS_TELNET_DEBUG` | unset | Set to `1` for raw protocol tracing |

Review recent activity with `python cis_activity.py --tail 50`, or filter using
`--event login_failed`. Events include connections, authentication failures,
lockouts, and session endings. Failed-password lockouts expire after 15 minutes;
SysOps may also unlock accounts manually. First-time visitors can enter `NEW` at
the User ID prompt; blank User IDs are rejected.

ntfy sends login alerts asynchronously and logout alerts synchronously with a
five-second request timeout. Logout alerts include session duration. Use a topic
appropriate for the member identifiers and client addresses in the alerts.
Protocol tracing can contain raw input, including passwords; enable it only for
controlled troubleshooting and protect the trace output.

## Deployment checklist

1. Build and verify the package with `python tests/check_installed_package.py`;
   run `python smoke_test.py` and the regression commands below.
2. Back up `compuserve.db` and preserve runtime data before upgrading.
3. Configure a dedicated service account, the four marked systemd paths/settings,
   connection limits, a writable activity log, and optional ntfy topic.
4. Start the service and inspect `systemctl status compuserve-telnet` and
   `journalctl -u compuserve-telnet` for startup errors.
5. Connect with a real terminal: verify login, password masking on negotiating
   clients, scrolling, logout, and matching activity events. For a C64 client,
   select the C64 preset and verify PETSCII input/output and pacing.
6. Verify an ordinary member is denied `GO SYSOP`; check a trusted SysOp's shell
   access using a harmless command and confirm its outcome appears in the log.

## Database backups

Mutable data is stored in `compuserve.db`, a local SQLite database. On the first run
after upgrading, existing mutable JSON files are imported automatically and retained as
rollback copies. Up to ten consistent SQLite backups are kept under `backups`.
Static menus and seed content remain JSON. Versioned migrations add new fields to older
data without discarding existing messages, accounts, or library records.


## Building a release

Run `build_release.cmd` (or `python build_release.py`). It creates a reproducible ZIP
under `dist` using only Python's standard library. The ZIP includes a manifest with a
SHA-256 checksum for every shipped file.


## Running tests

Run:

```text
python -m unittest -v
```

The targeted operational checks are:

```text
python -m unittest -q test_compuserve.SysopOsShellTests test_activity_log test_ntfy
python tests/check_installed_package.py
```

Run `python smoke_test.py` for a quick release check covering required packaged files,
Linux event-service assets, JSON data, and a temporary scripted member workflow.

---

[Back to the user guide](../USER_GUIDE.md)
