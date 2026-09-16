# Classic CompuServe Simulation

This project is an independent historical simulation of the text-mode
CompuServe Information Service circa 1988. It is not affiliated with or endorsed by
CompuServe, AOL, or their successors. CompuServe names and historical service names
are used descriptively. All charges, orders, reservations, quotations, transfers, and
premium transactions are fictional. The News service intentionally displays current
headlines through a period-style interface.

## Your first call

After sign-in, enter `GO service` or `G service` at any service prompt, including
message readers, forms, the line editor, and CB. For example, `GO MAIL`, `GO NEWS`,
and `GO TOP` leave the current interaction and open the requested destination.
`GO BACK`, `GO RECENT`, page addresses, and unambiguous abbreviations also work.
An unknown destination leaves you at the same prompt. A jump does not submit the
unfinished form; existing EasyPlex and forum draft autosaves retain text already
entered. Password fields read literal passwords. In adventure games, movement
commands such as `GO NORTH` still move within the game.

Choose **User Information**, then **10: Guided Tour and Service Representatives**.
Select stops 1 through 4 to open EasyPlex, the IBM Hardware Forum, its libraries,
and the Activity Center. Each stop explains the commands before opening the service.
Use M through the service menus to return to the tour. Signed-in members retain
VISITED markers between calls; these indicate opened stops, not completed tasks.
Choose A to ask a TRAVEL, FINANCE, or STORE representative a question, or M to exit.

Six original forum discussions unfold with replies after 2, 4, 8, and 24 simulated
hours. Read competing suggestions, the original poster's test result, and a closing
summary. One new discussion opens per simulation date until all six have appeared;
they are not recycled. Existing threads and scheduled replies remain available.
Watch a thread with W from its message actions and use GO NEW on a later call to
look for unread follow-ups. Delivery depends on the simulation clock and event
processing, so a reply need not appear immediately after reading the first post.

## Starting the simulation

On Windows, run `start_compuserve.cmd`. You can also run `compuserve.py` with Python.
The startup screen remembers terminal configuration in `terminal_config.json`.

### Browser terminal

The optional browser interface permits multiple simultaneous sessions. SQLite support is
included with Python, so no separate database server is required. From this directory, create its
private Python environment and install the two web dependencies:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-web.txt
```

After this one-time setup, run `start_web.cmd`, or run `python web_app.py` on Linux.
The server listens on port 8000; open `http://SERVER-IP:8000`. Closing the server
window or pressing Control-C stops it.
The original `start_compuserve.cmd` interface remains available and unchanged.
The browser input supports Up/Down command recall, normal cursor editing, Home, End,
Delete, Control-A/Control-E movement, and Escape to clear. Unsent input is restored after
browsing history. The optional Remember Commands checkbox stores up to 100 non-password
commands in that browser; password prompts are always excluded.

**Save text** downloads a `.txt` file from your current browser session. Highlight
text in the terminal to save only that selection; otherwise it saves the session
transcript, including earlier pages cleared from the screen. Password input remains
masked. No capture command or existing server file is needed. The transcript resets
on Reconnect or page refresh; it retains the most recent five million characters
and labels any truncation in the saved file.

Completed library transfers and requested report exports now start a browser
download. A **Files ready** list below the terminal provides a clickable retry link
if automatic downloads are blocked. Your browser saves to its configured Downloads
folder or asks where to save, depending on its settings. Links belong to the session
that requested each file and last for one hour after disconnect, or until the web
server restarts. The normal server copy remains available too.

`CAPTURE ON` and `CAPTURE OFF` still control server-side recording. In the web
terminal, `CAPTURE OFF` also offers that capture as a browser download. Restart the
web server and refresh the page after installing this update.

On Linux, the included installer can perform a fresh installation or upgrade while
preserving `compuserve.db` and runtime directories:

```bash
chmod +x install-linux.sh
./install-linux.sh
```

To apply a downloaded release to an existing installation, run the installer from
the newly extracted release directory. The installer verifies the release manifest,
shows the current and target versions, validates staged files, and makes a verified
database backup before replacing application files:

```bash
./install-linux.sh --install-dir ~/compuserve --upgrade --systemd-user
```

Add `--telnet` when that service is installed. Upgrades prompt before changing files;
automation can add `--non-interactive`. Updated services and timers are restarted and
checked with systemd. If installation or a health check fails, application files are
restored from the rollback copy under `backups/`. The database and the `captures`,
`downloads`, and `uploads` directories are never replaced.

To install and start a user-level systemd service automatically:

```bash
./install-linux.sh --systemd-user
```

This also enables `compuserve-events.timer`, which processes due events every five
minutes. Check it with `systemctl --user status compuserve-events.timer`.

To also install a Telnet-style terminal listener on port 2323:

