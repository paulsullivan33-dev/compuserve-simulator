# CompuServe Simulator — Architecture Document

**Version:** 1.18.0 · **Release commit:** `c879007` · **Authored:** 2026-09-22

## Why this document exists

The simulator is now ~95 Python files and roughly 40,000+ lines of code — too large
to paste into an LLM whole. This document is the map. **Read this file, then work
on one module at a time.** Each module section tells you what the file does, its
key entry points, and how it plugs into the rest of the app, so a single module
plus this document is enough context to modify that module safely.

This document covers the repo as of release 1.18.0. It is a companion to the
in-repo `ARCHITECTURE.md` (implementation notes) and `CONTRIBUTING.md` (branch
workflow); neither needs to be re-read before doing module work.

---

## 1. Big picture

The app is a historical simulation of the text-mode CompuServe Information
Service as of **December 1988**, with a time-capsule mode that can rewind to
other dates (1979–1998). Everything the member sees is a 1988 terminal screen.

### Entry points

| Entry point | File | What it is |
|---|---|---|
| Terminal (primary) | `compuserve.py` | `py -3 compuserve.py` — the full interactive session: dial-in, login, menus, all services |
| Web terminal | `web_app.py` | FastAPI app; spawns one `compuserve.py` process per browser session over WebSocket, plus per-session file delivery |
| Telnet gateway | `telnet_app.py` | TCP/Telnet-style gateway launching one isolated session per connection |
| Background worker | `event_worker.py` | Processes due simulated events (mail delivery, scheduled content) with no interactive session |
| Sysop tool | `make_sysop.py` | CLI: grants/revokes sysop flag for a member id |

The browser and Telnet gateways each launch **one isolated `compuserve.py`
process per terminal session**. Those processes share state only through
**SQLite** (`compuserve.db`) — presence, live messages, and persistent member
data. No shared in-memory state.

### The coordinator: `compuserve.py`

`compuserve.py` (~3,850 lines) owns the session lifecycle and the command
router. It does not implement services itself; it dispatches to `cis_*.py`
modules. The central dispatch:

1. Member types `GO <word>` (or picks a menu number).
2. `resolve_go_destination()` maps the word through `go_commands.json` →
   internal target id (also registers forum ids and file-library ids into
   `PAGE_ADDRESSES` at startup).
3. `open_go_destination(target, stack)` opens it: a `direct_services` dict
   maps target ids to service functions, `FORUM_CATALOG` keys open forums via
   `forum_service()`, and special cases route to specific modules.

**The module-calling convention:** every service module accepts the application
module as its runtime context — calls look like
`cis_arcade.play(sys.modules[__name__])` and inside the module the parameter is
named `app`. Modules never print or read stdin directly; they use
`app.ansi_scroll(text, 0.01)` for output and `app.input()` for input.

### Menu model: `screens.json`

Declarative menu screens. Each key is a screen with `title`, `page`,
`options` (number → label), and `targets` (number → destination id or
`quick:WORD`). Some screens are `poster: true` — photo-backed menus
reconstructed from photos of a real CompuServe poster; `cis_poster.py` renders
them and honors `related_targets` for the related reconstructed services.

### GO words: `go_commands.json` and `poster_words.json`

- `go_commands.json` — maps every `GO WORD` to an internal target id (149+
  destinations: forums, libraries, news specials, games, services).
- `poster_words.json` — the 27 quick-reference words from the real poster
  (e.g. `MAUG`), mapping label → target. `cis_poster.open_word()` resolves
  them via the `quick:` prefix.

### Storage: SQLite is truth, JSON files are seeds

`cis_storage.py` provides transactional SQLite persistence:

- Database file: `compuserve.db`. Mutable state lives in the **`documents`**
  table (each logical file — `forums.json`, `profiles.json`, etc. — is one
  document row). **Editing the on-disk `forums.json` directly does nothing** —
  the app reads from the `documents` table.
