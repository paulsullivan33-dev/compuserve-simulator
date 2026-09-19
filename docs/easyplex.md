# EasyPlex

## EasyPlex

EasyPlex supports numeric-ID mail, Inbox and Sent folders, unread notices, directory
lookup, reply, forward, delete, and Postmaster failure notices. Message composition uses
LINEDIT. Type `LIST`, `DELETE n`, `REPLACE n text`, `SAVE`, or `ABORT`.
EasyPlex and Forum compositions are saved after every LINEDIT change. If a connection
drops or `ABORT` is entered, begin another composition and select `R` to resume the
draft or `D` to delete it. A successfully sent or posted draft is removed automatically.
`GO DRAFTS` opens the Personal Draft Center, where saved mail, new Forum posts, and
Forum replies can be previewed, resumed directly, or deleted after confirmation.
Unfinished drafts also appear in `GO NEW`.

`GO TIMELINE` opens a curated offline history of December 1988, with at least one
entry for every day of the month. Use `F` and `B` to
browse days, `C` to choose a date, `S` to search, and `MARK id`, `MARKED`, and
`DOWNLOAD` to prepare an attributed ASCII research packet. Exact dated events are
distinguished from broader period-context entries. The simulated day's entries appear
in `GO NEW`, and timeline text is included in the global `FIND words` search. Source
names and URLs are shipped inside `historical_timeline.json`; browsing does not require
an Internet connection.

Timeline and offline reference articles display numbered linked records. Select a
number or record ID to follow a connection, use `RELATED` or `TIMELINE` to review the
available links, and enter `BACK` to return to the originating article. Timeline
research packets include a titled index of each cited reference record.

`GO FEATURES` opens five curated, offline multi-day stories. Use `N` and `P` to move
between chapters, `LINKS` to open a chapter's timeline and reference sources,
`BOOKMARK` to save or remove a story, and `DOWNLOAD` to prepare an ASCII edition.
Reading position is saved automatically. New-story notices appear in `GO NEW`, and
feature text is included in the global `FIND words` search.

After login, `TODAY IN 1988` provides a one-screen briefing with the simulated date's
history, unread service totals, live modern weather, and a rotating reference fact.
The weather city defaults to Chicago and remembers the last city entered in
`GO WEATHER`. From any menu, use `READ HISTORY`, `READ WEATHER`, or `READ NEW` to
open those services directly.

---

[Back to the user guide](../USER_GUIDE.md)
