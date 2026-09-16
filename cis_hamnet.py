"""Amateur Radio (Hamnet) Forum content module.

Expands the ``hamnet`` forum already present in compuserve.py's FORUM_CATALOG
(title: "Amateur Radio Forum"). The expanded section spec, seed posts,
ARRL-style bulletins, and scheduled on-air nets live here; the coordinator
wires SECTIONS into the forum catalog.

Period rules enforced by this module:
* License classes are Novice / Technician / General / Advanced / Extra.
  The no-code Technician class did not exist until 1991 -- it is never
  mentioned.
* Nothing in this module references anything after December 1988.
"""

from cis_session import read_input as input

from datetime import timedelta

FORUM_ID = "hamnet"
FORUM_TITLE = "Amateur Radio Forum"

# Expanded section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("hamnet_packet", "Packet Radio"), ...}
# The coordinator wires this into FORUM_CATALOG["hamnet"]["sections"].
SECTIONS = {
    "1": ("hamnet_packet", "Packet Radio"),
    "2": ("hamnet_rigs", "HF/VHF Rigs"),
    "3": ("hamnet_antennas", "Antennas & Towers"),
    "4": ("hamnet_dx", "DX & Contesting"),
    "5": ("hamnet_license", "License Study"),
    "6": ("hamnet_arrl", "ARRL Bulletins"),
    "7": ("hamnet_swap", "Swap & Shop"),
}

WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

NETS = [
    {
        "name": "CompuServe Ham Net",
        "weekday": 2,  # Wednesday
        "time": "8:00 PM Central",
        "where": "CB simulator, channel 1 (the CB side of CompuServe)",
        "net_control": "N5SYS (rotating net control each week)",
        "description": (
            "Weekly voice-style check-in net run inside the CB simulator. "
            "All license classes welcome; check in with your callsign and "
            "location. After check-ins the floor opens for roundtable "
            "discussion -- rigs, packet, DX, whatever is on the bench."
        ),
    },
    {
        "name": "DFW Packet BBS Net",
        "weekday": 5,  # Saturday
        "time": "7:00 PM Central",
        "where": "145.01 MHz via packet, through the WB5PKT-7 digipeater",
        "net_control": "N5PKT",
        "description": (
            "Weekly packet-radio net for TNC owners. Bring your Kantronics "
            "KAM, AEA PK-232, or any TNC and connect to the net node. Topics "
            "rotate: BBS forwarding, KA9Q NOS experiments, HF packet, and "
            "traffic handling."
        ),
    },
]