- On-disk JSON files in the repo root are **legacy seed data** / immutable
  content packs. `migrate_json_to_sqlite` imported them once.
- Content packs install via `cis_storage.install_content_pack()` (exposed as
  `cis_communities.install()`), **keyed by the pack `id`** in
  `computer_communities.json`. The merge is idempotent: it skips already-known
  `content_id`s. **When you append new seed posts or files to
  `computer_communities.json`, bump the pack id** (e.g. v5 → v6) or existing
  member databases will skip the merge and the new forums will be empty.
- Forum posts, library files, member profiles, CB presence, live messages,
  reference caches — all document-backed through `cis_storage.load_json` /
  `update_json_atomic`.

### Content packs and forums

`computer_communities.json` is the master seed: forum definitions (title,
sections, library), seed messages, seed library files, under a top-level pack
`id` (currently `computer-communities-1988-v5`). Each forum content module
(`cis_hamnet.py`, `cis_guitar.py`, …) declares `FORUM_ID`, `FORUM_TITLE`,
`SECTIONS`, `SEED_POSTS` plus `section_spec()` / `seed_posts()` accessors; the
coordinator wires the section specs into `FORUM_CATALOG` and the pack install
merges the seed posts.

### Time-capsule system

- `cis_timecapsule.py` — login-time era selection: 14 curated featured dates
  (1979–1998) plus free-form date and "surprise me"; per-account era memory.
- Per-date content packs (archival headlines, announcements, CB topics, market
  notes) live in `timecapsule_packs.json`.
- `cis_dynamic.py` — deterministic simulation clock: `simulation_day()`,
  daily content (forums, CB, trivia, markets, weather), scheduled events,
  member state. Deterministic seeding derived from the simulation date.
- Known limitation: daily forum story arcs stay 1988-flavored in all eras
  (shared global state, by design).

### Pure content + logic modules (the standard pattern)

Most services are "pure content + logic": they hold data and return line lists.
Rules of the pattern:

- Content functions take an optional `day` parameter defaulting to
  `cis_dynamic.simulation_day()`; the coordinator wires the real date.
- Menu builders return `_menu_lines`, service functions run the interactive
  loop taking `app`.
- Never hardcode absolute paths — derive repo root from
  `Path(__file__).resolve().parent`.
- `cis_archive.archive_service()` scopes the "DECEMBER 1988 ARCHIVE" label
  across a service and its nested pages.

### Test suite conventions

- `test_compuserve.py` — 764 unit tests covering the whole app.
- `smoke_test.py` — dependency-free release/install smoke checks.
- `test_expansion.py` — 16 expansion tests (plus a few skipped) for
  newer features.
- `tests/` — release hygiene tests (wheel contents, privacy, web files).
- **Paul's rule: the full suite must be green before any branch is merged.**
- Known flaky test: `test_concurrent_market_trades_do_not_lose_positions`
  (database-is-locked under parallel runs; passes in isolation; mitigated by a
  per-database-file threading.RLock in `cis_storage.py`).

### Release tooling

`pyproject.toml` lists every runtime module — **update the module list when
adding one**. `build_support.py` ships seed JSON and browser files in wheels;
`MANIFEST.in` carries resources into sdists; `build_release.py` builds the
deterministic release ZIP; `release_payload.py` defines the distributable
asset policy; `smoke_test.py` verifies the archive.

---

## 2. Module reference — core engine & session plumbing

### `compuserve.py` (3,853 lines) — session lifecycle + command router
The heart of the app. Owns dial-in/login, the top menu loop, GO dispatch,
page-pause rendering, baud-rate scrolling, capture, flow control, logout
summary, and simulated billing display. Defines `PAGE_PAUSE_LINES` (24),
`FORUM_CATALOG`, `OPTION_TARGETS`, `PAGE_ADDRESSES`, and `ansi_scroll`.
Every module function it calls receives `sys.modules[__name__]` as `app`.
Key functions: `resolve_go_destination`, `open_go_destination`, `login_screen`,
`forum_service`, `modem_dial_in`, `choose_temporal_destination_setup`,
`sysop_console`, `initialize_database`. **Do not scatter service logic here —
dispatch to a `cis_*` module.**