```bash
./install-linux.sh --systemd-user --telnet
telnet SERVER-IP 2323
```

The terminal listener enables ANSI/VT100 screen clearing by default. Set
`CIS_TELNET_ANSI=0` to use plain scrolling output. This listener and the web terminal
are intended for a trusted private network; the deferred security milestone should be
completed before exposing either service directly to the Internet.

If Ubuntu reports that the virtual environment has no `pip`, install the complete
Python environment support and rerun the installer:

```bash
sudo apt update
sudo apt install python3-venv python3-pip
rm -rf ~/compuserve/.venv
./install-linux.sh
```

Available presets:

- `C64`: 40 columns, 1200 baud, scrolling display.
- `IBM`: 80 columns, 1200 baud, scrolling display.
- `MAC`: 80 columns, 2400 baud, screen display.

The detailed configuration also controls modem dialing, connection quality, sound,
16-line pauses, automatic News updates, and fast output mode. Fast mode removes the
simulated character delay while preserving the historical screen layout.

Daily service content varies deterministically while remaining within December 1988.
Main-page bulletins, classified advertisements, market figures, CB activity, trivia,
and simulated forum traffic remain stable for the simulated day. Set
`CIS_SIMULATION_DATE=1988-12-15` to select a specific day for demonstrations or tests.
Set `CIS_SIMULATION_TIME=21:30` to select a time of day. A persistent event queue
delivers welcome and order mail, advances fictional orders, and creates follow-up forum
replies when the user next logs in. Trivia scores, classified lifetimes, and processed
events are retained in SQLite. CB participants respond to period-appropriate keywords
such as MODEM, DOS, MEMORY, GAME, and WEATHER.

The displayed calendar remains in December 1988, but delayed events use a hidden
monotonic minute counter. Events therefore remain due in the correct order when the
visible date wraps from December 31 to December 1. Login-time event processing remains
available as a fallback when the Linux timer is not installed.

User Information includes a fictional usage statement assembled from completed
sessions. It lists connection time, baud rate, estimated connect charges, premium
charges, and totals, and can be downloaded as an ASCII file. The current session is
shown as a preview until logout records its final duration. Duplicate logout processing
does not duplicate a session.

Enter `GO PROFILE` for a personal service summary covering EasyPlex, forum activity,
trivia, library use, and fictional order status. Forum conferences have daily topics,
persistent simulated member identities, and transcripts posted back to the forum.
The IBMHW library receives a rotating harmless text reference and displays its most
accessed files. Travel includes variable 1988 airline schedules and December simulation
weather. SysOps can select option 7 to inspect the event queue and simulated members.
Travel also offers a Live Weather Wire powered by Open-Meteo. It shows modern current
conditions and a three-day forecast, clearly separated from the fictional 1988 weather.
Reports are cached for 30 minutes and stale cached data is used during provider outages.

The Weather Operations Center models three fictional December 1988 systems: Great
Lakes snow, a Northeast coastal storm, and a central ice advisory. Air reservations
whose dates and routes intersect a system are placed into an action-required state and
receive an EasyPlex alert. The affected trip also appears in the Trip Folder, Calendar,
Profile, and Weather Operations display.

Members may accept the first controlled alternate flight, request protective Amtrak
routing, join an airport-hotel waitlist, retain the original trip on standby, or cancel
under a fictional weather waiver. The choice and resulting itinerary status persist;
older scheduled ticketing updates will not overwrite a weather resolution. All storm
effects, availability, accommodations, schedules, and alternatives are simulation data.

Enter `GO NEW` for a consolidated activity center. The global `FIND words` command
searches forum messages, library descriptions, active classifieds, and curated reference
entries. Forum replies retain their parent message number and members can watch a thread
for EasyPlex notifications. Generated library references are readable ASCII documents.
Members can post 21-day classifieds, send seller inquiries, and mark their own listings
sold. Fictional airline selections can be recorded as reservations and are listed under
`GO PROFILE`. SysOps may cancel pending events or archive processed events from the
dynamic event monitor.

Selected period-appropriate technical questions posted in Forum sections may be noticed
by recurring simulated members. Their reply arrives later in the same discussion, with
an EasyPlex notice and, where useful, a numbered Data Library file reference. The same
handle may remember the exchange in CB. `GO PROFILE` lists these Forum correspondents;
this is an authored historical simulation, not a connection to modern messaging or an
automated advice service.

Recurring simulated members now maintain a persistent relationship with each signed-in
member. Forum replies, CB follow-ups, service-representative questions, and selected
Special Desk outcomes contribute to the same history. Relationship levels progress from
unfamiliar through acquainted, regular, trusted, and confidant. Repeatedly hostile
exchanges can instead produce a rival relationship.

