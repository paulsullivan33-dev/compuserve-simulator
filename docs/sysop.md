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


## Data protection

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

Run `python smoke_test.py` for a quick release check covering required packaged files,
Linux event-service assets, JSON data, and a temporary scripted member workflow.

---

[Back to the user guide](../USER_GUIDE.md)