### `cis_session.py` (129 lines) — session state objects
`SessionState`, `active_session()`, `current_session_state()`,
`session_simulation_date()`; `GoNavigation` for GO stack navigation and
`navigation_prompts()`; `read_input()`. The place session-wide facts live.

### `cis_terminal.py` (50 lines) — terminal text helpers
`wrap_terminal_text`, `header_line`, `menu_lines`. Pure formatting used by
menu screens; no session state.

### `cis_dynamic.py` (1,084 lines) — deterministic world simulation
The simulation clock and living world. `simulation_day()`,
`simulation_datetime()`, `timeline_now()`, event scheduling and processing
(`schedule_event`, `process_events`, mail delivery `_deliver_mail`), daily
content generators: CB topics/lines/presence (`cb_line`, `cb_presence`,
`cb_ambient_events`), forum activity arcs (`ensure_forum_activity`,
`FORUM_ARCS`), market quotes/reports, classifieds, trivia, weather, flight
schedules, reservations, conference schedules, member dashboard, announcements.
`validate_state` / `repair_state` for world hygiene. Called from
`compuserve.py` to keep the world ticking.

### `cis_timecapsule.py` (156 lines) — era selection + date packs
Login-time featured-date menu (`MIN_DATE`/`MAX_DATE`, `FEATURED_DATES`),
`parse_user_date`, `surprise_date`, `pack_for`, `pack_headlines`,
`cb_conversation`. Loads curated per-date packs from
`timecapsule_packs.json`.

### `cis_storage.py` (445 lines) — SQLite persistence layer
The only persistence module everything else funnels through.
`documents`-table doc store (`_read_document`, `_write_document`,
`load_json`, `write_json_atomic`, `update_json_atomic`),
`migrate_json_to_sqlite`, `install_content_pack` (idempotent, pack-id keyed),
backup/restore (`create_backup`, `restore_latest`, `_backup_database`,
`_prune_backups`), `upgrade_database` / `database_status`, session
registration, live-message + CB presence helpers (`post_live_message`,
`set_cb_presence`, …), reference cache. **Read this before any module that
stores state.**

### `cis_security.py` (29 lines) — password hashing
`ALGORITHM`/`ITERATIONS`, `hash_password`, `verify_password`. No session
logic.

### `cis_accounts.py` (59 lines) — account lifecycle
`load_profile`, `set_password`, `authenticate`. Thin auth wrapper over
profiles stored via `cis_storage`.

### `cis_settings.py` (34 lines) — settings presets
`PRESETS`, `DEFAULTS`, `merged_settings`, `apply_preset`. Terminal/service
settings merge.

### `cis_migrations.py` (29 lines) — schema migrations
`CURRENT_SCHEMA_VERSION`, `migrate_data`. Run at startup via
`initialize_database`.

### `cis_archive.py` (17 lines) — archive-label scoping
`archive_service()` — scopes the DECEMBER 1988 ARCHIVE label across a service
and its nested article pages, resetting even on GO-navigation interrupts.
Called by fixed-period services.

---

## 3. Module reference — forums (content modules)

Every forum content module follows the same shape: `FORUM_ID`, `FORUM_TITLE`,
`SECTIONS`, `SEED_POSTS` constants plus `section_spec()` / `seed_posts()`
accessors. The coordinator appends them to the content pack; `install()`
merges seed posts into the database. To add a forum, copy this shape in a new
`cis_<topic>.py` (see §6).

- **`cis_communities.py`** (64 lines) — the content-pack installer itself.
  `PACK`, `FORUMS`, `FILES`, `LIBRARIES` aggregate every forum's seed data;
  `merge_forums`, `merge_files`, `install()` (calls
  `install_content_pack`); `detail_lines`, `download_content`. **Touch this
  when adding a forum module** to include its seeds.