Enter `GO PEOPLE`, `GO RELATIONSHIPS`, or `GO CONTACTS` to view correspondents, trust,
friction, exchange counts, remembered topics, and open favors. Trusted contacts use
more familiar CB greetings, rivals acknowledge prior disagreements, and major
relationship milestones generate personal EasyPlex follow-ups. Existing correspondence
from earlier releases is converted automatically from its saved interaction count.

Release 1.4 uses numbered transactional schema upgrades. Before changing an older
database, startup writes a `PRE-UPGRADE-...db` safety copy under `backups`. Diagnostics
reports SQLite integrity, schema version, database size, and dynamic-record problems.
The SysOp event screen accepts `SET DATE 12/20/88`, `SET TIME 21:30`, `ADVANCE 1 DAY`,
and `PROCESS EVENTS`. Search results may be selected to open a forum message or begin a
library transfer. The browser terminal supports up/down command history, TOP/MENU/OFF
buttons, and saving text from the current browser session.

Release 1.5 adds tree views for forum discussions (`T number`), watch removal
(`U number`), EasyPlex custom folders and an address book, categorized member
classifieds, and cancellation of eligible fictional orders and reservations through
`GO PROFILE`. Simulated members retain simple topic memories across CB and forum
interactions. The daily library rotation includes RS-232, CONFIG.SYS, AUTOEXEC.BAT,
VGA, and expanded-memory references. SysOp option 8 posts top-page announcements or
adds notes to simulated-member profiles.

### Time capsule

