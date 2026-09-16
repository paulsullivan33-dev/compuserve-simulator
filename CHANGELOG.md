# Changelog

## 1.17.0 - 2026-09-16

- Marked fixed period services as the December 1988 archive, separate from
  selected-date headlines and live feeds. Year-end election results and the
  full-year roundup now respect publication dates; briefings omit future history.
- Added GO START with three date-aware destinations and direct GO shortcuts
  for the new news specials, arcade, crossword, and Trading Post.
- Fixed Windows path and line-ending assumptions in regression tests.
- Included all runtime modules, seed JSON, and browser assets in Python wheels;
  added a clean installed-package check and Windows/Linux CI.
- Removed superseded patch/bundle handoff files and updated release guidance.


- Added ELIZA, a faithful 1966-style computer therapist engine (`cis_eliza`),
  in two places: as arcade game 5 (`GO ARCADE`) and as CB Channel 4,
  "Eliza's Office" (CB option 7). In both, she answers in classic Rogerian
  style, reflects the user's words back, remembers context across turns for
  each member, and a goodbye ends the session and clears its state. The engine
  is deterministic (round-robin replies, no randomness), and CB degrades to a
  polite "away" message if the engine module is ever absent.

- Added Lunar Lander to the Classic Games Arcade (game 6, `GO ARCADE`): the
  1970s BASIC classic — choose a fuel burn each turn, mind gravity, land soft;
  safe landings are graded and recorded in Player Records. The arcade menu and
  Player Records now cover all six games.

- Added the Pets & Animals Forum (`GO PETS`, forum choice 20) with six sections
  (dogs, cats, birds, fish & aquariums, small pets, ask the vet) and 16
  December 1988 seed posts.

- Added the Model Railroading Forum (`GO TRAINS`, forum choice 21) with six
  sections (layout design, DCC & wiring, locomotives, scenery, prototype
  research, buy/sell/trade) and 16 December 1988 seed posts.

- Expanded the Photography Forum (`GO PHOTO`, choice 4) from one section to
  five (general, cameras & lenses, darkroom, composition & technique, film &
  processing) with 14 December 1988 seed posts.

- Added shortwave broadcast schedules to the Amateur Radio Forum (`GO HAMNET`):
  a new Broadcast Listening section (section 8) with December 1988 schedules for
  the BBC World Service, Voice of America, and Deutsche Welle, rendered with a
  verified-vs-estimate fact marking convention, plus one seed post announcing
  the section (`hamnet-1988-017`).

- Merged 47 new seed posts (16 pets, 16 trains, 14 photography, 1 hamnet) from
  computer_communities.json (pack id bumped to
  `computer-communities-1988-v4` so existing databases pick up the new posts;
  the merge skips known content_ids, so the bump is safe and repeat installs
  are no-ops).

- Added the 1988 Holiday Shopping Guide news special (News option 13,
  `GO GIFTGUIDE`): hottest gifts of Christmas 1988, a catalog-vs.-mall price
  comparison, a toy shortage and shelf-watch report, and gift trends for '88,
  all written from a December 1988 perspective, plus an interactive gift picker
  that recommends a present from the catalog by recipient and budget.

- Added the Christmas in the Sim news special (News option 14, `GO CHRISTMAS`):
  a 25-day advent calendar with one treat unlocked each day December 1-25,
  browsable holiday CB topics, and a Christmas music section of 1988-or-earlier
  albums and songs (albums and songs also wired into Entertainment as a new
  "Christmas Music" section).

- Added the Health & Fitness Forum (`GO FITNESS`, forum choice 19) with six
  sections (aerobics, running, weight training, nutrition, sports
  medicine/injuries, mind & body) and 16 December 1988 seed posts, merged from
  computer_communities.json (pack id bumped to
  `computer-communities-1988-v3` so existing databases pick up the new posts).

- Added a "1988 Weather Retrospective" section to the Weather Wire (News option
  10): a December 1988 look back at Hurricane Gilbert and the summer drought
  and heat wave, written three months after the fact.

- Added seasonal holiday topics to the CB simulator: during December, keyword
  mentions of Christmas topics are answered by established CB handles, on top
  of the regular topic set.

- Verified and covered the December 1988 movie review set (Rain Man, Twins,
  Scrooged, The Naked Gun, Working Girl) with regression tests; the five
  reviews pre-existed from content pack 2 and remain in Entertainment's Movies
  section.