- **`cis_forums.py`** (98 lines) — forum message persistence + authorization:
  `post`, `thread_root_id`, `message_actions`, `set_watch`, `thread_lines`.
  The runtime forum engine; content modules are its data source.
- **`cis_hamnet.py`** (738 lines) — Amateur Radio Forum: expanded section
  spec, 16 Dec-'88 seed posts, 2 scheduled on-air nets (`NETS`,
  `upcoming_net`), ARRL bulletins, broadcast schedule.
- **`cis_guitar.py`** (335 lines) — Guitar & Music Forum (GO GUITAR).
- **`cis_veterans.py`** (330 lines) — Veterans Forum (GO VETERANS).
- **`cis_roots.py`** (453 lines) — Roots & Branches genealogy forum (GO
  ROOTS) + period research tips.
- **`cis_tech.py`** (354 lines) — Tech Talk Forum (GO TECH).
- **`cis_space.py`** (388 lines) — Space & Astronomy Forum (GO SPACE).
- **`cis_cooking.py`** (361 lines) — Cooking Forum.
- **`cis_aviation.py`** (389 lines) — Aviation Forum.
- **`cis_scifi.py`** (357 lines) — Comics & Sci-Fi Forum.
- **`cis_fitness.py`** (398 lines) — Health & Fitness Forum (GO FITNESS).
- **`cis_pets.py`** (391 lines) — Pets & Animals Forum (GO PETS).
- **`cis_trains.py`** (418 lines) — Model Railroading Forum (GO TRAINS);
  treats 1988 command control as *early* command control (pre-NMRA DCC).
- **`cis_photo.py`** (373 lines) — Photography Forum: 5 sections (expands the
  pre-existing `photography_general` section; key preserved for wiring
  compatibility).

Period rules live in each module's docstring — an LLM editing a forum's seed
content must read its docstring's period rules first (era-correct gear, prices,
culture references).

---

## 4. Module reference — news, information & reference services

- **`cis_news.py`** (13 lines) — current-news refresh integration:
  `refresh()`. Thin hook that feed modules feed into.
- **`cis_period_news.py`** (109 lines) — authored Dec-1988-style dispatches:
  `TOPICS`, `archive`, `edition`. Hand-written period wire copy.
