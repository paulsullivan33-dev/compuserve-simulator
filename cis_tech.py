"""Tech Talk Forum content module.

Section spec and December 1988 seed posts for the ``tech`` forum
("Tech Talk Forum"): IBM PC & clones, Macintosh, Amiga vs Atari ST,
OS/2 & operating systems, modems & telecom, and CD-ROM & new tech.

Period rules enforced by this module:
* Hardware is 1988-era only: 286/386 (SX and DX), IBM PS/2, Compaq
  Deskpro, EGA/VGA, Hayes Smartmodem 1200/2400, USRobotics Courier HST,
  Macintosh Plus/SE/II, Amiga 500/2000, Atari 1040ST, NEC MultiSync.
  No post-1988 tech is ever mentioned: no Windows 95/98, no Pentium,
  no USB, no Wi-Fi, no World Wide Web, no Linux (1991), no internet
  as we know it.
* Software is December 1988: MS-DOS 3.3/4.0, OS/2 1.0/1.1, Windows/286
  and Windows/386 (Windows 2.x), Lotus 1-2-3, WordPerfect 5.0, dBase
  III Plus, Turbo Pascal 5.0, Turbo C, HyperCard, DESQview. Nothing
  references anything after December 1988.
* Online life means BBSs, CompuServe forums, ProComm and Qmodem --
  there is no email-as-we-know-it and no internet.
"""