- Added the 1988 Year in Review news special (News option 12, `GO YEARINREVIEW`):
  Election '88 results, top news stories, the Armenia earthquake wire, science
  and technology highlights, and a best-of roundup spanning movies, music,
  sports, and technology. Armenia coverage appears from December 7 onward and
  the Pan Am Flight 103 developing story appears from December 21 onward,
  gated by the session's simulated date.

- Added three new interest forums (choices 16-18): the Cooking Forum
  (`GO COOKING`, 6 sections, 16 December 1988 posts), the Aviation Forum
  (`GO AVIATION`, 6 sections, 16 posts), and the Comics & Sci-Fi Forum
  (`GO SCIFI`, 6 sections, 16 posts). Seed messages are merged into the forums
  from computer_communities.json at startup via cis_communities.merge_forums,
  matching the Guitar/Space pattern.

- Expanded December 1988 Sports & TV (News option 8, `GO SPORTS`) with four new
  sections: a Super Bowl XXIII preview (preview-only; the game is January 22,
  1989, after the sim date), a 1988 World Series recap, mid-December 1988 NBA
  standings (25 teams, 1988-89 expansion placements verified), and NHL standings
  with points math (21 teams, verified as of Dec 15, 1988).

- Fixed the Forums Directory screen to list all 18 forum choices (it previously
  stopped at 14, omitting Space, Cooking, Aviation, and Comics & Sci-Fi).

- Added the time capsule: a Temporal Destination step during connection setup
  beside the baud-rate prompt, offering Present Day, fourteen featured dates
  (1981-1991), any date from 1979 through 1998, or session-scoped Surprise Me.
  Featured dates carry curated archival content packs (headlines, sysop
  announcements, CB topics, market notes); each account remembers its last era
  and is offered a post-login "Return to <date>?" shortcut when Present Day is
  chosen. Ambient CB and simulated forum content adapt to the session date.

- Added four new time-capsule featured dates with curated archival content
  packs: Columbia's first flight (1981-04-12), the INF Treaty signing
  (1987-12-08), the Loma Prieta earthquake (1989-10-17), and the Hubble launch
  (1990-04-24). Each pack carries 10 era-written headlines, sysop announcements,
  CB conversation topics, and market notes; the picker now offers fourteen
  featured dates in chronological order.

- Added the Amateur Radio Forum (8 sections, 16 seeded December 1988 posts,
  bulletins, two scheduled nets; `GO HAMNET`).

- Added NIGHT SHIFT: EARTH STATION, a standalone 17-room text adventure
  (Games option 7) with a repair-chain win condition, 81-move clock, scoring,
  and persistent high scores.

- Added December 1988 Sports & TV (News option 8, `GO SPORTS`): NFL standings
  and scores, prime-time TV grid, and MLB hot-stove news.

- Added the Guitar & Music Forum (6 sections, 16 December 1988 posts;
  `GO GUITAR`), the Veterans Forum (4 sections, 16 posts; `GO VETERANS`), the
  Roots & Branches genealogy forum (6 sections, 18 posts; `GO ROOTS`), and the
  Tech Talk Forum (6 sections, 16 posts; `GO TECH`).

- Added the Trading Post classifieds (`GO TRADINGPOST`): FOR SALE, WANTED, and
  TRADE boards seeded with 15 December 1988 ads, member ad placement, and 30-day
  expiry on the simulated clock.

- Added December 1988 Entertainment (News option 9, `GO ENTERTAINMENT`):
  date-aware Billboard Hot 100 number one, movie reviews, and January 1989 bowl
  previews.

- Added the December 1988 Weather Wire (News option 10): 12 city forecasts, 7
  ski resorts, and three date-aware variants; `GO WEATHER` still opens the live
  Open-Meteo service.

- Added the Daily Crossword (Games option 8, `GO CROSSWORD`): seven rotating
  7x7 1988-themed puzzles, one per weekday, with persistent per-member progress.

- Added Books & Magazines (News option 11, `GO BOOKS`): December 1988 hardcover
  bestseller lists, magazine cover blurbs, staff reviews, and back-issue library
  files.

- Expanded Online Weekly from 25 to 50 articles across its five December issues.
  Every original article is more than twice its previous length; all articles
  exceed 400 words, with over 24,000 words of article text in the collection.
- Added practical 1988 coverage of DOS memory, modems, backups, HyperCard,
  graphics standards, mail merge, shareware, BASIC, spreadsheets, MIDI,
  desktop publishing, Apple II learning, BBS culture, databases, and networking.