ARRL_BULLETINS = [
    {
        "number": "ARLD049",
        "title": "ARRL DX Bulletin",
        "date": "December 8, 1988",
        "body": (
            "SB DX @ ARL $ARLD049\n"
            "ARLD049 DX news\n\n"
            "This week's bulletin was made possible with information provided\n"
            "by the Northern California DX Foundation and the operators\n"
            "listed below. Thanks to all.\n\n"
            "MONACO, 3A. 3A2LU is reported active on 20 meter CW most\n"
            "evenings around 0200Z. QSL via F6FYA.\n"
            "PITCAIRN ISLAND, VP6. VP6TC continues to be heard on 15 meter\n"
            "SSB near 21300 kHz around 1800Z. QSL via W0RJU.\n"
            "MACQUARIE ISLAND, VK0. VK0MM is expected to return to the air\n"
            "before the end of the month on 20 meters. QSL via VK2DEQ.\n"
            "SOUTH GEORGIA, VP8. VP8CKB has been worked on 40 meter CW\n"
            "near 7025 kHz around 0100Z. QSL via LA5NM.\n\n"
            "Conditions: Solar flux remains high as Cycle 22 builds toward\n"
            "its peak. Ten meters is open to most of the world during\n"
            "daylight hours -- check 28.4 to 28.6 MHz for DX.\n"
        ),
    },
    {
        "number": "ARLX012",
        "title": "ARRL 10-Meter Contest Reminder",
        "date": "December 5, 1988",
        "body": (
            "The ARRL 10-Meter Contest runs from 0000Z Saturday, December 10\n"
            "through 2359Z Sunday, December 11 -- phone and CW, 28 MHz only.\n\n"
            "Exchange: signal report and your state or province; DX stations\n"
            "send signal report and serial number. Multipliers are US states,\n"
            "Canadian provinces, and DXCC countries worked per mode.\n\n"
            "With the sunspot cycle climbing, this year's contest should be\n"
            "the best in a decade. Even a modest station -- a dipole at 20\n"
            "feet and 100 watts -- can work the world on 10 meters right now.\n"
            "Logs are due at ARRL HQ within 30 days. See December QST for\n"
            "complete rules."
        ),
    },
    {
        "number": "ARLX013",
        "title": "ARRL/VEC Amateur Exam Session",
        "date": "December 6, 1988",
        "body": (
            "The Dallas Amateur Radio Club will sponsor an ARRL/VEC\n"
            "examination session on Saturday, December 17, at 9:00 AM at the\n"
            "Red Cross Building, 2300 McKinney Avenue, Dallas, Texas.\n\n"
            "All license classes will be examined: Novice, Technician,\n"
            "General, Advanced, and Extra. Code tests will be given at 5,\n"
            "13, and 20 words per minute per FCC requirements.\n\n"
            "Bring your current license (original and a copy), a photo ID,\n"
            "and the $4.50 test fee in cash or check. Walk-ins are welcome,\n"
            "but pre-registration with the VE team is appreciated. Talk-in\n"
            "on the 146.88 repeater."
        ),
    },
    {
        "number": "ARLX014",
        "title": "Straight Key Night Announcement",
        "date": "December 12, 1988",
        "body": (
            "ARRL Straight Key Night will be held from 0000Z to 2359Z\n"
            "January 1, 1989. Dust off that J-38 or Vibroplex, warm up the\n"
            "finals, and join the fun on 80 through 10 meters.\n\n"
            "This is not a contest -- the idea is to get on the air with a\n"
            "straight key or bug and enjoy some old-fashioned brass pounding.\n"
            "Vote for the best fist you hear and send your list of calls\n"
            "worked to ARRL HQ. Results and soapbox comments appear in QST."
        ),
    },
]

