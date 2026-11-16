# SysOp and maintenance

## Local SysOp maintenance

Log in with a profile marked as SysOp and enter `GO SYSOP`. The console can unlock or
disable accounts, reset forgotten passwords, approve or reject uploads, review feedback
and simulated orders, post IBMHW announcements, and create or restore backups. A reset
replaces the password with a one-time temporary password shown to the SysOp; relay it
privately. The member must choose a new password after signing in with it.
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
output is capped at 500 lines. Combined stdout and stderr capture is limited to
1 MiB; exceeding that limit stops the command. Standard input is closed, so commands
cannot prompt for input. On timeout or excess output, the simulator terminates the
process group on Unix or uses `taskkill /T /F` on Windows to stop the shell and its
ordinary descendants. Processes that deliberately detach can escape this boundary;
on Windows, descendants can also escape if their parent shell has already exited
before cleanup. Use the service sandbox to constrain their permissions. Process
cleanup takes additional time beyond the command's execution deadline.

Use a dedicated, unprivileged service account with access only to the simulator's
required files. Remote SysOps inherit that account's permissions. The provided
systemd unit restricts filesystem writes and privilege escalation; adapt its
`User`, `WorkingDirectory`, `ExecStart`, and `ReadWritePaths` before installation.

Command starts and completion, timeout, output-limit, or launch-error outcomes are recorded as
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
| `CIS_LLM_CONFIG` | `llm_config.json` beside the module | Optional local-model replies (see below) |
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

## Optional local-model replies

Without any setup, every simulated reply is scripted. Operators who run an
[Ollama](https://ollama.com) server can let small local models answer members
instead. This is entirely optional: if `llm_config.json` does not exist, nothing
contacts a model server and nothing changes.

To turn it on, copy `llm_config.example.json` to `llm_config.json` beside
`compuserve.py` (or point `CIS_LLM_CONFIG` at another file), set `ollama_url`,
and choose a model and prompt for each role. `llm_config.json` is local
configuration: git ignores it and release builds never include it, and upgrades
leave it in place. Check it with:

```text
python cis_llm.py --check
```

which lists each role, its model, and whether the server has that model.

| Role | Where it answers | How the member gets it |
| --- | --- | --- |
| `cb_chat` | CB Simulator: a simulated member replies to a live user's message, with recent scrollback as context. ELIZA's channel 4 keeps the ELIZA engine. | In the channel, while the member waits |
| `customer_service` | Feedback to Customer Service | On screen after "Your feedback has been recorded", while the member waits |
| `representative` | Questions to the Travel, Finance and Store representatives | EasyPlex mail; the model writes in the background |
| `warranty` | Equipment warranty cases | EasyPlex mail; the model writes in the background |

Each role has `model` and `prompt` (both required) and may set `enabled`,
`max_chars`, `temperature`, `timeout_seconds`, `context_lines` and
`multiline` (keep paragraph breaks; use it for mail). The prompt may use
`{placeholders}`: `{member}` everywhere, `{handle}`, `{channel}` and
`{channel_description}` for CB chat, `{name}` and `{department}` for
representatives, and `{product}` for warranty cases. Top-level settings are
`ollama_url`, `timeout_seconds`, `min_seconds_between_calls` (per session and
role), `max_input_chars` and `keep_alive` (how long the server keeps a model
loaded). Set `"enabled": false` at the top level to turn everything off. Edits
take effect on the next reply; no restart is needed.

Replies always fall back to the scripted text: when a role is missing or
disabled, the server is down or slow, the answer is empty, or calls come too
fast. Mailed replies are scheduled with the scripted text first and replaced
only if the model finishes before delivery, so members never wait for them.
Model output is cleaned for the terminal: ASCII only, no escape or control
characters, no markdown, and cut to `max_chars`.

Choosing models: live roles keep a member waiting, so use a small, fast model
there (on a CPU-only server, a 1-2B model answers in a few seconds; a 4B model
can take 10-25 seconds, longer when it must first load). Avoid models that
print their reasoning even with thinking turned off. Members' text goes to the
model server, and on a public Telnet gateway anyone can try to steer the
model, so keep prompts specific about staying in character and in 1988.

## Deployment checklist

1. Build and verify the package with `python tests/check_installed_package.py`;
   run `python smoke_test.py` and the regression commands below.
2. Back up `compuserve.db` and preserve runtime data before upgrading.
3. Configure a dedicated service account, the four marked systemd paths/settings,
   connection limits, a writable activity log, optional ntfy topic, and the
   optional `llm_config.json` (check it with `python cis_llm.py --check`).
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
python -m unittest -q tests.test_llm
python tests/check_installed_package.py
```

Run `python smoke_test.py` for a quick release check covering required packaged files,
Linux event-service assets, JSON data, and a temporary scripted member workflow.

---

[Back to the user guide](../USER_GUIDE.md)
