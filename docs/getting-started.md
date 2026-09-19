# Getting started

## Your first call

After sign-in, enter `GO service` or `G service` at any service prompt, including
message readers, forms, the line editor, and CB. For example, `GO MAIL`, `GO NEWS`,
and `GO TOP` leave the current interaction and open the requested destination.
`GO BACK`, `GO RECENT`, page addresses, and unambiguous abbreviations also work.
An unknown destination leaves you at the same prompt. A jump does not submit the
unfinished form; existing EasyPlex and forum draft autosaves retain text already
entered. Password fields read literal passwords. In adventure games, movement
commands such as `GO NORTH` still move within the game.

The TOP menu follows the photographed twelve-category CompuServe map. Choose
**1 Instructions/User Information**, **1 Tour/Find a Topic**, then **1 Tour**.
`GO HELP` opens the instructions menu directly. `GO INDEX` offers topic search
and an alphabetical directory; `GO QUICK` opens the searchable GO-word directory.
In directories, use `S words`, `F`/`B`, `ALL`, a displayed number, or `M`.
Historical entries identify related simulations and services not yet recreated.
Every numbered poster menu choice now opens either its transcribed destination
or a related reconstructed simulation, announced before opening; only a few
photographed quick words (e.g. ASHTON) intentionally keep the unimplemented
notice.
`GO SUPPORT` retains the older support menu and its extra simulation features.
See [Poster reference](../POSTER_REFERENCE.md) for source coverage and limitations.

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

Release 1.6 adds simultaneous browser sessions, shared live CB channels and forum
conferences, SQLite online-session and live-message tables, a SysOp online-member
display, and an optional ANSI Telnet-style listener on port 2323.

---

[Back to the user guide](../USER_GUIDE.md)