- Preserved issue dates and original article IDs for existing reading history.
  Verified tenth-article selection, publication gating, service links, and full
  ASCII exports at terminal-friendly widths.

- Expanded Online Weekly magazine: three new recurring departments in each of
  the five December 1988 issues — News Briefs, SysOp Q&A, and Letters to the
  Editor — for 15 new articles (65 total, 13 per issue, each 400+ words).
  Topics include DOS memory management, modems, backups, a holiday gift guide
  for computerists, BBS culture, and a 1988 year-in-review. Content is merged
  from `cis_magazine.py` at load; original article IDs, issue dates, and
  `magazine_issues.json` are unchanged, so reading history is preserved.

- Added the Classic Games Arcade (Games option 9, `GO ARCADE`): Hunt the Wumpus,
  Hamurabi, Super Star Trek, and Blackjack played with fictional arcade chips
  worth nothing but pride, with one entry per game per member session recorded
  in Player Records.

- Added the Space & Astronomy Forum (6 sections, 16 seeded December 1988 posts;
  `GO SPACE`): shuttle and spaceflight, deep-sky observing, planets and probes,
  amateur telescopes, NASA and space news, and star parties.

- GO and G commands now work at nested service prompts, including readers,
  forms, line editing, CB, and the post-login briefing. Navigation exits the
  current prompt without submitting its input; saved composition drafts remain.
- Unknown GO destinations re-prompt. Password input remains literal and adventure
  directions such as GO NORTH retain their local meaning.

- Replaced repeated daily forum filler with six original discussions. Four
  follow-ups per discussion deliver suggestions, test results, and resolutions
  after 2, 4, 8, and 24 simulated hours. Each discussion opens once per installation.
- Added an interactive first-call tour under User Information option 10, with
  real mailbox, forum, library, and activity stops and saved visit markers.
  Service representatives remain available through the tour's A command.

## 1.16.0

- Added the PHONES host directory with 199 searchable cities, historical access
  numbers, and clearly labeled fictional supplements.
- Show top-menu member announcements only on the first visit of a login session.

- Added Online Weekly: five original December 1988 magazine issues with 25
  articles, date-based publication, searchable back issues, and saved reading progress.
- Added News Services option 7, `GO MAGAZINE` / `GO WEEKLY`, activity discovery,
  and complete plain-text issue downloads in both console and web sessions.

- Replaced the web Capture link with Save text for the current session transcript
  or selected terminal text, retaining cleared pages and masking password input.
- Library transfers, generated reports, and closed captures now offer real browser
  downloads with retry links and isolated, expiring session snapshots.

- Added Commodore/Amiga, Apple II, Atari ST, and DOS Software forums with 12
  discussion sections, 36 original threaded posts, and community conference topics.
- Added 16 usable library files: five BASIC listings, original reference notes,
  project worksheets, ASCII art, and a short fictional club newsletter.
- Added direct forum/library GO commands and `I number` file information with
  usage instructions, release history, and simulated member reviews.
- Install the content pack once in a transaction while preserving existing posts,
  uploads, and download counts.

## 1.15.0

- Added the persistent Online Adventure League with Scout, Engineer, and Courier
  classes, health, experience levels, gold, inventory, and three campaign chapters.
- Added deterministic daily quests, class-specific approaches, rare relic rewards,
  rotating events, and SysOp-controlled Adventure world bulletins.
- Added persistent guilds, simulated parties, EasyPlex invitations and level notices,
  Gamers Forum adventure journals, and League details in Player Records.
- Preserved all existing Silent Mainframe, MegaWars, and Trivia save records.

## 1.14.0

- Added persistent buy and sell limit orders with automatic execution, order history,
  and EasyPlex fill notices.
- Added idempotent fictional INTC dividend and AAPL two-for-one split processing.
- Added a seven-day semiconductor market arc, analyst commentary, and an Investment
  Club forecast challenge with closing scorecards and rankings.
- Connected CHIP-88 member decisions to small, member-specific INTC and MOT sentiment
  adjustments while preserving deterministic delayed market quotes.

## 1.13.0

- Added a seven-day TERMLINK shareware arc that advances from announcement through
  release, serial-port reports, diagnostics, patch submission, approval, and thanks.
- Connected six evolving IBM Hardware Forum posts to versioned TERM10.TXT and
  TERM11.TXT Data Library entries with pending, approved, withdrawn, and replacement
  metadata.