Connection setup includes a Temporal Destination step: experience CompuServe as of
the date you choose. Pick **Present Day** (the service's current date), choose from
fourteen featured dates, enter any date from 1979 through 1998 as `MM/DD/YYYY`, or
let **Surprise me** choose a session-scoped deterministic date that stays fixed for that
call. Featured dates include Columbia's first flight (1981), the IBM PC
announcement (1981), the Macintosh debut (1984), Live Aid (1985), Challenger and
Chernobyl (1986), the Black Monday crash and the INF Treaty signing (1987),
Exxon Valdez, the Loma Prieta earthquake, and the Berlin Wall's fall (1989), the
Hubble launch (1990), and Desert Storm and the first website (1991).

Featured dates carry curated archival content packs: period headlines, sysop
announcements, CB conversation topics, and market notes written for that moment.
Your account remembers the last era you visited; when you choose Present Day after
login, the service offers to return to that date. Ambient CB conversation and
simulated forum traffic also adapt to the session's date, while the shared daily
forum story arcs remain December 1988 regardless of era.

Release 1.6 adds simultaneous browser sessions, shared live CB channels and forum
conferences, SQLite online-session and live-message tables, a SysOp online-member
display, and an optional ANSI Telnet-style listener on port 2323.

## Online Weekly magazine

Use `GO MAGAZINE` (or `GO WEEKLY`, page `MAG-1`), or choose **7 Online Weekly
Magazine** from News Services. Five original fictional issues are dated December
1, 8, 15, 22, and 29, 1988. Only issues published by the simulation date are shown;
on December 15 the latest issue is *Small Programs, Real Evenings*. Earlier issues
remain available as back issues. This is authored simulation content, not an
archived CompuServe publication or a live news subscription.

Each issue has thirteen articles (65 total), each at least 400 words. All 25 original
articles have more than doubled in length. Departments include editorials, hardware comparisons,
workshops, game reviews, reader letters, and club projects, plus three departments that
appear in every issue: News Briefs (short December 1988 items), SysOp Q&A (member
questions answered by the sysop), and Letters to the Editor (member letters about
computing life). The issue list shows
how many articles you have read. Choose an issue number or ID, `L` for the latest
issue, or `S words` to search published articles. Global `FIND words` also indexes
the magazine, and `GO NEW` highlights the latest issue.

Inside an issue, choose an article number or `R` to resume the last article you
opened. `N` and `P` move between articles; `M` returns to the contents, then the
issue list. Reading progress is saved with your profile. `D` downloads the entire
issue, including its contents and every article, as a 72-column plain-text file.
Browser sessions receive the normal automatic download and retry link.

## Computer forums and downloads

The Forums Directory includes Commodore/Amiga, Apple II, Atari ST, and DOS
Software as choices 7 through 10. Use `GO COMMODORE` (also `GO C64` or `GO AMIGA`),
`GO APPLEII`, `GO ATARIST`, or `GO DOS` to open them directly.

Each community has three discussion sections, threaded conversations, its own
conference topic, and four real downloadable files. These 36 posts, file reviews,
and 16 files are original fictional simulation content, not recovered historical
forum messages or commercial software. You can reply, watch threads, and join
these forums using the existing forum commands.

Select **2 Libraries** inside a forum, or use `GO C64LIB`, `GO APPLELIB`, `GO STLIB`,
or `GO DOSLIB`. Enter `I number` to read a file's usage notes, version history,
and simulated member review. Enter the file number, then `B` or `X`, to save the
actual file in the application's `downloads` folder. `FIND DOCK64`, for example,
finds the related discussions and library entry.

| Forum | Files |
| --- | --- |
| Commodore/Amiga | `DOCK64.BAS` docking game, `C64NOTES.TXT` type-in guide, `AMIGALOG.TXT` test worksheet, `PIXELCAT.TXT` ASCII postcard |
| Apple II | `ORCHARD.BAS` arithmetic practice, `APPLETIP.TXT` exercises, `DISKLOG.TXT` catalog forms, `APPLEART.TXT` welcome card |
| Atari ST | `TEMPO.BAS` duration calculator, `STDESK.TXT` publishing checklist, `MIDIPLAN.TXT` rehearsal worksheet, `STCLUB.TXT` newsletter |
| DOS Software | `CALLCOST.BAS` fictional charge estimator, `LOSTDISK.BAS` text adventure, `DOSNOTES.TXT` setup notes, `CLUBLIST.TXT` sample roster |

BASIC files are readable ASCII source listings. They are not tokenized C64/Apple
files or disk images. Type or paste the numbered lines into the indicated BASIC
interpreter; GW-BASIC can load its ASCII listings directly. All five programs'
shared BASIC logic was checked in PC-BASIC, including expected results and invalid
inputs. Original-machine imports have not been emulated. The calculators and games
do not alter your simulator account or access disks.

The content installs once at application startup. Installation adds records while
preserving member posts, uploads, and download counts; subsequent starts do not
duplicate the content or restore seeded posts a SysOp has deleted.

## Community forums

Beyond the computer forums, the directory offers nine interest forums. The
**Amateur Radio Forum** (`GO HAMNET`, choice 5) covers packet radio, HF/VHF rigs,
antennas and towers, DX and contesting, license study, ARRL bulletins, and swap
and shop, with December 1988 seed posts and two scheduled on-air nets. The
**Veterans Forum** (`GO VETERANS`, choice 11) hosts service stories, reunions and a
buddy finder, VA benefits discussion, and a Wall remembrance section. **Roots &
Branches** (`GO ROOTS`, choice 12) is a genealogy forum covering getting started,
NARA and archives, census records, family history centers, a surname registry,
and military records. The **Guitar & Music Forum** (`GO GUITAR`, choice 13) covers
electrics, acoustics, amps and effects, a tablature exchange, MIDI and home
recording, and what's spinning; gear and music discussion stay era-appropriate to
December 1988. **Tech Talk** (`GO TECH`, choice 14) debates IBM PC and clones,
Macintosh, Amiga vs Atari ST, OS/2 and operating systems, modems and telecom,
and CD-ROM and new tech. The **Space & Astronomy Forum** (`GO SPACE`, choice 15)
covers shuttle and spaceflight, deep-sky observing, planets and probes, amateur
telescopes, NASA and space news, and star parties, with December 1988 seed posts.
The **Cooking Forum** (`GO COOKING`, choice 16) swaps recipes, holiday baking
ideas, cast-iron and cookware talk, microwave cooking, canning and preserving,
and restaurant recommendations. The **Aviation Forum** (`GO AVIATION`, choice 17)
covers private flying, IFR training, aircraft ownership, flight simulators, trip
reports, and hangar talk. The **Comics & Sci-Fi Forum** (`GO SCIFI`, choice 18)
discusses comic books, Star Trek, Doctor Who, movies and TV, science-fiction
books, and conventions, all era-appropriate to December 1988.
All nine use the standard forum commands for reading,
posting, replying, and watching threads. These forums are original fictional
simulation content, not recovered historical messages.

## Accounts and login

Enter `CIS` at the Host Name prompt (or press Enter) to log in. Enter `PHONES`
to browse the access-number directory without an account. Search by full or partial
city name, optionally including the state/province abbreviation (for example,
`Portland, OR`). `ALL` lists cities in pages; Enter advances, `S` starts another
search, and `M` returns to Host Name. At the city prompt, blank input also returns.
Search ignores case, accents and punctuation; `NYC`, `LA`, `SF`, and `DC` work too.

The directory covers major U.S. cities, all 50 states, DC, and Canadian centers.
Every number is marked `HISTORICAL` or `FICTIONAL`. Historical entries come from
CompuServe's [March 1, 1983 access-number sheet, page 1](https://www.pagetable.com/docs/cbm1600modem/compuserve2.pdf)
and retain its original area codes (CNS, 300 baud); they are not a verified 1988
or current directory. Supplemental cities use fictional `555-01xx` numbers.
`SOURCES` displays the reference inside PHONES. This directory only displays
numbers; it does not dial them or change the session's baud setting.

User IDs use the form `70000,0001`. Existing
legacy accounts establish a local password on their next login. Unknown IDs can create
a new local account. Passwords are stored as salted PBKDF2 hashes, never as plain text.
Three failed attempts lock the account until a local SysOp unlocks it.

User ID `77777,0001` is designated as the initial local SysOp account. Its password is
established on first login.

## Global commands

- `T` — Top menu.
- `M` — Previous menu.
- `G name` or `GO name` — Go directly to a service.
- `GO BACK` — Return to the previous menu in the navigation path.
- `GO RECENT` — Select from the last 10 destinations visited this session.
- `G CIS-1` — Go to a page address.
- `H` — Help.
- `R` — Resend the current page.
- `F` / `B` — Forward or back.
- `N` / `P` — Next or previous menu item.
- `S n` — Scroll beginning with menu item `n`.
- `CAPTURE ON` / `CAPTURE OFF` — Save terminal output under `captures`.
- `BACKUP` — Create a rotating backup archive.
- `RESTORE` — Restore the latest archive; restart afterward.
- `VERSION` — Show the simulation and data-format versions.
- `STATUS` — Show terminal, connection, account, and session status.
- `DIAG` — Check the local data files and terminal configuration.
- `?` — Display help for the current service.
- `HELP topic` — Search help, such as `HELP TRADING` or `HELP TRAVEL`.
- `COMMANDS` — Display actions available in the current service.
- `NOTE title | text` — Save a persistent note from the current service.
- `GO CALENDAR`, `GO NOTEBOOK`, `GO DOWNLOADS`, or `GO ACHIEVEMENTS` — Open personal tools directly. Unambiguous GO abbreviations of at least three letters are accepted.
- `GO NEW` — Open a selectable activity center for unread mail, forum posts, orders, travel, and scheduled events. Use `MARK ALL READ` to clear the current list.
- `OFF` or `BYE` — Log off.

On a Windows terminal, Control-S pauses output, Control-Q resumes it, and Control-C
interrupts the current transmission.

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

## Forums and Data Libraries

CB channels share persistent scrollback and live presence between simultaneous console,
web, and Telnet sessions. Inside a channel, use `/WHO`, `/CHANNELS`, `/JOIN name`,
`/MSG handle text`, `/IGNORE handle`, `/STATUS AVAILABLE|AWAY|BUSY`, and `/EXIT`.
Joining an unknown name creates a member channel. Arrival and departure notices are
retained with the latest 20 messages; the existing Private Messages screen receives
messages sent with `/MSG`. Sound-enabled sessions announce new live messages.
CB also includes 34 clearly simulated period members, with 7–12 present in each
channel. They remember prior topics, recognize directly addressed handles, and tailor
technical replies and follow-up questions to the subject and computer mentioned.
They also hold occasional channel-specific conversations, move between rooms, and
observe quieter overnight hours. Ambient and direct replies are retained in shared
scrollback without duplicate generation by simultaneous server sessions. Use
`/INFO handle` to see a simulated member's computer, interests, home forum, and the
most recent topic you discussed together.

Forums contain Messages, Libraries, Conferencing, Announcements, a member directory,
options, instructions, and membership. Message commands include SELECT, READ, CHANGE,
and COMPOSE. Searches accept a message number, `FROM name`, or `SUBJECT words`.

IBMHW libraries support CompuServe B and XMODEM-style transfers. Downloads are written
under `downloads`. Uploads are copied under `uploads` and remain pending until approved
through the local SysOp console.

## News

News option 6 refreshes current BBC RSS headlines. Previous News data is preserved when
the refresh fails. Stories retain source attribution and update timestamps while using
a numbered, paged wire-service presentation.

News option 5 also offers a separately labeled December 1988 period edition drawn from
64 authored World, Business, Technology, and Science dispatches. Each member receives
12 selections per edition; recently presented dispatches are retained in that member's
history so five consecutive editions contain no repeated items. Option 6 updates the
clearly separate current-news wire.

**Sports & TV** (News option 8, `GO SPORTS`) presents 1988 NFL standings and
December scores, the 1988-89 prime-time TV grid, and MLB hot-stove news, plus a
Super Bowl XXIII preview (clearly marked preview-only; the game is played
January 22, 1989), a 1988 World Series recap, and mid-December 1988 NBA and NHL
standings. **Entertainment**
(News option 9, `GO ENTERTAINMENT`) carries the December 1988 Billboard Hot 100 with
a date-aware number one ("Look Away" by Chicago early in the month, "Every Rose Has
Its Thorn" by Poison at Christmas), reviews of films in theaters that month, and
previews (never results) of the January 2, 1989 college bowl games. The **Weather
Wire** (News option 10) publishes December 1988 city forecasts and ski-resort
conditions with three date-aware variants; `GO WEATHER` continues to open the live
Open-Meteo weather service described in Travel. **Books & Magazines** (News option
11, `GO BOOKS`) lists December 1988 hardcover bestseller lists, December magazine
issues with cover-story blurbs, staff reviews of 1988 books, and back-issue files
readable from the Data Library. **1988 Year in Review** (News option 12,
`GO YEARINREVIEW`) is a news special recapping the year: Election '88 results,
the year's top news stories, the Armenia earthquake wire, science and
technology highlights, and a best-of roundup spanning movies, music, sports,
and technology. Date gating applies: the Armenia earthquake coverage appears
from December 7 onward and the Pan Am Flight 103 developing story appears from
December 21 onward, following the session's simulated date. All News content stays dated no later than December
1988; these are authored simulation contents, not archived period publications.

CB recognizes a broad set of period topics including modems, DOS memory, disks, display
adapters, Macintosh development, packet radio, games, software, printers, weather,
classifieds, and news. Recurring handles retain the last subject and can ask a related
follow-up question during the exchange.

## Business & Financial

MicroQuote contains twelve delayed fictional December 1988 securities. Enter a ticker,
`LIST` for the symbol directory, `WATCH symbol` to retain a company, `MY` to display the
member watch list, `REMOVE symbol` to remove one, or `M` to return. A fictional market
simulation begins with $10,000 cash. Use `BUY` and `SELL` for whole-share trades, `PORT`
for cash, positions, average cost, market value, realized and unrealized profit/loss, and
total return, or `HISTORY` for the persistent transaction ledger. Each trade includes a
simulated period-style commission and requires confirmation. `LIMIT` files a persistent
buy or sell limit order and `ORDERS` reviews its status; eligible orders execute on a
later MicroQuote visit and generate an EasyPlex notice. Fictional INTC dividends and an
AAPL two-for-one split are applied once as the December timeline advances. Market Reports show
a simulated DJIA, volume, and market commentary. Standard & Poor's accepts a symbol,
company name, industry, or `LIST` and provides company, office, industry, business, and
sector information plus related period-wire context. Portfolio Center can download an
ASCII packet containing positions, watch-list quotes, and economic indicators. The
indicators screen includes illustrative interest rates, inflation, employment, and
production figures. Prices remain stable during a simulated day and may change when the
simulation advances. All money and securities are fictional historical-simulation data,
not investment advice, brokerage activity, or real trading.

Investment Club Market Watch follows a dated seven-day semiconductor story. Members may
file one INTC or MOT direction forecast, receive a December 23 scorecard and club rank,
and compare the result with their Market Challenge account. A completed CHIP-88 decision
adds a small member-specific sentiment effect to fictional semiconductor quotes.

## Travel Services

The Official Airline Guide recognizes twelve major U.S. airport codes and provides
fictional December 1988 schedules, availability, coach or first-class fares, travel dates,
and reservations for up to six passengers. Invalid codes open the airport directory.
The expanded hotel directory covers six cities with nightly rates, locations, amenities,
and fictional multi-night lodging requests. Air and hotel confirmations arrive through
EasyPlex and appear under `GO PROFILE`. Travelgrams combine destination advisories with
the simulated weather report. My Trip Folder combines reservations and statuses, stores
seat, car, and hotel preferences, and downloads an ASCII itinerary. Reservations advance
to TICKETED or GUARANTEED on the simulation timeline. Rail and Rental Cars provides
period-style ground-transport guidance. Companies, airports, and hotels are searchable
with global `FIND`. Always verify real schedules, fares, and availability.

## Comp-U-Store

Comp-U-Store contains a fictional 36-item 1988 mail-order catalog covering modems,
cables, media, printers, software, books, accessories, and upgrades. Choose `GO SHOP`,
then Comp-U-Store. Enter an item number for its description, availability, compatibility,
and a simulated owner's report when available. Use `C` to choose a category, `S` to
search, `D` for rotating December specials, `K` for IBM PC/XT, IBM PC AT, Macintosh
Plus, Commodore 64, or TRS-80 Model I/III compatibility guidance,
`A` to add an item and quantity, `V` to review the order, `R` to remove an item, and `O`
to send the order. `F` and `B` page through the catalog.

The cart is retained between calls. Sending it creates one consolidated fictional order
with itemized prices and period-style shipping charges, sends an EasyPlex receipt, and
advances through RECEIVED, PROCESSING, and SHIPPED over simulated days. Limited stock
and back orders vary by simulated date, and each status change produces an EasyPlex
notice. Order status is
shown under `GO PROFILE`; store products are also searchable with the global `FIND`
command. No real goods, payment, or shipment are involved.

Orders now continue from SHIPPED to DELIVERED. Each delivered quantity becomes an
individually identified item under Shopping's Owned Equipment and Support service,
`GO EQUIPMENT`, `GO OWNED`, and the member Profile. Members can install an item against
the catalog compatibility index and associate it with an IBM PC, Macintosh Plus,
Commodore 64, or TRS-80 system.

Owned items support fictional warranty cases, return authorizations, owner reports,
and resale through Electronic Classifieds. Warranty reports generate an EasyPlex
response from Helen/Orders, add general installation guidance to the IBM Hardware
Forum, and contribute to the member relationship with the representative. Equipment
ownership also unlocks a member achievement. These workflows never move real goods or
money and should not be treated as actual product support.

The **Trading Post** (`GO TRADINGPOST`) is a member classifieds board separate from
Comp-U-Store: FOR SALE, WANTED, and TRADE categories seeded with December 1988 ads
for modems, 8-bit micros, dot-matrix printers, floppies, LPs, concert tickets, and
computer books, all priced in 1988 dollars. Members can place their own ads; ads
persist and expire 30 days after the simulated date they were placed. All listings
are fictional simulation content, and no real goods change hands.

## Games

Adventure: The Silent Mainframe is a multi-room puzzle with an essential restoration
and optional diagnostic and cooling objectives. Use `LOOK`, compass directions,
`TAKE item`, `INVENTORY`, `EXAMINE item`, `USE item`, `MAP`, and `SCORE`; enter `QUIT`
to leave. Wins, best move counts, and full restorations are retained by member.

MegaWars stores a separate ship career for each member. Star Command missions award
credits and experience, which advances the member from Cadet through Commodore.
Combat distinguishes energy, shields, and hull integrity and supports phasers and a
limited missile magazine. Starbases offer trading, repair, shield charging, docking,
and missile purchases. `MAP` shows the nine-sector jump ring; `STATUS` reports the
complete ship. Enter `SAVE` to hold position and return to the Games menu.

Trivia Tournament presents deterministic five-question rounds drawn from a larger
period-computing question bank. Lifetime accuracy, completed rounds, best round,
answer streak, and tournament points persist for each member. Player Records on the
Games menu summarizes progress across all three games.

Online Adventure League adds a separate save-compatible campaign character. Choose a
Scout, Engineer, or Courier, then complete one deterministic quest per simulated day
using class abilities such as `SEARCH`, `REPAIR`, or `BARGAIN`. Experience unlocks
levels and three campaign chapters; relics, health, gold, inventory, and daily progress
persist. Members can join a guild, invite recurring handles to a party through EasyPlex,
and post adventure journals to the Gamers Forum. Rotating world events alter encounters,
and a SysOp can replace the current event with `ADVENTURE text`. Player Records also
shows League character, level, and guild information.

**NIGHT SHIFT: EARTH STATION** (Games option 7) is a second standalone text
adventure, distinct from The Silent Mainframe. You are the overnight operator at a
remote C-band earth station: a thunderstorm has knocked out the satellite uplink,
and the 6 AM news-wire feed must be on the air before the slot passes. Explore
17 rooms, restore power, realign the dish, load the feed cartridge, and transmit.
Verbs include TAKE, USE, EXAMINE, START, FILL, INSTALL, LOAD, TRANSMIT, and CLIMB,
plus SCORE and TIME; you have 81 five-minute moves from 23:15 to 06:00. High scores
persist per member.

The **Daily Crossword** (Games option 8, `GO CROSSWORD`) serves a fresh 1988-themed
7x7 puzzle every day, one per weekday: movies, music, tech, sports, TV, news, and
variety. Rows 1, 4, and 7 are seven-letter across answers; each column holds two
three-letter down answers crossing exactly one across word. Use `A<num>` to answer
an across clue, `D<num>` for a down clue, and `GRID` to redisplay the board.
Progress persists per member until the puzzle is solved.

The **Classic Games Arcade** (Games option 9, `GO ARCADE`) hosts four
era-appropriate favorites: Hunt the Wumpus, Hamurabi, Super Star Trek, and
Blackjack. Blackjack is played with fictional arcade chips worth nothing but
pride. Each game records one entry per member session in Player Records
(Games option 5).

## Special Desk investigations

Beginning December 12, the Special Desk may send a member an EasyPlex research request.
The CHIP-88 case follows a disputed memory-chip shipment through a real IBM Hardware
Forum thread, the Period Business News wire, the Finance market report, and a Special
Desk index in Reference. Enter `GO CASE` or `GO INVESTIGATE` to review the evidence
ledger. Reading the relevant material inside each service checks off that source.

After collecting evidence from at least three services, the member may report the lot
privately, publish a qualified warning, or hold the evidence for confirmation. The
decision, consequence, activity history, and closing EasyPlex report persist. All
companies, shipments, quotations, and outcomes in this scenario are fictional.

## TERMLINK shareware project

From December 10 through 16, the IBM Hardware Forum and Data Library follow a fictional
shareware launch. ByteBender announces the TERMLINK terminal utility, releases version
1.0, gathers COM2/IRQ3 conflict reports, requests tester configurations, submits a 1.1
patch, and receives SysOp approval before thanking contributors.

Enter `GO SHAREWARE` or `GO TERMLINK` to review the seven-day project record. Members
can watch the project for EasyPlex updates, file DOS/port/IRQ/modem configuration
reports, and transfer the newest approved release. Testers earn contributor reputation
when the final milestone is published, and their work contributes to the persistent
ByteBender relationship.

TERM10.TXT and TERM11.TXT are harmless simulated text documentation rather than
executable programs. Version 1.0 becomes withdrawn when 1.1 is approved, with explicit
replacement metadata retained in the library record.

## Reference Data Bases

The four classic Reference choices contain 200 records total, with 50 records apiece in Academic
American Encyclopedia, Medical Information, Science and Technology Index, and Electronic Library. Enter words
to search, `B` to browse the complete index, `H` for help, or `M` to return. Search
results display stable record identifiers and may be selected for the full entry. Result
lists show 12 records per page; use `F` and `B` to move between pages. A record ID such
as `L4003` may be entered directly. Boolean expressions support `AND`, `OR`, and `NOT`,
and displayed records include `SEE ALSO` cross-references derived from their descriptors.
Medical records are general historical-simulation information and are not a diagnosis.
Reference records are also included in the global `FIND words` command.

Reference content is stored separately in `reference_databases.json`. Startup validates
the four database names, record structure, unique identifiers, 50 records per database,
and the 200-record total before accepting the catalog.

Member research commands include `HISTORY`, `RECALL n`, `CLEAR HISTORY`, `MARK id`,
`MARKED`, and `DOWNLOAD`. The download command writes an ASCII marked-record packet in
the member download directory. `SUBJECTS` lists database-specific subject indexes and
`SUBJECT name` browses one. Relevant Reference record IDs may also appear as background
suggestions after a Forum post or beneath a News dispatch.

A fifth choice, Live General Reference, searches Wikipedia over the Internet and presents
up to 10 results in the same terminal style. Live records use `W` identifiers and are
clearly labeled as modern content outside the December 1988 simulation. The search waits
up to five seconds; if the provider or network is unavailable, the classic offline
databases remain usable. Results are cached in SQLite for 24 hours, and an older cached
copy is used when the provider is temporarily unavailable. `MARK n`, `MARKED`, and
`DOWNLOAD` preserve live records and include them in the same research packet as classic
records. No additional Python package or API key is required.

Live Academic Reference searches OpenAlex scholarly works and displays authors, source,
publication year, DOI, citations, open-access status, and available abstracts. Enter
`BEFORE 1989 words` to restrict results to literature published before 1989. Academic
results use `OA` record identifiers and share the live cache, marking, and download
features. Casual searches work without a key; setting `OPENALEX_API_KEY` raises the
OpenAlex usage allowance.

## Personal organization and continuity

User Information includes a unified Personal Calendar for pending EasyPlex replies,
store fulfillment, travel status, Forum follow-ups, trips, and classified expirations.
The Personal Notebook stores persistent notes; from any menu, `NOTE title | text` saves
an item with its source service. `GO CALENDAR`, `GO NOTEBOOK`, `GO DOWNLOADS`, and
`GO ACHIEVEMENTS` provide direct access. The Download Center lists and reads generated
ASCII files and can rename or delete a selected file after confirmation.

Achievements summarize exploration, correspondence, research, fictional trading, travel,
shopping, and games. Session Economics compares baud rate, elapsed time, connect and
premium charges, and the benefit of downloading a report for offline reading. New members
receive an expanded welcome message and can select the guided tour. Travel, Finance, and
Store representatives accept questions there and send delayed EasyPlex replies while
remembering the exchange.

Business quotations observe simulated weekends and include modest sector effects tied to
the period business wire. The optional December Market Challenge tracks the portfolio
against a preserve-capital goal. Travel schedules may show delays or cancellations, and
the Combined Trip Planner compares outbound, return, and lodging choices before separate
fictional booking.
Delayed itineraries generate status notices and may be replaced from the Trip Folder's
rebooking display. Traveler profiles also retain a home airport, preferred airline, and
fictional frequent-traveler number.

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