FORUM_ID = "tech"
FORUM_TITLE = "Tech Talk Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("tech_pc", "IBM PC & Clones"), ...}
# The coordinator wires this into FORUM_CATALOG["tech"]["sections"].
SECTIONS = {
    "1": ("tech_pc", "IBM PC & Clones"),
    "2": ("tech_mac", "Macintosh"),
    "3": ("tech_amiga", "Amiga vs Atari ST"),
    "4": ("tech_os", "OS/2 & Operating Systems"),
    "5": ("tech_modem", "Modems & Telecom"),
    "6": ("tech_cdrom", "CD-ROM & New Tech"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "tech-1988-001",
        "section": "tech_pc",
        "date": "12/01/88",
        "author": "SYSOP_SAM",
        "subject": "Welcome to the Tech Talk Forum",
        "body": (
            "Welcome to Tech Talk, the forum for people who argue about "
            "computers the way other people argue about sports. We have "
            "six sections: IBM PC & Clones, Macintosh, Amiga vs Atari ST "
            "(yes, it needs its own section -- you people never stop), "
            "OS/2 & Operating Systems, Modems & Telecom, and CD-ROM & New "
            "Tech. Newcomers: post your rig in your first message. House "
            "rules: no flame wars, cite your sources, and if you quote a "
            "magazine, name the issue. Enjoy."
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-002",
        "section": "tech_pc",
        "date": "12/03/88",
        "author": "386DREAMER",
        "subject": "386 vs 286 -- is the 386 worth double the money?",
        "body": (
            "I am pricing a new machine and I cannot make the 386 math "
            "work. A 16 MHz 386 box with 1 MB RAM and a 40 MB hard drive "
            "runs about twice what a 12 MHz 286 with the same specs costs. "
            "I run Lotus 1-2-3, WordPerfect 5.0, and dBase III Plus, all "
            "under DOS 3.3. None of them touch the 386's 32-bit mode. Am I "
            "paying for a future that has not arrived yet? Or is the 386 "
            "worth it now just for the raw clock speed and the bigger "
            "address space? Talk me into or out of the 386 -- my wallet "
            "is listening."
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-003",
        "section": "tech_pc",
        "date": "12/05/88",
        "author": "VGA_VIC",
        "subject": "EGA vs VGA -- upgrade the monitor or the card first?",
        "body": (
            "I have an EGA card and a perfectly good EGA monitor, and I "
            "keep staring at the VGA ads. The 640x480 in 16 colors looks "
            "gorgeous in the magazines, and the analog signal means more "
            "colors later, but a VGA card plus a multisync monitor is a "
            "serious chunk of change. For those who made the jump: is VGA "
            "worth it for business graphics and desktop publishing, or is "
            "it mostly a gamer upgrade? And can a VGA card drive my old "
            "EGA monitor in the meantime, or do I need the whole package "
            "at once?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-004",
        "section": "tech_pc",
        "date": "12/07/88",
        "author": "BYTEFAN",
        "subject": "IBM PS/2 vs the clones -- is the badge worth it?",
        "body": (
            "My office is standardizing on PCs and the eternal question is "
            "back: genuine IBM PS/2 with Micro Channel, or a clone from "
            "Compaq or one of the mail-order houses? The PS/2 Model 50 and "
            "60 are beautiful machines and IBM service is IBM service, "
            "but a Compaq Deskpro 386 costs less and runs everything the "
            "IBM runs -- the clone makers have caught up on quality. The "
            "Micro Channel bus worries me: none of my old AT cards will "
            "fit. Is MCA the future or a dead end? What is your shop "
            "buying this year, and why?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-005",
        "section": "tech_mac",
        "date": "12/04/88",
        "author": "MACMANIAC",
        "subject": "Will Apple survive? The Mac II changed my mind",
        "body": (
            "I keep hearing the doom talk -- Apple is niche, the Mac is a "
            "toy, IBM will crush them -- and then I sit down at a Mac II "
            "with the 13-inch color monitor and 5 MB of RAM and the doom "
            "talk sounds ridiculous. PageMaker on this thing is faster "
            "than anything on a PC, the color is gorgeous, and HyperCard "
            "has every department building little stack applications. The "
            "Mac SE is selling into businesses now, not just schools. So "
            "I will ask it straight: are the Apple obituaries premature, "
            "or am I drinking the Cupertino Kool-Aid?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-006",
        "section": "tech_mac",
        "date": "12/09/88",
        "author": "DESKTOP_DAN",
        "subject": "Maxing out a Mac Plus -- 4 MB RAM and HyperCard",
        "body": (
            "Took my Mac Plus from 1 MB to 4 MB this weekend (yes, with "
            "the 150-nanosecond SIMMs, and yes, it was terrifying opening "
            "the case). The difference in MultiFinder is night and day -- "
            "I can finally keep PageMaker, Word, and HyperCard open at "
            "once. Speaking of HyperCard: who else is building stacks? I "
            "made a home inventory stack in an evening with zero "
            "programming experience. Bill Atkinson is a genius. For the "
            "Plus owners here: is 4 MB the practical ceiling, and what "
            "are you doing with it?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-007",
        "section": "tech_amiga",
        "date": "12/06/88",
        "author": "AMIGA_ANGIE",
        "subject": "Amiga vs Atari ST -- settle it once and for all",
        "body": (
            "Time for the thread that never ends. Amiga 500 versus Atari "
            "1040ST, and I want arguments, not slogans. The Amiga has the "
            "custom chips -- real multitasking, 4096 colors, stereo "
            "sampled sound, genlock for video work. The ST has the MIDI "
            "ports built in, a cleaner high-res monochrome mode, and a "
            "price that keeps undercutting the Amiga. For games the Amiga "
            "wins on graphics; for music the ST owns the studio. So which "
            "machine would you buy TODAY with your own money, and what is "
            "the one thing that decides it? Keep it civil, people."
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-008",
        "section": "tech_amiga",
        "date": "12/11/88",
        "author": "ST_STEVE",
        "subject": "RE: Amiga vs Atari ST -- the ST case",
        "body": (
            "ST owner here, making the case. My 1040ST with the SM124 "
            "monochrome monitor gives me a rock-solid 640x400 desktop for "
            "WordPerfect and publishing work -- try reading text all day "
            "on an interlaced Amiga screen and get back to me. The built-"
            "in MIDI ports mean my sequencer rig cost me nothing extra, "
            "and the ST's software library for music is deeper. The Amiga "
            "is the better game machine and the better video machine, no "
            "argument. But for a working computer on a budget, the ST is "
            "the rational buy. There, I said it."
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-009",
        "section": "tech_os",
        "date": "12/08/88",
        "author": "OS2CURIOUS",
        "subject": "OS/2 vs DOS -- is OS/2 the future or a footnote?",
        "body": (
            "IBM and Microsoft keep telling us OS/2 is the future: real "
            "multitasking, protected mode, no more 640K wall. But OS/2 1.1 "
            "with the Presentation Manager needs a 286 with serious RAM, "
            "a hard drive, and patience -- and my DOS programs mostly run "
            "fine under plain DOS 3.3 today. The software houses are all "
            "saying 'OS/2 versions coming,' but coming when? I need a "
            "machine that earns its keep next year, not three years from now. Who here is "
            "actually running OS/2 daily? Is it ready, or should the rest "
            "of us stick with DOS and wait for the dust to settle?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-010",
        "section": "tech_os",
        "date": "12/12/88",
        "author": "DOS4EVER",
        "subject": "DOS 4.0 shell gripes + DESQview for multitasking",
        "body": (
            "Upgraded to DOS 4.0 for the big-partition support and the new "
            "shell, and I have mixed feelings. The 32 MB partition limit "
            "being gone is wonderful -- my 40 MB drive is finally one "
            "volume. But the shell is slow and it eats memory I used to "
            "spend on TSRs. Meanwhile a friend showed me DESQview running "
            "three DOS programs at once on a 386, switching between them "
            "instantly. That feels like the multitasking future without "
            "waiting for OS/2. Anyone running DESQview daily? How much "
            "expanded memory does it really want, and does it play nice "
            "with SideKick?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-011",
        "section": "tech_modem",
        "date": "12/02/88",
        "author": "HAYES_FAN",
        "subject": "Hayes vs USRobotics -- the modem holy war",
        "body": (
            "Picking a 2400 baud modem and it comes down to the Hayes "
            "Smartmodem 2400 versus the USRobotics Courier HST. The Hayes "
            "is the standard -- the AT command set every BBS and every "
            "communications program speaks is Hayes-compatible, and the "
            "build quality is legendary. The Courier costs less, does "
            "9600 bps HST to other Couriers, and the USR support BBS is "
            "excellent. But HST only helps if the board you call has a "
            "Courier too. For general CompuServe and BBS use at 2400, "
            "which one do you trust at 2 AM when the line is noisy?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-012",
        "section": "tech_modem",
        "date": "12/10/88",
        "author": "MODEM_MIKE",
        "subject": "2400 baud upgrade -- is 1200 still enough?",
        "body": (
            "Still running a trusty 1200 baud modem and wondering if the "
            "jump to 2400 is worth it. The math says everything downloads "
            "twice as fast and the per-minute connect charges on the big "
            "services get cut in half -- that alone might pay for the "
            "modem in a few months of heavy use. But do the BBSs I call "
            "even support 2400? Most of the local boards top out at 1200, "
            "and long-distance 2400 calls can be flaky on a noisy line. "
            "Who made the jump this year? Did your phone bill thank you, "
            "and did you run into boards that could not keep up?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-013",
        "section": "tech_modem",
        "date": "12/14/88",
        "author": "BBS_BOB",
        "subject": "ProComm Plus scripts and my favorite BBS doors",
        "body": (
            "Spent the weekend writing ProComm Plus scripts to auto-log "
            "into my three favorite BBSs -- dial, wait for the prompt, "
            "send the password, jump straight to the new-messages scan. "
            "It feels like living in the future. The door games are "
            "eating my evenings: TradeWars on one board, Legend of the Red "
            "Dragon on another. Qmodem users: does Qmodem's script language "
            "do dialing directories as cleanly? And what is everyone "
            "playing in the doors this month? I need a new time sink."
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-014",
        "section": "tech_cdrom",
        "date": "12/13/88",
        "author": "CDROM_CARL",
        "subject": "CD-ROM hype -- revolution or expensive coaster maker?",
        "body": (
            "The magazines will not shut up about CD-ROM: 550 megabytes on "
            "one disc, a whole encyclopedia on a shiny platter. The drives "
            "are finally under a thousand dollars and Microsoft Bookshelf "
            "and the Grolier encyclopedia look genuinely useful -- "
            "instant lookup without swapping twenty floppies. But the "
            "drives are slow, the discs cost a fortune to press, and most "
            "titles feel like demos of what the format could be. Early "
            "adopters: is your CD-ROM drive earning its keep, or is it "
            "the most expensive paperweight in the office? What title "
            "justifies the drive?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-015",
        "section": "tech_cdrom",
        "date": "12/16/88",
        "author": "BYTEFAN",
        "subject": "CD-ROM drive prices are finally dropping",
        "body": (
            "Saw a CD-ROM drive advertised at $799 this week, down from "
            "well over a grand last year. At this rate they will be "
            "standard equipment in a year or two. The catch is still software: a "
            "handful of reference titles, a few clip-art collections, and "
            "not much else. But the trajectory is clear -- when the "
            "drives hit $500, every PC maker will bundle one. Question "
            "for the group: buy now and ride the early titles, or wait a "
            "year for cheaper drives and a real software library?"
        ),
        "parent": None,
    },
    {
        "content_id": "tech-1988-016",
        "section": "tech_cdrom",
        "date": "12/18/88",
        "author": "DESKTOP_DAN",
        "subject": "Killer app watch: what belongs on a CD-ROM?",
        "body": (
            "Forget the hardware debate for a minute -- what SHOULD be on "
            "a CD-ROM? Reference works are the obvious answer: "
            "encyclopedias, dictionaries, the Microsoft Bookshelf bundle, "
            "maybe a whole clip-art library for desktop publishing. But I "
            "want to hear the wild ideas: a disc with every shareware "
            "program from every BBS in the country? The complete works of "
            "a magazine's back issues, searchable? Phone directories for "
            "the whole nation on one disc? The format is a solution "
            "looking for problems -- pitch me the title that sells a "
            "million drives."
        ),
        "parent": None,
    },
]


def section_spec():
    """Return the forum section spec for coordinator wiring."""
    return {k: tuple(v) for k, v in SECTIONS.items()}


def seed_posts():
    """Return a copy of the seed posts for forum seeding."""
    return [dict(post) for post in SEED_POSTS]
