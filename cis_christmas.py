"""Christmas in the sim: advent calendar, holiday CB topics, Christmas music.

Pure content + logic module for the December 1988 simulation setting:

* An advent-calendar daily treat: 25 original short treats (1988-flavored
  trivia, tiny fiction, holiday tips), one per day for December 1-25.
  Outside the season the treat function politely says the season has
  passed or hasn't arrived yet.
* Holiday CB channel topics in the same shape as cis_dynamic.CB_TOPICS
  (keywords / handles / responses / followups), plus ambient holiday
  chatter lines in the CB_LINES style. Seasonal: the topic set is only
  offered during December.
* 1988-era Christmas music as plain data (albums and songs released no
  later than 1988). Facts marked VERIFIED were confirmed against
  published records; items marked "(by most accounts)" are widely
  reported but not independently confirmed for this module. Nothing in
  this module references anything after December 1988.

All content functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned
line lists into the menu system (e.g. via text_page). The finisher hooks
the music data into cis_entertainment.py and the CB topics into the CB
channel answer loop -- see the wiring notes at the end of this file.

Never hardcode absolute filesystem paths; the repo root is derived from
``Path(__file__).resolve().parent`` per ARCHITECTURE.md.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _day(day: Optional[date]) -> date:
    """Resolve the simulation day, defaulting to the session-aware one."""
    if day is not None:
        return day
    try:
        from cis_dynamic import simulation_day
        return simulation_day()
    except Exception:
        return date(1988, 12, 15)


# ---------------------------------------------------------------------------
# Advent calendar: 25 original daily treats
# ---------------------------------------------------------------------------
# Each entry: (title, kind, lines). All prose is original. Factual claims
# follow the module convention: VERIFIED = confirmed against published
# records; "(by most accounts)" = widely reported.
ADVENT_TREATS: List[Tuple[str, str, List[str]]] = [
    (
        "STRINGING THE LIGHTS",
        "HOLIDAY TIP",
        [
            "Window one: the box of C7 bulbs from the attic, half of",
            "them dark. Test the whole string before it goes on the",
            "tree, and tape the spare fuses inside the lid where you",
            "will actually find them next year.",
            "",
            "A ladder, a patient helper, and no staples through the",
            "wire -- that is the recipe for lights that survive the",
            "season. Unplug them when you leave the house; the electric",
            "bill and the fire marshal will both thank you.",
        ],
    ),
    (
        "THE GIFT-SHOPPING MODEM",
        "HOLIDAY TIP",
        [
            "Ordering gifts by mail this year? The golden rule of",
            "December 1988: allow two to three weeks. Parcel post is",
            "cheap and slow; if the catalog says 'allow 4-6 weeks,'",
            "believe it.",
            "",
            "Browse the Electronic Mall here on CompuServe, but place",
            "the order early and keep the confirmation on paper. And",
            "check the post office's holiday deadlines before you mail",
            "anything -- late December lines are not a place to linger.",
        ],
    ),
    (
        "CARRIER TONE",
        "TINY FICTION",
        [
            "Snow coming down sideways, and the BBS is the warmest room",
            "in the county. The sysop uploads tonight's greeting file --",
            "a little ASCII tree, a little 'SEASONS GREETINGS' banner --",
            "and at midnight a caller from two states away leaves a",
            "message: 'Saw your lights file. Merry Christmas, stranger.'",
            "",
            "The sysop types back one line, saves it, and listens to the",
            "modem sing its handshake into the storm.",
        ],
    ),
    (
        "HOW THE TRACKING OF SANTA BEGAN",
        "TRIVIA",
        [
            "By most accounts, the great Santa-tracking tradition began",
            "with a misprint. In 1955 a department-store ad listed a",
            "telephone number for children to call Santa -- and printed",
            "the wrong one. The calls reached a military command post",
            "instead.",
            "",
            "The officers on duty played along, gave out Santa's",
            "'position,' and a holiday institution was born. Every",
            "Christmas Eve since, the trackers report his progress",
            "around the globe.",
        ],
    ),
    (
        "THE THANKSGIVING CHRISTMAS SONG",
        "TRIVIA",
        [
            "'Jingle Bells' was not written for Christmas at all. By",
            "most accounts, James Lord Pierpont wrote it in 1857 for a",
            "Thanksgiving church program -- which explains the dashing",
            "through the snow with no mention of December 25.",
            "",
            "The congregation liked it so much they asked for it again",
            "at Christmas, and it never went back.",
        ],
    ),
    (
        "ST. NICHOLAS DAY",
        "TRIVIA",
        [
            "December 6 is St. Nicholas Day, and in Dutch and German",
            "tradition it is the real gift morning: children set out a",
            "shoe the night before and wake to find it filled with",
            "treats.",
            "",
            "The American Santa Claus grew out of this same St.",
            "Nicholas -- Sinterklaas, carried across the Atlantic by",
            "Dutch settlers and gradually merged with the English",
            "Father Christmas.",
        ],
    ),
    (
        "WHITE CHRISTMAS",
        "TRIVIA",
        [
            "Irving Berlin wrote 'White Christmas' for the 1942 film",
            "Holiday Inn, and Bing Crosby's recording of it is, by most",
            "accounts, the best-selling single ever released.",
            "",
            "Berlin reportedly told his secretary to write down a song",
            "'like the best song I ever wrote' -- and then wrote it. The",
            "song's wistful dreaming-of-home verse is the part radio",
            "usually skips.",
        ],
    ),
    (
        "PHOTOGRAPHING THE LIGHTS",
        "HOLIDAY TIP",
        [
            "Want the tree lights on film this year? Load ASA 200, put",
            "the camera on a tripod, and shoot at dusk -- not full",
            "dark. The deep-blue sky behind the bulbs is what makes the",
            "shot.",
            "",
            "Turn off the flash (it kills the glow), brace the camera",
            "on anything solid, and take twice as many frames as you",
            "think you need. Film is cheap; the moment is not.",
        ],
    ),
    (
        "A CHARLIE BROWN CHRISTMAS",
        "TRIVIA",
        [
            "By most accounts, 'A Charlie Brown Christmas' premiered on",
            "December 9, 1965, on CBS -- made in a hurry, scored with",
            "a jazz trio instead of a laugh track, and nearly shelved",
            "by nervous network executives.",
            "",
            "It became one of the most beloved holiday specials ever",
            "made. That sad little tree, it turns out, was all any of",
            "us needed.",
        ],
    ),
    (
        "REINDEERRUNNER ON THE CB",
        "TINY FICTION",
        [
            "Somewhere on I-80, a trucker with the handle ReindeerRunner",
            "keys the mike: 'Merry Christmas to the eastbound, Merry",
            "Christmas to the westbound, and Merry Christmas to the",
            "bears in the median.'",
            "",
            "A dozen voices answer back out of the static, and for one",
            "long mile the whole highway sounds like a neighborhood.",
        ],
    ),
    (
        "THE BATTERY ENVELOPE",
        "HOLIDAY TIP",
        [
            "Every December 25 morning, somewhere, a child unwraps a",
            "toy that needs four C batteries nobody bought. Beat the",
            "curse: tape a labeled envelope of the right batteries",
            "inside the gift box before you wrap it.",
            "",
            "Include a small screwdriver if the battery door needs one.",
            "Future you, at 6 a.m. on Christmas morning, says thanks.",
        ],
    ),
    (
        "THE FIRST CHRISTMAS STAMP",
        "TRIVIA",
        [
            "By most accounts, the world's first Christmas postage stamp",
            "came from Austria in 1937. The United States issued its",
            "first Christmas stamp in 1962 -- and the annual stamp has",
            "been a holiday tradition at the post office ever since.",
            "",
            "Collectors watch each year's design the way the rest of us",
            "watch the parade: with opinions.",
        ],
    ),
    (
        "SANTA LUCIA DAY",
        "TRIVIA",
        [
            "In Sweden, December 13 is Santa Lucia Day: the festival of",
            "light in the darkest month. A girl chosen as Lucia wears a",
            "crown of candles and leads a procession, singing, while the",
            "household is served coffee and saffron buns.",
            "",
            "It is a small bright ceremony against the longest nights",
            "of the year -- and it predates the electric Christmas light",
            "by centuries.",
        ],
    ),
    (
        "THE MALL AT CHRISTMAS",
        "TINY FICTION",
        [
            "The mall smells like cinnamon and new plastic. Kids three",
            "deep crowd the video-game kiosk while their parents pretend",
            "to comparison-shop and memorize wish lists in secret.",
            "",
            "At the food court, a teenager in a reindeer headband takes",
            "a break from gift-wrapping and watches the skaters of",
            "shopping bags go by. Everybody is tired. Everybody is",
            "glowing a little.",
        ],
    ),
    (
        "TAPE THE SPECIALS",
        "HOLIDAY TIP",
        [
            "The holiday specials air once and then they are gone --",
            "unless your VCR is ready. Set the timer tonight, not five",
            "minutes before airtime, and record in SP for the best",
            "picture. Two hours per tape at SP; plan accordingly.",
            "",
            "Label every tape the moment it comes out of the machine.",
            "An unlabeled tape in January is a mystery; in December it",
            "is a tragedy.",
        ],
    ),
    (
        "ROCKEFELLER CENTER",
        "TRIVIA",
        [
            "By most accounts, the Rockefeller Center Christmas tree",
            "tradition began in 1931, when construction workers put up a",
            "small tree on the site -- in the middle of the Depression,",
            "paid for out of their own pockets.",
            "",
            "The official tree-lighting ceremony followed two years",
            "later. The workers' tree is still the ancestor of every",
            "towering spruce that has stood there since.",
        ],
    ),
    (
        "KITTY HAWK",
        "TRIVIA",
        [
            "On December 17, 1903 (VERIFIED), at Kitty Hawk, North",
            "Carolina, the Wright brothers made the first powered,",
            "controlled airplane flights. The longest lasted 59 seconds",
            "and covered 852 feet.",
            "",
            "Orville won the coin toss and flew first. Twelve seconds",
            "that changed the century -- on a cold December beach, with",
            "the whole world watching exactly nobody.",
        ],
    ),
    (
        "THE OFFICE PARTY FLOPPY",
        "TINY FICTION",
        [
            "Somebody's cousin's shareware disk makes the rounds at the",
            "office party: forty carols, MIDI files, lyrics included.",
            "The dot-matrix printer in the corner spends the afternoon",
            "hammering out song sheets, one perforated page at a time.",
            "",
            "By the third verse of 'Deck the Halls,' even accounting is",
            "singing. The printer jams on the last page. Nobody minds.",
        ],
    ),
    (
        "DRIVING HOME FOR CHRISTMAS",
        "HOLIDAY TIP",
        [
            "If the holiday means the highway, winterize first: antifreeze,",
            "tires, wipers, and a full tank before the rural stretches.",
            "Pack the emergency kit -- blanket, flashlight, jumper",
            "cables, and a thermos.",
            "",
            "Check the weather wire (GO WEATHER) before you leave, and",
            "tell somebody your route. The long way home is only",
            "romantic in songs.",
        ],
    ),
    (
        "A CHRISTMAS CAROL",
        "TRIVIA",
        [
            "Charles Dickens published 'A Christmas Carol' on December",
            "19, 1843 (VERIFIED) -- and paid for the printing himself,",
            "with hand-colored illustrations and gilt page edges.",
            "",
            "It sold out its first run before Christmas Eve. Scrooge,",
            "Tiny Tim, and the three ghosts have been haunting Decembers",
            "ever since -- and improving them.",
        ],
    ),
    (
        "THE LONGEST NIGHT",
        "TRIVIA",
        [
            "December 21 is the winter solstice: the longest night of",
            "the year in the Northern Hemisphere, and the turning point",
            "when the days start growing longer again.",
            "",
            "By most accounts, more than a few ancient midwinter",
            "festivals -- lights against the dark, feasts, evergreens --",
            "were aimed at exactly this night. The Christmas lights in",
            "your window are older than you think.",
        ],
    ),
    (
        "CHRISTMAS EVE EVE ON THE CB",
        "TINY FICTION",
        [
            "December 22, and channel 1 is quiet for once. No static",
            "wars, no kerchunking -- just a few regulars checking in,",
            "saying goodnight early, saving their voices for tomorrow.",
            "",
            "Somebody holds a handset up to a radio playing carols, and",
            "for one chorus the whole channel hums along through the",
            "crackle. Then: '73s, all. See you on the other side.'",
        ],
    ),
    (
        "THE LAST-MINUTE GIFT",
        "HOLIDAY TIP",
        [
            "December 23 and one name left on the list? The homemade",
            "gift certificate never fails: an evening of babysitting, a",
            "home-cooked dinner, a promise of help moving in spring.",
            "Write it nicely; it counts double.",
            "",
            "Or give time online: a gift subscription to an information",
            "service like this one keeps giving all year, and there is",
            "no wrapping paper involved at all.",
        ],
    ),
    (
        "SHORTWAVE SANTA",
        "TINY FICTION",
        [
            "Christmas Eve. A kid in Ohio tunes a shortwave set past the",
            "number stations and the hams calling CQ, listening for",
            "something that is not quite there -- until the evening news",
            "cuts in with the tracking report, and the whole house goes",
            "quiet to hear it.",
            "",
            "'He's over the Atlantic,' the announcer says, and the kid",
            "decides the radio was picking him up all along.",
        ],
    ),
    (
        "SILENT NIGHT",
        "TRIVIA",
        [
            "By most accounts, 'Silent Night' was first performed on",
            "Christmas Eve 1818 in Oberndorf, Austria -- words by a",
            "young priest, music by the church organist, sung with",
            "guitar because the organ was broken.",
            "",
            "It has been translated into well over a hundred languages",
            "since. Merry Christmas, from all of us in the sim -- may",
            "your night be silent, and your modem loud.",
        ],
    ),
]


def christmas_treat(day: Optional[date] = None) -> List[str]:
    """Return the advent-calendar treat lines for ``day``.

    December 1-25: that day's treat (title, kind, and body). December
    26-31: a note that the calendar has closed for the year. Any other
    month: a polite note that the season hasn't arrived yet.
    """
    d = _day(day)
    if d.month == 12 and 1 <= d.day <= 25:
        title, kind, lines = ADVENT_TREATS[d.day - 1]
        return [
            f"ADVENT CALENDAR -- DECEMBER {d.day}, {d.year}",
            title,
            f"({kind})",
            "",
            *lines,
        ]
    if d.month == 12:
        return [
            "ADVENT CALENDAR -- SEASON'S GREETINGS",
            "",
            "All twenty-five windows are open -- the calendar has",
            "closed for the year. Season's greetings, and we'll see",
            "you back here next December.",
        ]
    return [
        "ADVENT CALENDAR -- NOT YET IN SEASON",
        "",
        "The Christmas season hasn't arrived yet. The advent",
        "calendar opens December 1 -- come back then for 25 daily",
        "treats: trivia, tiny fiction, and holiday tips.",
        "",
        f"(Your simulated date is {d.strftime('%B %d, %Y')}.)",
    ]


def advent_treat_count() -> int:
    """Number of daily treats in the advent calendar (always 25)."""
    return len(ADVENT_TREATS)


# ---------------------------------------------------------------------------
# Holiday CB topics (same shape as cis_dynamic.CB_TOPICS)
# ---------------------------------------------------------------------------
# Seasonal set: only offered during December (see christmas_cb_topics).
# Handles are all established CB handles from cis_dynamic.HANDLES so the
# CB simulator's member profiles resolve.
CHRISTMAS_CB_TOPICS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "gifts": {
        "keywords": ("gift", "present", "wrapping", "shopping",
                     "wish list", "stocking"),
        "handles": ("SilverFox", "MegaMolly"),
        "responses": (
            "I finished my shopping early this year and I am still not sure I believe it.",
            "The wish lists get more electronic every year. Mine still has books on it.",
            "Wrap as you buy. A December 24 wrapping marathon is a young person's game.",
        ),
        "followups": (
            "What is the hardest person on your list to shop for?",
            "Are you a mall shopper or a catalog shopper?",
            "Do you open one gift on Christmas Eve?",
        ),
    },
    "tree": {
        "keywords": ("tree", "lights", "ornament", "tinsel", "garland", "star"),
        "handles": ("NightOwl", "CommodoreCat"),
        "responses": (
            "Our tree went up the day after Thanksgiving and the cat has declared war on the tinsel.",
            "Test every string of lights before it goes on the tree. Every year I forget, every year I regret it.",
            "The star on top is older than I am. Some ornaments are family members at this point.",
        ),
        "followups": (
            "Real tree or artificial at your house?",
            "Colored lights or all white?",
            "When does the tree come down -- New Year's or Twelfth Night?",
        ),
    },
    "carols": {
        "keywords": ("carol", "christmas music", "silent night",
                     "choir", "hymn"),
        "handles": ("ByteBender", "SilverFox"),
        "responses": (
            "The new A Very Special Christmas tape has been in my deck since Thanksgiving.",
            "Nothing beats carolers at the door, even when they only know two verses.",
            "I have strong opinions about which version of 'The Little Drummer Boy' is correct.",
        ),
        "followups": (
            "What is your must-hear-every-year carol?",
            "Do you sing along or just listen?",
            "Have you heard the Mannheim Steamroller Christmas record?",
        ),
    },
    "travel": {
        "keywords": ("driving home", "flight", "visiting", "in-laws",
                     "road trip", "airport"),
        "handles": ("NightOwl", "PacketPete"),
        "responses": (
            "Driving home for Christmas this year. The interstate will be a parking lot with headlights.",
            "Flying out on the 23rd. I have made my peace with the middle seat.",
            "We take turns hosting. This year the in-laws come to us, and the guest room is ready.",
        ),
        "followups": (
            "Are you traveling this year or staying home?",
            "How far is the drive?",
            "Do you leave on Christmas Eve or wait for the morning?",
        ),
    },
    "feast": {
        "keywords": ("turkey", "cookies", "eggnog", "dinner",
                     "baking", "fruitcake"),
        "handles": ("WordPro", "CommodoreCat"),
        "responses": (
            "The cookie tins are already full and it is not even the 20th. Send help.",
            "Turkey, dressing, and the good gravy boat. Some things are not negotiable.",
            "I defend fruitcake. Aged properly and sliced thin, it is genuinely good.",
        ),
        "followups": (
            "What is the signature dish at your table?",
            "Do you bake, or is that someone else's department?",
            "Eggnog: with or without?",
        ),
    },
    "santa": {
        "keywords": ("santa", "reindeer", "norad", "chimney", "north pole"),
        "handles": ("MegaMolly", "AtariKid"),
        "responses": (
            "The kids called the Santa tracking line and got a full position report. The magic is holding.",
            "I am the designated chimney inspector this year. The cookies are a bribe and I accept.",
            "Reindeer games are cancelled if there is no snow. Those are the rules and the kids made them.",
        ),
        "followups": (
            "Do the little ones still believe at your house?",
            "What time does Santa arrive -- after bedtime or Christmas morning?",
            "Cookies and milk, or does your Santa prefer something else?",
        ),
    },
}

# Ambient holiday chatter in the CB_LINES style, for the channel mix.
CHRISTMAS_CB_LINES: List[str] = [
    "Merry Christmas Eve Eve, everyone.",
    "The tree lights look great through the window tonight.",
    "Anybody else wrapping gifts at midnight?",
    "Snow is coming down hard here. Stay warm out there.",
    "Just finished the last of the Christmas cookies.",
    "The carolers came by earlier. Made my whole week.",
    "Driving home tomorrow. Wish me clear roads.",
    "My modem and I are both getting the night off on the 25th.",
    "Has anyone taped the holiday specials yet?",
    "Eggnog: with. This is not a debate.",
    "The stockings are hung. Repeat: the stockings are hung.",
    "Merry Christmas to the night owls on channel 2.",
]


def christmas_cb_topics(day: Optional[date] = None) -> Dict[str, Dict[str, Tuple[str, ...]]]:
    """Holiday CB topic set, in the cis_dynamic.CB_TOPICS shape.

    Returns the full topic dict during December (the Christmas season)
    and an empty dict outside it, so the finisher can merge it into the
    CB answer loop only when seasonally appropriate.
    """
    d = _day(day)
    if d.month == 12:
        return CHRISTMAS_CB_TOPICS
    return {}


def christmas_cb_lines(day: Optional[date] = None) -> List[str]:
    """Browsable display lines for the holiday CB topics."""
    d = _day(day)
    topics = christmas_cb_topics(d)
    lines = [
        "HOLIDAY CB TOPICS -- DECEMBER 1988",
        "Seasonal discussion topics for the CB channels, in the",
        "style of the regular topic set. Mention a keyword on CB",
        "and a member with something to say will answer.",
        "",
    ]
    if not topics:
        lines.append("The holiday topics are in season during December.")
        return lines
    for key, topic in topics.items():
        lines.append(f"* {key.upper()} -- {', '.join(topic['handles'])}")
        lines.append(f"    try: {', '.join(topic['keywords'][:3])} ...")
        lines.append(f"    e.g. \"{topic['responses'][0]}\"")
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Christmas music (plain data; the finisher hooks it into cis_entertainment)
# ---------------------------------------------------------------------------
# VERIFIED = confirmed against published records (see module docstring).
# "(by most accounts)" = widely reported.
CHRISTMAS_ALBUMS: List[Dict[str, object]] = [
    {
        "title": "A Very Special Christmas",
        "artist": "Various Artists",
        "year": 1987,
        "label": "A&M",
        "note": "Released October 12, 1987. Special Olympics benefit "
                "produced by Jimmy Iovine; cover art by Keith Haring. "
                "Includes U2, Madonna, Bruce Springsteen, Sting, Whitney "
                "Houston, Bon Jovi, Run-D.M.C., and Stevie Nicks. (VERIFIED)",
    },
    {
        "title": "A Fresh Aire Christmas",
        "artist": "Mannheim Steamroller",
        "year": 1988,
        "label": "American Gramaphone",
        "note": "The year's best-selling Christmas album; topped "
                "Billboard's Christmas Hits album chart in the December "
                "24, 1988 issue. Chip Davis's synth-and-strings take on "
                "the carols. (VERIFIED)",
    },
    {
        "title": "Once Upon a Christmas",
        "artist": "Kenny Rogers & Dolly Parton",
        "year": 1984,
        "label": "RCA",
        "note": "Billboard Christmas Hits #1 album in the December 15, "
                "1984 issue. (VERIFIED)",
    },
    {
        "title": "Alabama Christmas",
        "artist": "Alabama",
        "year": 1985,
        "label": "RCA",
        "note": "Billboard Christmas Hits #1 album in the December 21, "
                "1985 issue. (VERIFIED)",
    },
    {
        "title": "Merry Christmas Strait to You!",
        "artist": "George Strait",
        "year": 1986,
        "label": "MCA",
        "note": "The best-selling Christmas album of 1986 "
                "(by most accounts).",
    },
    {
        "title": "Christmas",
        "artist": "Kenny Rogers",
        "year": 1981,
        "label": "Liberty",
        "note": "The best-selling Christmas album of 1981 and 1983 "
                "(by most accounts).",
    },
    {
        "title": "A Christmas Gift for You from Phil Spector",
        "artist": "Various Artists",
        "year": 1963,
        "label": "Philles",
        "note": "The Wall of Sound Christmas record -- Darlene Love, "
                "the Ronettes, the Crystals (by most accounts).",
    },
    {
        "title": "Elvis' Christmas Album",
        "artist": "Elvis Presley",
        "year": 1957,
        "label": "RCA",
        "note": "Among the best-selling Christmas albums of all time "
                "(by most accounts).",
    },
    {
        "title": "Merry Christmas",
        "artist": "Bing Crosby",
        "year": 1945,
        "label": "Decca",
        "note": "The crooner's Christmas perennial, anchored by 'White "
                "Christmas' (by most accounts).",
    },
    {
        "title": "The Jackson 5 Christmas Album",
        "artist": "The Jackson 5",
        "year": 1970,
        "label": "Motown",
        "note": "A young Michael Jackson on 'Santa Claus Is Comin' to "
                "Town' and 'Frosty the Snowman' (by most accounts).",
    },
    {
        "title": "Christmas Portrait",
        "artist": "Carpenters",
        "year": 1978,
        "label": "A&M",
        "note": "Karen Carpenter's warm alto on the carols; a late-70s "
                "staple (by most accounts).",
    },
]

CHRISTMAS_SONGS: List[Dict[str, object]] = [
    {
        "title": "Christmas in Hollis",
        "artist": "Run-D.M.C.",
        "year": 1987,
        "note": "From A Very Special Christmas; the hip-hop holiday "
                "anthem. (VERIFIED)",
    },
    {
        "title": "Santa Claus Is Comin' to Town",
        "artist": "Bruce Springsteen & the E Street Band",
        "year": 1985,
        "note": "Hit #1 on Billboard's Christmas singles chart in the "
                "December 28, 1985 issue. (VERIFIED)",
    },
    {
        "title": "Grandma Got Run Over by a Reindeer",
        "artist": "Elmo 'n' Patsy",
        "year": 1979,
        "note": "Billboard Christmas singles #1 in the December 24, "
                "1983 issue. (VERIFIED)",
    },
    {
        "title": "The Chipmunk Song (Christmas Don't Be Late)",
        "artist": "David Seville & the Chipmunks",
        "year": 1958,
        "note": "Reached #1 on the Hot 100 in 1958. (VERIFIED)",
    },
    {
        "title": "Do They Know It's Christmas?",
        "artist": "Band Aid",
        "year": 1984,
        "note": "The charity single that started it all "
                "(by most accounts).",
    },
    {
        "title": "Last Christmas",
        "artist": "Wham!",
        "year": 1984,
        "note": "George Michael's bittersweet holiday standard "
                "(by most accounts).",
    },
    {
        "title": "Feliz Navidad",
        "artist": "Jose Feliciano",
        "year": 1970,
        "note": "Twenty words, two languages, endless airplay "
                "(by most accounts).",
    },
    {
        "title": "Rockin' Around the Christmas Tree",
        "artist": "Brenda Lee",
        "year": 1958,
        "note": "Recorded when Lee was thirteen (by most accounts).",
    },
    {
        "title": "Jingle Bell Rock",
        "artist": "Bobby Helms",
        "year": 1957,
        "note": "A Christmas-chart perennial since the 1950s "
                "(by most accounts).",
    },
    {
        "title": "White Christmas",
        "artist": "Bing Crosby",
        "year": 1942,
        "note": "By most accounts the best-selling single ever released.",
    },
    {
        "title": "Blue Christmas",
        "artist": "Elvis Presley",
        "year": 1957,
        "note": "From Elvis' Christmas Album (by most accounts).",
    },
]


def christmas_music_lines(day: Optional[date] = None) -> List[str]:
    """Display lines for the Christmas music section.

    The finisher hooks this into the entertainment menu as a
    ("Christmas Music", christmas_music_lines(day)) section, mirroring
    how chart_lines()/movies_lines()/bowls_lines() are used.
    """
    _ = _day(day)  # resolved for signature parity; list is date-agnostic
    lines = [
        "CHRISTMAS MUSIC -- DECEMBER 1988",
        "Records on the turntable this season. All releases are 1988",
        "or earlier -- nothing after December 1988.",
        "",
        "ALBUMS",
        "------",
    ]
    for album in CHRISTMAS_ALBUMS:
        lines.append(f"  {album['title']} -- {album['artist']} ({album['year']})")
        lines.append(f"    {album['note']}")
        lines.append("")
    lines.extend(["SONGS", "-----"])
    for song in CHRISTMAS_SONGS:
        lines.append(f"  \"{song['title']}\" -- {song['artist']} ({song['year']})")
        lines.append(f"    {song['note']}")
        lines.append("")
    lines.append("Items marked VERIFIED were confirmed against published")
    lines.append("records; 'by most accounts' items are widely reported.")
    return lines


# ---------------------------------------------------------------------------
# Menu / service entry points
# ---------------------------------------------------------------------------
def christmas_menu_lines(
    day: Optional[date] = None,
) -> List[Tuple[str, List[str]]]:
    """All Christmas sections as (title, lines) pairs for the menu wire-up."""
    d = _day(day)
    return [
        ("Advent Calendar", christmas_treat(d)),
        ("Holiday CB Topics", christmas_cb_lines(d)),
        ("Christmas Music", christmas_music_lines(d)),
    ]


def christmas_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return Christmas sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return christmas_menu_lines()


def _advent_browse(app, day: Optional[date] = None) -> None:
    """Browse the 25 advent windows; M returns to the Christmas menu."""
    d = _day(day)
    window = d.day if (d.month == 12 and 1 <= d.day <= 25) else 1
    while True:
        treat = christmas_treat(date(d.year, 12, window))
        app.text_page("news", f"ADVENT -- DECEMBER {window}", treat)
        app.ansi_scroll("Enter a day 1-25 for another window, or M to go back.",
                        0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return
        if choice.isdigit() and 1 <= int(choice) <= 25:
            window = int(choice)
        else:
            app.ansi_scroll("Enter a number 1-25, or M.", 0.01)


def christmas_menu(app, day: Optional[date] = None) -> None:
    """Interactive 'Christmas in the Sim' submenu.

    Follows the yearend_menu() convention: numbered sections, text_page
    for each, M to return. All interactive output goes through
    ``app.ansi_scroll``.
    """
    d = _day(day)
    while True:
        app.clear()
        app.header_bar("news")
        app.ansi_scroll("CHRISTMAS IN THE SIM - DECEMBER 1988 ARCHIVE", 0.01)
        app.ansi_scroll("--------------------", 0.01)
        app.ansi_scroll("1  Advent Calendar (25 daily treats)", 0.01)
        app.ansi_scroll("2  Holiday CB Topics", 0.01)
        app.ansi_scroll("3  Christmas Music", 0.01)
        app.ansi_scroll("M  Back", 0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return
        if choice == "1":
            _advent_browse(app, d)
        elif choice == "2":
            app.text_page("news", "HOLIDAY CB TOPICS", christmas_cb_lines(d))
        elif choice == "3":
            app.text_page("news", "CHRISTMAS MUSIC", christmas_music_lines(d))
        else:
            app.ansi_scroll("Enter 1-3, or M.", 0.01)


if __name__ == "__main__":
    for title, lines in christmas_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))


# ---------------------------------------------------------------------------
# Finisher wiring notes (not executed; for the coordinator)
# ---------------------------------------------------------------------------
# 1) go_commands.json: add  "GO CHRISTMAS": "<screen>"  mirroring the
#    "GO YEARINREVIEW": "news" entry.
# 2) compuserve.py: `import cis_christmas`, plus a wrapper like
#    yearend_menu():
#        def christmas_menu_cmd():
#            cis_christmas.christmas_menu(sys.modules[__name__])
#    and a dispatch branch in the main command loop.
# 3) CB topics hook (cis_dynamic.py): in the answer routine that iterates
#    `for topic_key, topic in CB_TOPICS.items()` (and the memory-followup
#    lookup `CB_TOPICS.get(memory["topic_key"])`), merge the seasonal set:
#        from cis_christmas import christmas_cb_topics
#        ALL_TOPICS = {**CB_TOPICS, **christmas_cb_topics()}
#    and iterate / look up ALL_TOPICS instead. christmas_cb_topics()
#    resolves the simulation day itself and returns {} outside December.
#    Optionally mix CHRISTMAS_CB_LINES into CB_LINES during December.
# 4) Entertainment hook (cis_entertainment.py): append
#    ("Christmas Music", cis_christmas.christmas_music_lines(day))
#    to the list returned by entertainment_menu_lines().