- **`cis_entertainment.py`** (320 lines) — GO ENTERTAINMENT: Dec-1988
  Billboard Hot 100 (#1 computed date-aware), in-theater movie reviews, five
  Jan-2-1989 bowl previews (previews only, never results).
- **`cis_books.py`** (420 lines) — GO BOOKS: Dec-1988 bestsellers, magazine
  issues with cover blurbs, staff reviews; plus `seed_files`.
- **`cis_yearend.py`** (343 lines) — GO YEARINREVIEW: 1988 retrospective
  (election, Armenia earthquake, developing Pan Am 103 coverage gated to
  Dec 21+, best-of-1988 roundups).
- **`cis_giftguide.py`** (583 lines) — GO GIFTGUIDE: 1988 holiday shopping
  special (hot gifts, catalog-vs-mall, toy shortages) + interactive gift
  picker by budget/recipient.
- **`cis_christmas.py`** (906 lines) — GO CHRISTMAS: 25-day advent calendar,
  December holiday CB topics, Christmas music (gated on December — off-season
  it says so politely).
- **`cis_sports.py`** (630 lines) — GO SPORTS: late-1988 NFL, 1988-89 TV
  grid, MLB hot stove, Super Bowl XXIII preview (preview only), 1988 World
  Series recap, mid-Dec NBA/NHL standings.
- **`cis_weather.py`** (381 lines) — GO WEATHER: modern weather data rendered
  for the period terminal (geocode + forecast APIs), plus 1988 weather
  retrospectives (Hurricane Gilbert, summer drought/heat wave). Also serves
  the WEATHERWIRE news special.
- **`cis_timeline.py`** (106 lines) — curated offline December 1988
  historical timeline; `records_for_date`, `search`, bookmarks.
- **`cis_features.py`** (73 lines) — curated offline multi-chapter
  historical features; `progress`, bookmarks, `chapter_lines`.
- **`cis_magazine.py`** (457 lines) — original weekly magazine per the
  simulation calendar; `ISSUES`, `available`, `read_article`, new-department
  merge (`_merge_new_departments`).
- **`cis_reference.py`** (392 lines) — period-style reference databases
  (offline) + optional live Wikipedia/OpenAlex lookups; boolean search,
  bookmarks, `export_marked`.

---

## 5. Module reference — games

- **`cis_arcade.py`** (1,586 lines) — GO ARCADE, the Classic Games Arcade:
  six playable 1988-authentic games — Hunt the Wumpus (20-room dodecahedron),
  Hamurabi (10-year reign), Super Star Trek (8×8 galaxy campaign), Blackjack
  (fictional-chip shoe), Eliza (1966 therapist), Lunar Lander. Persistent
  player records (`RECORDS_KEY`, `record_play`, `arcade_records_lines`).
  `play(app)` is the entry; `ARCADE_MENU` lists choices.
- **`cis_crossword.py`** (471 lines) — GO CROSSWORD: daily 7×7 crossword,
  one per weekday (7-puzzle rotation), all clued for 1988. State machine:
  `new_state`, `fill_slot`, `check_answer`, `is_solved`, `render_grid`.
  `play(app)` entry.
- **`cis_nightstation.py`** (725 lines) — NIGHT SHIFT: EARTH STATION text
  adventure: 17 rooms, overnight C-band uplink operator restoring the
  satellite feed before the 6 AM news-wire slot. `NightStationGame`,
  `play(app)` entry.
- **`cis_adventure_league.py`** (175 lines) — persistent Online Adventure
  League: character classes, quests, world events, guilds, journals.
  `service(app)` entry.
- **`cis_eliza.py`** (617 lines) — standalone classic Eliza engine (ranked
  keywords, decomposition/reassembly, pronoun reflection, memory queue);
  shared by the arcade and CB Channel 4 "Eliza's Office". `respond(state,
  text)` is the core API; deterministic round-robin reassembly.

---

## 6. Module reference — communications

- **`cis_cb.py`** (30 lines) — shared CB channel metadata + command parsing:
  `CHANNELS`, `normalize_channel`, `room`, `parse_command`. Pure data/parsing,
  no session.
- **`chat_emulator.py`** (109 lines) — simulated CB chatter engine:
  `ChatEmulator`, `Message`, `generate_expanded_reply`. Produces period
  personalities' ambient lines.
- **`cis_communications.py`** (348 lines) — local reconstructed
  communications services: listings/directory, bulletin board posts, personal
  and public file uploads (`personal_files`, `public_files`, `publish_file`),
  CB society, color e-cards (`send_card`, `cards`). `service(app)` style
  entries taking `app`; poster menus that route here are kept intact.
- **`cis_mail.py`** (180 lines) — EasyPlex mail, isolated from terminal
  navigation: `service`, `compose`, `read`, `folders`, `address_book`,
  `settings`.
- **`cis_drafts.py`** (42 lines) — persistent EasyPlex/forum composition
  drafts: `save_draft`, `get_draft`, `list_drafts`, `delete_draft`.
- **`cis_poster.py`** (310 lines) — photo-backed navigation: renders poster
  menu screens, `open_word` resolves the 27 quick words, `directory` handles
  the `poster_*` targets, `related_targets` route dead-end choices to
  reconstructed services. `install()`, `photo_requests()`.

---

## 7. Module reference — commerce, travel & personal services

- **`cis_store.py`** (177 lines) — Comp-U-Store catalog, cart, fictional
  orders: `catalog_issue`, `stock_status`, `specials`, `add_to_cart`,
  `checkout`.
- **`cis_ownership.py`** (148 lines) — persistent ownership + after-sale
  support for catalog products: `receive_order`, `install`, `warranty`,
  `return_item`, `review`, `sell`.
- **`cis_tradingpost.py`** (347 lines) — GO TRADINGPOST: three-category
  classifieds board seeded with ~15 period ads; members can place ads
  (`place_ad`); 30-day expiry (`is_expired`, `AD_LIFETIME_DAYS`); persisted
  to `tradingpost.json`.
- **`cis_shareware.py`** (133 lines) — seven-day shareware release arc across
  forums and Data Library: `ensure_arc`, milestones, watch/report.
- **`cis_travel.py`** (97 lines) — fictional Dec-1988 travel directory:
  airports/hotels data, itineraries, travelgrams.
- **`cis_disruptions.py`** (155 lines) — deterministic Dec-1988 travel
  weather operations: fictional storms, reservation evaluation.
- **`cis_experience.py`** (173 lines) — cross-service personal tools:
  guided tour, simulation calendar, notebook, download center, achievements,
  session cost, command card export.
- **`cis_hardware.py`** (274 lines) — member's owned computer setup +
  bounded simulated transfer resources: modem/specs, transfer plans,
  `service(app)`.
- **`cis_billing.py`** (62 lines) — connection-time billing simulation:
  prime-time rates, cost estimates, session statements.
- **`cis_phones.py`** (309 lines) — offline pre-login access-number
  directory: historical March-1983 300-baud CNS numbers (period area codes
  preserved) + clearly-marked fictional gap-fillers. `run()` takes injected
  `read`/`ansi_scroll` for standalone use.
- **`cis_business.py`** (299 lines) — period business info + member watch
  lists: simulated stock trading with limit orders, portfolios, forecasts,
  investment club. (`cis_dynamic.market_quotes` feeds its quotes.)
- **`cis_announcements.py`** (88 lines) — scheduled targeted sysop
  announcements: `create`, `active`, `mark_read`, `expire`.
- **`cis_story.py`** (190 lines) — persistent cross-service story cases
  (mystery arcs): clues across mail/news, `decide`, `service`.
- **`cis_discovery.py`** (302 lines) — cross-service discovery + period
  search: `start_suggestions` (GO START's three tailored picks), `whats_new`,
  `search`/`open_result`, activity tracking.
- **`cis_library.py`** (121 lines) — library file-transfer persistence
  helpers: `download_bytes`, `materialize_download`, generated documents.
- **`cis_web_files.py`** (30 lines) — queues immutable copies of explicitly
  requested files for web sessions: `offer_download`.
- **`cis_sysop.py`** (54 lines) — sysop console data ops: account
  rows/lock/reset, upload review queue. Flag target: member-profile
  `is_sysop` (see `make_sysop.py`).

---

## 8. Module reference — entry points, gateways & tooling

- **`web_app.py`** (225 lines) — FastAPI web terminal. `index`,
  `terminal` (WebSocket: spawns `compuserve.py` subprocess per session,
  relays I/O via `relay_output`/`relay_input`), `download_file` +
  `send_downloads`/`relay_downloads` (per-session file delivery with TTL),
  `stop_process`. `MAX_INPUT_LENGTH`, origin allow-list.
- **`telnet_app.py`** (95 lines) — Telnet-style TCP gateway:
  `strip_telnet_commands`, `serve_terminal`, one isolated session per
  connection.
- **`event_worker.py`** (10 lines) — processes due simulated events without
  an interactive session (delegates to `cis_dynamic`).
- **`make_sysop.py`** (42 lines) — CLI grant/revoke sysop:
  `python3 make_sysop.py USER_ID`. Member must exist; sets the
  `is_sysop` member-profile flag. (Plus `make_sysop.sh` convenience wrapper.)
- **`build_release.py`** (69 lines) — deterministic, dependency-free
  release archive builder (fixed timestamps, excludes Git/tests/runtime
  files).
- **`build_support.py`** (49 lines) — ships adjacent resource files in
  wheels/sdists.
- **`release_payload.py`** (20 lines) — explicit distributable asset list +
  clean starter state policy.
- **`smoke_test.py`** (69 lines) — dependency-free release and installation
  smoke checks.
- **`test_communications_store.py`** (120 lines) — unit tests for the
  communications file store.

### Feed scrapers (RSS → JSON content, run by maintainers, not the app)

Each `*_news.py` fetches feeds and writes a repo-root JSON snapshot that the
news services read. They are standalone scripts with `FEEDS` + a
`fetch_*_news` function; `feed_utils.py` holds the shared HTTP/RSS/XML
parsing and atomic JSON writes (`build_news_file`).

- **`feed_utils.py`** (125 lines) — shared fetcher: `fetch_feed`,
  `collect_news`, `write_json_atomic`, `build_news_file`. **Use this for any
  new feed script; never hand-roll HTTP+XML again.**
- **`news_feed.py`** → categorized news; **`merged_feeds.py`** → merged
  news; **`cnn_news.py`** → CNN; **`yahooNews.py`** → Yahoo;
  **`universalNews.py`** → universal feed matrix.
- **`fake2.py`** (68 lines) — synthetic chat-line generator used by the
  chat emulator; `generate_chat_sentence`, `append_random_chat_line`.
---

## 9. How to extend the app (the four common tasks)

### A. Add a new GO destination

1. Write the service logic in a new `cis_<name>.py` (see pattern D/E/F below),
   or reuse an existing module.
2. Register the GO word in **`go_commands.json`**: `"GO WORD": "target_id"`.
3. Handle the target in **`compuserve.py::open_go_destination()`** — add it
   to the `direct_services` dict (service functions) or route it to the
   module (`cis_x.service(sys.modules[__name__])`), following the existing
   branches.
4. If it should appear in a menu, add an option to the right screen in
   **`screens.json`** (`options` + `targets`).
5. If it's a poster quick word, add an entry to **`poster_words.json`**.
6. Update `pyproject.toml`'s module list if you added a `.py` file.

### B. Add a new forum

1. Create `cis_<topic>.py` following the forum content-module shape:
   `FORUM_ID`, `FORUM_TITLE`, `SECTIONS`, `SEED_POSTS`,
   `section_spec()`, `seed_posts()`. Read an existing forum module's
   docstring period rules and keep your seeds era-correct.
2. Wire the section spec into the coordinator's forum catalog (follow how
   `cis_hamnet.py`'s `SECTIONS` are wired into `FORUM_CATALOG`).
3. Add the forum's seed posts/files to **`computer_communities.json`** and
   include them in `cis_communities.py`'s `FORUMS` aggregation.
4. **Bump the pack `id`** in `computer_communities.json` (e.g.
   `...-v5` → `...-v6`) so existing databases merge the new seeds.
5. Add `GO FORUMWORD` in `go_commands.json`; consider a screen entry in
   `screens.json` and a docs page under `docs/`.
6. Run the full test suite before merging (Paul's rule).

### C. Add a new game

1. Create `cis_<game>.py` with a `play(app)` entry point. Keep game state in
   local objects; persist records through the app's record pattern (see
   `cis_arcade.py`'s `RECORDS_KEY` / `record_play`).
2. All output via `app.ansi_scroll(text, 0.01)`; all input via `app.input()`.
   Never bare `print()` or `input()`.
3. Register it in the arcade menu (`cis_arcade.py::ARCADE_MENU`) or as its own
   GO word (`go_commands.json` + `open_go_destination`).

### D. Add new seed content (posts, files, forum sections)

1. Append entries to the relevant place in **`computer_communities.json`**
   (message fields: `content_id`/`section`/`date`/`author`/`subject`/`body`/
   `parent`).
2. **Bump the pack `id`.** Without this, existing databases silently skip
   the merge (idempotency is keyed on the pack id).
3. `install_content_pack` is idempotent on `content_id`, so bumping is safe
   for members who already have older seeds.

### E. Content-module pattern checklist (for an LLM writing a new module)

- Functions that render date-sensitive content take optional
  `day=None` defaulting to `cis_dynamic.simulation_day()`.
- Module docstring documents the **period rules** your content must obey.
- Never hardcode absolute filesystem paths; derive repo root from
  `Path(__file__).resolve().parent`.
- Use `app.ansi_scroll(text, 0.01)` for output, never `print()`.
- Keep to `SCREEN_WIDTH` (80 cols) for output lines.
- Page pauses every `PAGE_PAUSE_LINES` (24) lines are handled by
  `ansi_scroll`; don't implement your own.
- Add tests mirroring the module in `test_compuserve.py`, and run the full
  suite before merging.

---

## 10. Conventions every contributor must follow

| # | Convention | Where |
|---|---|---|
| 1 | Interactive output goes through `app.ansi_scroll(text, 0.01)` — **never bare `print()`** (bare prints bypass baud-rate delay, flow control, capture, and page pauses) | All `cis_*` modules |
| 2 | Full test suite green before any merge (764 unit tests + smoke + 16 expansion tests) | `test_compuserve.py`, `smoke_test.py`, `test_expansion.py` |
| 3 | Page pause every 24 lines via `PAGE_PAUSE_LINES` | `compuserve.py` |
| 4 | Sysop privileges live on the member-profile `is_sysop` flag (granted via `make_sysop.py`) | `cis_sysop.py` |
| 5 | Bump the content-pack `id` in `computer_communities.json` when adding seed posts/files | §9 D |
| 6 | Mutable data lives in the SQLite `documents` table — editing on-disk JSON seeds does nothing at runtime | `cis_storage.py` |
| 7 | Modules accept the app module as runtime context (`app`), passed as `sys.modules[__name__]` | Dispatch in `compuserve.py` |
| 8 | New runtime modules must be added to `pyproject.toml`'s module list | Packaging |
| 9 | Keep era-authenticity: fixed-period content gets the DECEMBER 1988 ARCHIVE label; featured-date packs are separate | `cis_archive.py` |

---

## 11. Key data files (non-Python)

| File | Purpose |
|---|---|
| `screens.json` | Declarative menu screens: options/targets, poster-backed menus, prompts |
| `go_commands.json` | All `GO WORD` → internal target id mappings |
| `poster_words.json` | 27 poster quick-reference words → targets |
| `computer_communities.json` | Master content pack: forums, seed posts, library files (pack `id` = merge key) |
| `timecapsule_packs.json` | Curated per-featured-date content packs |
| `compuserve.db` | SQLite runtime database (`documents` table holds live state) |
| `docs/` | 15 per-service user-guide pages (accounts, forums, games, news, …) |
| `USER_GUIDE.md`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` | Player guide, overview, release notes, workflow |
| `service_data.json`, `store_catalog.json`, `library_files.json`, `magazine_issues.json`, `reference_databases.json`, `historical_timeline.json`, `historical_features.json`, `master_news_hub.json` | Seed/immutable content for services |
| `terminal_config.json`, `profiles.json`, `orders.json`, `feedback.json` | Config / legacy seed state |
| `cb_personalities.json`, `fake_lines.json` | CB chatter content |
| `page_names.json` | Forum/library → page address mapping |
| `startWebUI`, `install-linux.sh`, `start_compuserve.cmd`, `start_web.cmd`, `c.cmd`, `uvrunCompuserve` | Launchers |

---

*End of architecture document. To modify a module, read its section above, then
open that one `.py` file. For repo workflow (branches, releases), see
`CONTRIBUTING.md`.*