- Added project watches, EasyPlex release notifications, tester configuration reports,
  ByteBender relationship memory, contributor recognition, and reputation points.
- Added `GO SHAREWARE` and `GO TERMLINK`, plus direct transfer of the newest approved
  release and safe text-only shareware packages.

## 1.12.0

- Extended Comp-U-Store fulfillment through DELIVERED status and converted delivered
  order quantities into individually tracked, persistent owned-equipment records.
- Added installation against the catalog compatibility index, including installed and
  compatibility-help states tied to the member's selected computer system.
- Added warranty cases, EasyPlex vendor follow-ups, IBM Hardware Forum guidance,
  returns, owner reports, and resale through Electronic Classifieds.
- Added Owned Equipment to Shopping, Profile, achievements, `GO EQUIPMENT`, and
  `GO OWNED`, with idempotent delivery processing for safe event retries.
- Connected warranty activity to the persistent Helen/Orders relationship.

## 1.11.0

- Expanded existing simulated-member memories into persistent relationship records
  with exchanges, trust, friction, relationship levels, recent topics, and open favors.
- Added UNFAMILIAR, ACQUAINTED, REGULAR, TRUSTED, CONFIDANT, and RIVAL relationship
  states, including backward-compatible levels for existing member histories.
- Connected Forum replies and CB conversations to the same relationship progression;
  trusted contacts and rivals now respond with distinct acknowledgements.
- Added personal EasyPlex messages at relationship milestones and `GO PEOPLE`,
  `GO RELATIONSHIPS`, and `GO CONTACTS` for the member relationship directory.
- Connected Special Desk outcomes to recurring-member memory and expanded Profile
  correspondent summaries with relationship levels.

## 1.10.0

- Added three deterministic December 1988 storm systems affecting nine airport-route
  combinations during Great Lakes snow, a Northeast coastal storm, and central ice.
- Added automatic reservation evaluation, persistent action-required status, immediate
  Travel Weather Desk EasyPlex alerts, activity notices, and Trip Folder visibility.
- Added a Weather Operations Center with alternate-flight, protective-rail, airport-
  hotel waitlist, standby, and weather-waiver cancellation decisions.
- Protected completed weather choices from stale scheduled ticketing events and added
  forecast, active, and past operational bulletins.

## 1.9.0

- Added CHIP-88, a persistent December 1988 member investigation spanning EasyPlex,
  the IBM Hardware Forum, Period News, MicroQuote market reports, and Reference.
- Added evidence tracking, dashboard status, service-specific clues, activity records,
  three final decisions, distinct consequences, and a closing EasyPlex report.
- Added `GO CASE` and `GO INVESTIGATE`, plus a Special Desk Reference index and a
  story dispatch integrated into the period Business News wire.

## 1.8.0

- Expanded MegaWars with persistent Star Command missions, experience ranks, shields,
  hull damage, missiles, tactical defense, docking, repairs, equipment purchases, and
  a nine-sector campaign map while retaining existing careers.
- Expanded The Silent Mainframe with optional cooling and diagnostic objectives, new
  rooms and items, maps, scoring, full-restoration bonuses, and persistent win records.
- Replaced single-question trivia visits with deterministic five-question tournaments,
  a larger period-computing question bank, streaks, best rounds, and tournament points.
- Added a Player Records screen summarizing progress across all three games.
- Added a manifest-verified, staged Linux upgrade workflow with database backup,
  application rollback, installed-version tracking, and systemd health checks.
- Added standardized project metadata, bounded web dependencies, operational logging,
  backup integrity checks, upgrade-backup retention, and cleaner release contents.

## 1.7.0