SEED_POSTS = [
    {
        "content_id": "hamnet-1988-001",
        "section": "hamnet_general",
        "date": "12/01/88",
        "author": "N5SYS",
        "subject": "CompuServe Ham Net -- Wednesdays 8 PM Central",
        "body": (
            "Welcome to the Amateur Radio Forum! We are starting a weekly "
            "CompuServe Ham Net every Wednesday at 8:00 PM Central on the CB "
            "simulator, channel 1. Check in with your callsign and location, "
            "then join the roundtable -- rigs, packet, antennas, DX, anything "
            "ham. All license classes are welcome, from Novice on up. I will "
            "serve as net control this week; the job rotates weekly, so "
            "volunteers are appreciated. Spread the word on your local "
            "repeater! 73, N5SYS."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-002",
        "section": "hamnet_packet",
        "date": "12/02/88",
        "author": "WB5JON",
        "subject": "Kantronics KAM impressions after a week",
        "body": (
            "My Kantronics KAM arrived last week and I have had it on the "
            "air for seven days now. The dual-port design is the real deal: "
            "I run VHF packet on 145.01 on one port and HF packet on 14.105 "
            "on the other, both at the same time, into my TS-440S. The HF "
            "gateway function works nicely, though HF packet is still slow "
            "going with the QRM. Mailbox works as advertised. Anyone else "
            "running a KAM as a dual-port gateway? I would like to compare "
            "notes on HF tuning levels."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-003",
        "section": "hamnet_packet",
        "date": "12/03/88",
        "author": "KA9RTZ",
        "subject": "RE: Kantronics KAM impressions after a week",
        "body": (
            "I have been running an AEA PK-232 for about six months and it "
            "has been rock solid on both VHF and HF packet. The KAM's "
            "dual-port trick is tempting, but the PK-232 also does RTTY, "
            "AMTOR, CW, and even FAX and SSTV with the right software, which "
            "keeps me happy. The new PK-232MBX with the mailbox option looks "
            "interesting too. For pure packet work both boxes are fine -- "
            "pick the one your local packet crowd can help you configure."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-004",
        "section": "hamnet_packet",
        "date": "12/04/88",
        "author": "N5PKT",
        "subject": "Weekly Packet BBS Net -- Saturdays 7 PM Central",
        "body": (
            "Announcing a weekly packet net for the forum: every Saturday at "
            "7:00 PM Central on 145.01 MHz through the WB5PKT-7 digipeater "
            "here in the Dallas area. Connect your TNC -- Kantronics KAM, "
            "AEA PK-232, MFJ-1270, whatever you have -- and join the "
            "roundtable. Each week we pick a topic: BBS message forwarding, "
            "KA9Q NOS experiments, HF packet techniques, or traffic "
            "handling. Out-of-area stations can check in through the HF "
            "gateway. Net control this week is N5PKT. 73 and see you on "
            "packet!"
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-005",
        "section": "hamnet_rigs",
        "date": "12/05/88",
        "author": "WD5ABC",
        "subject": "TS-440S or IC-735? Help me decide",
        "body": (
            "I am upgrading from my old TS-520S (tubes still glow, but my "
            "back is tired of lifting it) and I have narrowed it down to the "
            "Kenwood TS-440S and the Icom IC-735. Both are 100-watt HF "
            "all-mode rigs at a similar price. The 440S has the optional "
            "internal antenna tuner which appeals to me, and the IC-735 "
            "seems to have a slightly better receiver from what I read in "
            "the QST reviews. Anyone own one or both? How is the general "
            "coverage receive, and which would you buy again? Thanks! -- "
            "WD5ABC."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-006",
        "section": "hamnet_rigs",
        "date": "12/06/88",
        "author": "K9VHF",
        "subject": "RE: TS-440S or IC-735? Help me decide",
        "body": (
            "I have owned both, so here is my two cents. The TS-440S with "
            "the AT-440 internal tuner is a joy for portable and quick "
            "band changes -- push a button and it tunes. The IC-735 has the "
            "edge in receiver performance on a crowded 40 meters, and the "
            "passband tuning is smoother. If you operate mostly CW and SSB "
            "on HF, you cannot go wrong with either. My 440S has been "
            "trouble-free for two years. One note: budget for a good power "
            "supply and an external speaker for either rig; the internal "
            "speakers are small."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-007",
        "section": "hamnet_rigs",
        "date": "12/07/88",
        "author": "N5ZZT",
        "subject": "FT-757GX mobile installation report",
        "body": (
            "Finished installing the Yaesu FT-757GX in my pickup this "
            "weekend and I am impressed. The little box does HF plus 6 "
            "meters, and the general coverage receiver keeps the XYL happy "
            "with broadcast listening on road trips. Running a Hustler "
            "resonator set on a ball mount -- 20 and 40 meters so far. "
            "Voltage drop was my biggest fight; run heavy cable straight to "
            "the battery with fuses at both ends. Worked three states on 40 "
            "meter SSB on the drive to work Monday. Mobile HF is a blast."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-008",
        "section": "hamnet_antennas",
        "date": "12/08/88",
        "author": "WB5TWR",
        "subject": "Rohn 25G vs. free-standing tower?",
        "body": (
            "Planning my first real tower this spring: 40 feet with a small "
            "tribander and a 2-meter vertical on top. I am torn between Rohn "
            "25G guyed and a free-standing crank-up. The guyed tower is "
            "cheaper, but my lot is not huge and guy wires eat yard fast. "
            "The crank-up costs more but cranks down for storms and keeps "
            "the neighbors calmer. For those who have put up either: what "
            "did the concrete base cost you, and would you do it the same "
            "way again?"
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-009",
        "section": "hamnet_antennas",
        "date": "12/09/88",
        "author": "KA5ANT",
        "subject": "Dipole at 30 feet vs. trap vertical",
        "body": (
            "Small lot here and no tower yet, so the choice is a 40-meter "
            "dipole at 30 feet between two trees or a trap vertical with a "
            "decent radial field. I mostly work 40 and 20 meter SSB and some "
            "CW. The dipole is cheap and quiet, but the vertical might hear "
            "better on DX. For those who have tried both at modest heights: "
            "which got out better for you? I have room for about 30 radials "
            "if I go the vertical route."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-010",
        "section": "hamnet_dx",
        "date": "12/10/88",
        "author": "N5DXS",
        "subject": "10 meters is alive -- sunspots doing their thing",
        "body": (
            "What a week! With the solar flux climbing as Cycle 22 builds, "
            "10 meters has been open to everywhere during daylight. Worked "
            "VK, ZL, and a pile of Europeans on 28.5 MHz SSB with 100 watts "
            "to a dipole at 25 feet. If you have not tried 10 lately, spin "
            "the dial between 28.4 and 28.6 -- the band sounds like 20 "
            "meters did five years ago. This is shaping up to be the best "
            "cycle in a decade. Who else is chasing DX on 10?"
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-011",
        "section": "hamnet_dx",
        "date": "12/11/88",
        "author": "W5CNT",
        "subject": "ARRL 10-Meter Contest -- who's on?",
        "body": (
            "The ARRL 10-Meter Contest is on right now through Sunday night "
            "(0000Z Saturday to 2359Z Sunday). Exchange is signal report and "
            "state; DX sends signal report and serial number. With the band "
            "in this shape, even a modest station can have a great weekend. "
            "I will be on 28.4 to 28.6 SSB and down in the CW portion at "
            "28.05 looking for multipliers. Post your score and best DX here "
            "afterward. Good luck and have fun! -- W5CNT."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-012",
        "section": "hamnet_license",
        "date": "12/12/88",
        "author": "KA9NEW",
        "subject": "Studying for General -- 13 wpm code tips?",
        "body": (
            "Passed my Technician written last month (the 5 wpm code test "
            "was fine) and now I am aiming for General. The 13 wpm code "
            "test has me nervous. I copy fine at 10 wpm but fall apart when "
            "the speed jumps. What worked for you? I have been copying "
            "W1AW code practice in the evenings. Should I just keep at it, "
            "or is there a trick to making the jump from 10 to 13? Any "
            "study guides worth buying for the General written?"
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-013",
        "section": "hamnet_license",
        "date": "12/13/88",
        "author": "N5VE",
        "subject": "ARRL/VEC exam session Saturday in Mesquite",
        "body": (
            "Reminder: the Dallas Amateur Radio Club is sponsoring an "
            "ARRL/VEC exam session this Saturday, December 17, at 9:00 AM "
            "at the Red Cross Building, 2300 McKinney Avenue in Dallas. All "
            "classes examined -- Novice, Technician, General, Advanced, "
            "Extra -- with code tests at 5, 13, and 20 wpm as required. "
            "Bring your current license (original and copy), photo ID, and "
            "the $4.50 fee. Walk-ins welcome. Talk-in on 146.88. If you have "
            "been studying, this is your chance before the holidays!"
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-014",
        "section": "hamnet_arrl",
        "date": "12/14/88",
        "author": "W5ARL",
        "subject": "W1AW bulletin and code practice schedule",
        "body": (
            "For the newcomers: W1AW, the ARRL headquarters station, sends "
            "code practice every weekday evening and bulletins several "
            "times a day. Code practice runs at 9 PM Eastern on 3.58, 7.08, "
            "14.07, 21.07, and 28.07 MHz, starting slow and working up to "
            "35 wpm. Bulletins go out on CW, RTTY, and phone. It is the best "
            "free code practice there is -- I went from 5 to 13 wpm in four "
            "months copying W1AW. Full schedule is in December QST."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-015",
        "section": "hamnet_swap",
        "date": "12/15/88",
        "author": "WB5OLD",
        "subject": "FS: Heathkit HW-101, works great",
        "body": (
            "For sale: Heathkit HW-101 HF transceiver, built from the kit in "
            "the late 70s and still going strong. Full 80-10 meter coverage, "
            "SSB and CW, puts out a solid 100 watts. New finals last year, "
            "fresh alignment, includes the original manual and a spare set "
            "of tubes. Asking $250. Local pickup in the Dallas area "
            "preferred -- this thing is heavy. Also have an HM-102 wattmeter "
            "for $30. Reply here or catch me on the Wednesday net."
        ),
        "parent": None,
    },
    {
        "content_id": "hamnet-1988-016",
        "section": "hamnet_swap",
        "date": "12/16/88",
        "author": "K9HT",
        "subject": "WTB: 2m handheld -- IC-2AT or FT-209RH",
        "body": (
            "Wanted: a 2-meter handheld in good working order. An Icom "
            "IC-2AT or Yaesu FT-209RH would be ideal, but I will consider "
            "other 2m HTs of similar vintage. Must transmit and receive "
            "cleanly; cosmetic wear is fine. I have cash or trade -- I can "
            "offer a Kantronics packet TNC (older single-port model) plus "
            "cash. Located in Chicago area but I will pay shipping for the "
            "right radio. Thanks! -- K9HT."
        ),
        "parent": None,
    },
]


def section_spec():
    """Return the expanded forum section spec for coordinator wiring."""
    return dict(SECTIONS)


def seed_posts():
    """Return a copy of the seed posts for forum seeding."""
    return [dict(post) for post in SEED_POSTS]


def upcoming_net(day=None):
    """Return a human-readable string naming the next scheduled net.

    ``day`` is a datetime.date; when omitted, the current simulation day
    (session time-capsule date, else CIS_SIMULATION_DATE, else the Dec-1988
    cycle) is used.
    """
    if day is None:
        from cis_dynamic import simulation_day
        day = simulation_day()
    best_delta, best_net = None, None
    for net in NETS:
        delta = (net["weekday"] - day.weekday()) % 7
        if best_delta is None or delta < best_delta:
            best_delta, best_net = delta, net
    net_date = day + timedelta(days=best_delta)
    if best_delta == 0:
        when = "tonight"
    elif best_delta == 1:
        when = "tomorrow"
    else:
        when = f"in {best_delta} days"
    return (
        f"Next net: {best_net['name']} -- {WEEKDAY_NAMES[best_net['weekday']]}, "
        f"{net_date.strftime('%B %d')}, {best_net['time']} ({when}). "
        f"{best_net['where']}. Net control: {best_net['net_control']}."
    )


def render_net_schedule():
    """Return a printable listing of all scheduled nets."""
    lines = ["SCHEDULED ON-AIR NETS", "=" * 22, ""]
    for net in NETS:
        lines.append(f"{net['name']}")
        lines.append(
            f"  {WEEKDAY_NAMES[net['weekday']]}s, {net['time']}"
        )
        lines.append(f"  Where: {net['where']}")
        lines.append(f"  Net control: {net['net_control']}")
        lines.append(f"  {net['description']}")
        lines.append("")
    lines.append("Both nets are also announced in the forum message areas.")
    return "\n".join(lines)


def render_bulletins():
    """Return a printable rendering of the ARRL-style bulletins."""
    lines = ["ARRL BULLETINS", "=" * 14, ""]
    for bulletin in ARRL_BULLETINS:
        lines.append(f"{bulletin['number']} -- {bulletin['title']}")
        lines.append(bulletin["date"])
        lines.append("")
        lines.append(bulletin["body"].rstrip())
        lines.append("")
        lines.append("-" * 40)
        lines.append("")
    return "\n".join(lines)


def run_hamnet_board(app):
    """Simple interactive viewer for nets and bulletins (for forum wiring)."""
    while True:
        print()
        print("AMATEUR RADIO FORUM -- Nets & Bulletins")
        print("1. Net schedule")
        print("2. Next net")
        print("3. ARRL bulletins")
        print("Q. Back")
        choice = input("Choice: ").strip().upper()
        if choice == "1":
            print()
            print(render_net_schedule())
        elif choice == "2":
            print()
            print(upcoming_net())
        elif choice == "3":
            print()
            print(render_bulletins())
        elif choice == "Q":
            return
        else:
            print("Please choose 1, 2, 3, or Q.")