- Corrected airline time arithmetic, added December 1988 date validation, and made delayed/cancelled/overnight schedule displays valid.
- Added SQLite-locked read-modify-write operations for concurrent trades, carts, notes, hints, events, activity, reservations, rebooking, and traveler preferences.
- Added state validation and SysOp `REPAIR STATE` recovery for malformed events, portfolios, notebooks, reservations, and new-service containers.
- Added upgrade tests for every prior application schema, concurrent-trade stress coverage, travel time/date tests, and release smoke verification.
- Added contextual and searchable HELP, `?`, `COMMANDS`, unambiguous GO abbreviations, one-time discovery hints, a downloadable 40-column-safe command card, and a dependency-free release/Linux/member-workflow smoke test.
- Updated global HELP with every command-line personal tool and GO destination added by the recent expansions, plus accurate FIND, NOTE, selection, capture, maintenance, and session commands.
- Added an integrated personal Calendar, Notebook with global NOTE command, Download Center, achievements, session-cost analysis, guided first-call tour, and recurring Travel, Finance, and Store representatives with delayed EasyPlex replies.
- Added weekend market closures, period-wire sector effects, a December portfolio challenge, operational flight delays and cancellations, a combined air/return/hotel planner, and persistent SysOp market, weather, travel, and store bulletins.
- Added a persistent fictional stock-market portfolio with $10,000 starting cash, confirmed whole-share purchases and sales, period-style commissions, weighted average cost, realized and unrealized profit/loss, total return, and a 200-entry trade ledger.
- Added personal Trip Folders, saved traveler preferences, timed ticketing and hotel-guarantee updates, rail and rental-car guidance, downloadable ASCII itineraries, and global airport/hotel discovery.
- Added business-wire links in company reports, illustrative economic and fixed-income indicators, downloadable portfolio research packets, and global company discovery.
- Expanded Business & Financial with twelve delayed quotations, persistent member watch lists, searchable company and industry reports, sector context, and clearer simulation notices.
- Expanded Travel Services with a twelve-airport directory, dated coach and first-class fare displays, passenger itineraries, six-city hotel rates and lodging requests, destination Travelgrams, EasyPlex confirmations, and profile activity.
- Expanded Comp-U-Store into a persistent 36-item 1988 catalog with rotating specials and availability, compatibility guidance for IBM PC, Macintosh Plus, Commodore 64, and TRS-80 systems, simulated-member owner reports, categories, search, pagination, saved carts, itemized shipping, EasyPlex status notices, global FIND results, back orders, and multi-day fulfillment.
- Added per-member Reference search history, subject indexes, marked records, downloadable ASCII research packets, and context-sensitive record suggestions in Forums and News.
- Moved Reference content into a validated JSON catalog and added 12-record pagination, direct record-ID access, Boolean AND/OR/NOT queries, and SEE ALSO cross-references.
- Replaced the shared four-entry Reference placeholder with four distinct searchable and browsable databases containing 200 records, selectable full entries, medical notices, and global FIND integration.
- Added a hidden monotonic simulation timeline so delayed events survive the December 31 display wrap, plus a Linux systemd user timer that processes due events every five minutes.
- Added a separate 64-dispatch December 1988 news edition with per-member presentation history, preventing repeats across five consecutive editions.
- Expanded CB from a few keyword lines to broad period topic sets, specialist handles, more ambient conversation, and contextual follow-up exchanges.
- Added period-style cross-service cases: selected Forum questions receive delayed replies from recurring members, EasyPlex notices, and numbered Data Library recommendations; those members can recognize the caller later in CB.
- Expanded Adventure into a multi-room inventory puzzle and MegaWars into a persistent sector campaign with trading, repairs, tactical turns, credits, cargo, and victories.
- Preserved member classifieds across simulated-day changes while continuing to expire individual listings.
- Added delayed mail, forum-reply, and multi-day order events so the service evolves between calls.
- Added member-specific forum, classified, and library activity history to the profile summary and main-page notices.
- Changed forum watches to follow the complete discussion tree, including replies to nested replies.

## 1.6.0

- Added multiple simultaneous browser sessions and shared SQLite-backed CB channels.
- Added shared forum conferences and a SysOp display of currently connected members.
- Added an optional Telnet-style TCP listener with ANSI/VT100 screen clearing.
- Added Linux launchers and optional user services for both remote interfaces.

## 1.5.0

- Added forum thread trees, thread watch controls, EasyPlex folders and contacts.
- Added classified categories, order and reservation lifecycle controls.
- Expanded readable library documents and persistent simulated-member memory.
- Added SysOp content controls and end-to-end workflow tests.

## 1.4.0

- Added transactional, numbered SQLite upgrades with automatic pre-upgrade backups.
- Added dynamic activity discovery, global search, threaded forums, readable library
  documents, member classifieds, fictional reservations, and SysOp event controls.
- Added compatibility migration for classified records created before IDs were used.

## 1.3.0

- Added persistent scheduled events, simulated time, forum activity, EasyPlex notices,
  dynamic finance, travel, weather, classifieds, CB responses, and trivia scores.

## 1.2.0

- Split authentication, billing, mail, forum, library, and news services into modules.

## 1.1.0

- Converted mutable persistence and backups from JSON files to SQLite.

## 1.0.0

- Initial Classic CompuServe simulation release.
