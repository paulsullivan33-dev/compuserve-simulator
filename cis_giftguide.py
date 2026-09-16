"""1988 Holiday Shopping Guide news special for the December 1988 setting.

Pure content + logic module: a News Services holiday special covering the
hottest Christmas 1988 gifts, catalog-vs.-mall shopping, toy shortages,
and gift trends -- plus an interactive gift picker that suggests
era-appropriate presents by budget and recipient.

All content functions accept an optional ``day`` parameter defaulting to
``cis_dynamic.simulation_day()``; the coordinator wires the returned line
lists into the menu system (e.g. via text_page). All review text and
framing is original; only historical facts (product names, release dates,
verifiable prices) are real.

Price/date flags: facts marked VERIFIED were confirmed against published
records; items marked "(by most accounts)" are widely reported but not
independently confirmed for this module; prices marked "(est.)" are
period-plausible estimates and are labeled as such. Nothing in this
module references anything after December 1988.

The interactive gift picker emits ALL output through ``app.ansi_scroll``
-- never bare print().
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple


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
# Gift catalog (used by the interactive gift picker)
# ---------------------------------------------------------------------------
# Every price_note carries exactly one of the flags VERIFIED,
# "(by most accounts)" or "(est.)" so readers know what is confirmed and
# what is estimated. ``price`` is a representative 1988 dollar figure
# used for budget filtering only.
@dataclass(frozen=True)
class Gift:
    name: str
    price: float
    price_note: str
    recipients: Tuple[str, ...]  # any of "kid", "teen", "adult"
    blurb: str


GIFT_CATALOG: List[Gift] = [
    Gift(
        "Nintendo Entertainment System (Action Set)", 149.99,
        "~$150 (by most accounts)", ("kid", "teen"),
        "The console under more trees than any other this year: two "
        "controllers, the light gun, and two games in the box.",
    ),
    Gift(
        "Super Mario Bros. 2 (NES cartridge)", 49.99,
        "~$50 (est.)", ("kid", "teen"),
        "Released in North America October 9, 1988 (VERIFIED) -- the "
        "sequel every NES owner is asking Santa for.",
    ),
    Gift(
        "Zelda II: The Adventure of Link (NES)", 49.99,
        "~$50 (est.)", ("kid", "teen"),
        "Released in North America December 1, 1988 (VERIFIED) in the "
        "famous gold cartridge. Brand-new under the tree.",
    ),
    Gift(
        "Teenage Mutant Ninja Turtles action figure", 5.99,
        "~$6 each (est.)", ("kid", "teen"),
        "Playmates' first series hit shelves in summer 1988 (VERIFIED). "
        "Collect all four turtles -- pizza not included.",
    ),
    Gift(
        "Cabbage Patch Kid doll", 24.99,
        "~$25 (est.)", ("kid",),
        "The craze that caused the 1983 Christmas riots (VERIFIED). "
        "Coleco collapsed in 1988; the line now ships under new "
        "ownership (by most accounts).",
    ),
    Gift(
        "My Little Pony", 7.99,
        "~$8 (est.)", ("kid",),
        "Brushable manes, pastel colors, and a different pony for every "
        "stocking. A perennial on wish lists.",
    ),
    Gift(
        "Transformers figure", 12.99,
        "$9.95-$20.99 (VERIFIED 1984 list)", ("kid",),
        "More than meets the eye -- and still morphing strong five "
        "years after the line's debut Christmas.",
    ),
    Gift(
        "Teddy Ruxpin", 69.99,
        "$69.99 (VERIFIED 1985 list)", ("kid",),
        "The talking bear that read bedtime stories from cassettes. "
        "Tapes and books sold separately, then as now.",
    ),
    Gift(
        "Micro Machines playset", 9.99,
        "~$10 (est.)", ("kid",),
        "If it doesn't say Micro Machines, it's not the real thing. "
        "Pocket-size cars that swallow whole afternoons.",
    ),
    Gift(
        "Barbie doll", 9.99,
        "~$10 (est.)", ("kid",),
        "Still the best-selling fashion doll in America, with a Dream "
        "House's worth of accessories to grow the gift.",
    ),
    Gift(
        "Koosh Ball", 4.99,
        "~$5 (by most accounts)", ("kid", "teen"),
        "Last year's surprise hit -- a rubber-band ball that begs to be "
        "tossed around the living room. Cheap and indestructible.",
    ),
    Gift(
        "Nintendo Power (1-year subscription)", 15.00,
        "~$15 (est.)", ("kid", "teen"),
        "Nintendo's own magazine; the first issue shipped July/August "
        "1988 (by most accounts). Maps, tips, and posters monthly.",
    ),
    Gift(
        "Pictionary", 24.99,
        "~$25 (est.)", ("kid", "teen", "adult"),
        "The draw-and-guess party game that turns quiet relatives into "
        "shouting artists. A family-night guarantee.",
    ),
    Gift(
        "Sony Walkman", 49.99,
        "~$50 (est.)", ("teen", "adult"),
        "Personal stereo, still the badge of teenage independence. "
        "Batteries not included -- buy the 4-pack.",
    ),
    Gift(
        "Boombox", 99.99,
        "~$100 (est.)", ("teen",),
        "Dual cassette decks for high-speed dubbing, detachable "
        "speakers, and enough bass to annoy the neighbors.",
    ),
    Gift(
        "Swatch watch", 39.99,
        "~$40 (est.)", ("teen", "adult"),
        "The Swiss plastic fashion watch -- collectible colors, "
        "unmistakable tick, and a wrist that says 1988.",
    ),
    Gift(
        "Lazer Tag set (Worlds of Wonder)", 39.99,
        "~$40 (est.)", ("teen",),
        "Infrared tag for the backyard after dark. The vest sensors "
        "make every game feel like prime time.",
    ),
    Gift(
        "Trivial Pursuit (Genus edition)", 29.99,
        "~$30 (est.)", ("teen", "adult"),
        "Six wedges of trivia glory. Settle once and for all who in "
        "the family actually paid attention in school.",
    ),
    Gift(
        "'Faith' -- George Michael (cassette)", 8.99,
        "~$9 (est.)", ("teen", "adult"),
        "By most accounts the year's biggest record -- the safe pick "
        "for any stocking with a tape deck nearby.",
    ),
    Gift(
        "Compact disc player", 199.99,
        "~$200 (est.)", ("adult",),
        "Skips the pops and hisses of vinyl. The future of music, in "
        "a box slightly larger than a toaster.",
    ),
    Gift(
        "VCR", 249.99,
        "~$250 (est.)", ("adult",),
        "Time-shift the holiday specials and finally settle the "
        "Beta-vs.-VHS debate: VHS won (by most accounts).",
    ),
    Gift(
        "Camcorder", 799.99,
        "~$800 (est.)", ("adult",),
        "The splurge gift: capture Christmas morning on tape and "
        "replay it every year until the tape wears out.",
    ),
    Gift(
        "Cordless telephone", 79.99,
        "~$80 (est.)", ("adult",),
        "Take the call to the kitchen, the den, or the driveway. "
        "Range: to the end of the block, weather permitting.",
    ),
    Gift(
        "Telephone answering machine", 59.99,
        "~$60 (est.)", ("adult",),
        "Never miss a call again. The outgoing message is half the "
        "fun -- and entirely the recipient's problem.",
    ),
    Gift(
        "Filofax personal organizer", 49.99,
        "~$50 (est.)", ("adult",),
        "The yuppie status symbol: leather binder, diary inserts, and "
        "the unmistakable rustle of importance.",
    ),
    Gift(
        "'Giorgio' Beverly Hills perfume", 39.99,
        "~$40 (est.)", ("adult",),
        "The scent of the eighties in the yellow-and-white striped "
        "box. Instantly recognizable across a crowded room.",
    ),
    Gift(
        "Cuisinart food processor", 149.99,
        "~$150 (est.)", ("adult",),
        "For the cook who has everything except eleven discs of "
        "slicing, shredding, and chopping power.",
    ),
    Gift(
        "Microwave oven", 199.99,
        "~$200 (est.)", ("adult",),
        "Reheat the leftovers in minutes. By 1988 the microwave has "
        "gone from gadget to kitchen standard (by most accounts).",
    ),
    Gift(
        "Service Merchandise gift certificate", 25.00,
        "~$25 (est.)", ("adult",),
        "For the impossible-to-shop-for: a slip of paper redeemable "
        "at the catalog-showroom counter for anything in the book.",
    ),
]


def pick_gifts(
    budget: float,
    recipient: str,
    day: Optional[date] = None,
) -> List[Gift]:
    """Suggest gifts for a recipient within a budget.

    Pure logic (no I/O): returns up to five catalog gifts tagged for
    ``recipient`` ("kid", "teen", or "adult") priced at or under
    ``budget``, best (priciest) fit first. Returns an empty list when
    nothing fits or the recipient is unknown.
    """
    _ = _day(day)  # Catalog is December 1988 throughout; kept for signature.
    recipient = recipient.strip().lower()
    if recipient not in ("kid", "teen", "adult") or budget <= 0:
        return []
    matches = [
        g for g in GIFT_CATALOG
        if recipient in g.recipients and g.price <= budget
    ]
    matches.sort(key=lambda g: g.price, reverse=True)
    return matches[:5]


def cheapest_for(recipient: str) -> List[Gift]:
    """Cheapest three gifts for a recipient (the 'stretch' fallback)."""
    recipient = recipient.strip().lower()
    matches = [g for g in GIFT_CATALOG if recipient in g.recipients]
    matches.sort(key=lambda g: g.price)
    return matches[:3]


# ---------------------------------------------------------------------------
# Content sections (each returns a list of display lines)
# ---------------------------------------------------------------------------
def hottest_lines(day: Optional[date] = None) -> List[str]:
    """The hottest Christmas 1988 gifts, wire-service shopping desk."""
    _ = _day(day)  # Retrospective of the season; no gating.
    return [
        "THE HOTTEST GIFTS OF CHRISTMAS 1988",
        "CompuServe Shopping Desk -- prices as marked",
        "",
        " 1. NINTENDO ENTERTAINMENT SYSTEM -- ~$90-$150 (by most",
        "    accounts). About $90 for the bare console, ~$100 bundled",
        "    with Super Mario Bros., ~$150 for the Action Set with two",
        "    games and an extra controller. The gift of the year.",
        "",
        " 2. TEENAGE MUTANT NINJA TURTLES figures -- ~$6 each (est.).",
        "    Playmates' first series hit shelves in summer 1988",
        "    (VERIFIED). Cowabunga is now a household word.",
        "",
        " 3. CABBAGE PATCH KIDS -- ~$25 (est.). The 1983 riots are",
        "    history (VERIFIED); Coleco collapsed in 1988 (VERIFIED),",
        "    and the line ships under new ownership (by most accounts).",
        "",
        " 4. SUPER MARIO BROS. 2 (NES) -- ~$50 (est.). Released in",
        "    North America October 9, 1988 (VERIFIED). The sequel every",
        "    NES owner has circled in the catalog.",
        "",
        " 5. ZELDA II: THE ADVENTURE OF LINK (NES) -- ~$50 (est.).",
        "    Released in North America December 1, 1988 (VERIFIED) in",
        "    the gold cartridge. Fresh off the truck.",
        "",
        " 6. TEDDY RUXPIN -- $69.99 (VERIFIED 1985 list). The talking",
        "    bear still tells bedtime stories from cassettes; tapes",
        "    and books sold separately.",
        "",
        " 7. NINTENDO POWER subscription -- ~$15 a year (est.).",
        "    Nintendo's own magazine; the first issue shipped",
        "    July/August 1988 (by most accounts).",
        "",
        " 8. MICRO MACHINES -- ~$5-$20 (est.). Pocket-size cars and",
        "    playsets. If it doesn't say Micro Machines, it's not the",
        "    real thing.",
        "",
        " 9. PICTIONARY -- ~$25 (est.). The draw-and-guess party game",
        "    turning quiet relatives into shouting artists.",
        "",
        "10. KOOSH BALL -- ~$5 (by most accounts). Last year's",
        "    surprise hit; a rubber-band ball that begs to be tossed.",
        "",
        "Price key: VERIFIED = confirmed against published records;",
        "by most accounts = widely reported; est. = period-plausible",
        "estimate.",
    ]


def catalog_vs_mall_lines(day: Optional[date] = None) -> List[str]:
    """Catalog vs. mall shopping in December 1988."""
    _ = _day(day)  # Season retrospective; no gating.
    return [
        "CATALOG VS. MALL: HOW AMERICA SHOPS FOR CHRISTMAS",
        "",
        "THE WISH BOOK -- Every December, the Sears Christmas catalog",
        "lands with a thud and becomes the most-read book in the house.",
        "Kids circle pages in crayon; parents study the order form like",
        "a tax return. JCPenney and Montgomery Ward publish their own",
        "Christmas catalogs, and Spiegel serves the well-heeled by mail.",
        "",
        "THE CATALOG SHOWROOM -- Service Merchandise perfected the",
        "hybrid: browse the catalog in the store, write the item number",
        "on a slip, pay up front, and wait by the pickup counter while",
        "your treasure rides the conveyor belt from the stockroom.",
        "",
        "THE TOY WAREHOUSE -- Toys 'R' Us turned toy shopping into a",
        "safari through aisle after aisle of boxes, with the giraffe",
        "mascot grinning down from the sign. Bring a cart. Bring two.",
        "",
        "THE MALL -- Santa holds court for photos, carols play on an",
        "endless loop, and the Orange Julius stand does land-office",
        "business. Mall hours stretch later every December, and the",
        "parking lot is a contact sport.",
        "",
        "ORDERING BY PHONE -- Toll-free 1-800 numbers in the back of",
        "every catalog take your order with a credit card. Order by",
        "mid-December (by most accounts) and the truck still beats",
        "Santa to your door.",
    ]


def shortages_lines(day: Optional[date] = None) -> List[str]:
    """Toy shortages and shelf-watch for the 1988 season."""
    d = _day(day)
    days_left = (date(1988, 12, 25) - d).days
    if days_left > 1:
        countdown = f"{days_left} shopping days until Christmas."
    elif days_left == 1:
        countdown = "1 shopping day until Christmas -- tomorrow is the big day."
    elif days_left == 0:
        countdown = "Christmas Day is here -- hope the layaway is paid off!"
    else:
        countdown = "Christmas has come and gone -- clearance season begins."
    return [
        "TOY SHORTAGES & SHELF WATCH",
        countdown,
        "",
        "DEJA VU -- Veterans of Christmas 1983 remember the Cabbage",
        "Patch riots, when parents literally fought over the dolls",
        "(VERIFIED). Nobody is throwing punches this year, but the",
        "pattern rhymes: the hot toy sells out, the phone starts",
        "ringing, and the desperate start calling stores two towns over.",
        "",
        "NINTENDO WATCH -- By most accounts, the NES Action Set is the",
        "item clerks get asked about most. Stores report selling out",
        "within days of each restock (by most accounts) -- if you see",
        "one on the shelf, do not walk away to 'think about it.'",
        "",
        "TURTLE WATCH -- Playmates' Teenage Mutant Ninja Turtles",
        "figures are flying off the pegs (by most accounts).",
        "Complete sets of all four turtles are the first to vanish.",
        "",
        "SURVIVAL TIPS --",
        "  * LAYAWAY is still big in 1988: put it on hold now, pay a",
        "    little each week, take it home paid in full.",
        "  * Ask for a RAIN CHECK when the sale item is gone.",
        "  * CALL AHEAD before driving across town for one toy.",
        "  * CATALOG ORDERING beats the crowds if you order early.",
        "  * The early bird gets the Turtle; the late bird gets the",
        "    IOU note in the stocking.",
    ]


def trends_lines(day: Optional[date] = None) -> List[str]:
    """Gift trends for Christmas 1988."""
    _ = _day(day)  # Season retrospective; no gating.
    return [
        "GIFT TRENDS FOR CHRISTMAS '88",
        "",
        "THE VIDEO-GAME CHRISTMAS -- Nintendo owns December. Super",
        "Mario Bros. 2 arrived October 9 (VERIFIED) and Zelda II",
        "followed December 1 (VERIFIED); by most accounts the sequel",
        "is selling by the millions. The NES is the gift other gifts",
        "are measured against.",
        "",
        "TURTLE POWER -- The cartoon went into production in December",
        "1987 (VERIFIED), the Playmates toys landed in summer 1988",
        "(VERIFIED), and now you can't swing a nunchuk without hitting",
        "turtle merchandise. Pizza sales, by most accounts, are up.",
        "",
        "ELECTRONICS GO MAINSTREAM -- CD players, camcorders, VCRs,",
        "cordless phones, and answering machines move from gadget",
        "counter to gift wrap. The future arrives with batteries not",
        "included.",
        "",
        "THE YUPPIE STOCKING -- Filofax organizers, Swatch watches,",
        "and appointment books for the briefcase crowd. Success now",
        "comes with accessories.",
        "",
        "BOARD-GAME NIGHTS -- Pictionary and Trivial Pursuit turn the",
        "living room into a game show. The gift that gets unwrapped",
        "twice: once on Christmas, once at the table.",
        "",
        "FITNESS UNDER THE TREE -- Workout tapes and leotards ride the",
        "aerobics wave. Give with love, and maybe a gift receipt.",
        "",
        "WHAT'S OUT -- The Cabbage Patch mania of '83 is a memory",
        "(VERIFIED); the gifts of '88 plug in, light up, or level up.",
    ]


# ---------------------------------------------------------------------------
# Menu / service entry points
# ---------------------------------------------------------------------------
def giftguide_menu_lines(
    day: Optional[date] = None,
) -> List[Tuple[str, List[str]]]:
    """Reading sections as (title, lines) pairs for the menu wire-up."""
    d = _day(day)
    return [
        ("Hottest Gifts of Christmas 1988", hottest_lines(d)),
        ("Catalog vs. Mall", catalog_vs_mall_lines(d)),
        ("Toy Shortages & Shelf Watch", shortages_lines(d)),
        ("Gift Trends for '88", trends_lines(d)),
    ]


def giftguide_service(app) -> List[Tuple[str, List[str]]]:
    """Coordinator entry point: return gift-guide sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return giftguide_menu_lines()


# ---------------------------------------------------------------------------
# Interactive gift picker
# ---------------------------------------------------------------------------
_RECIPIENT_LABELS = {"kid": "Kid (ages 5-8)", "teen": "Teen", "adult": "Adult"}


def _parse_recipient(raw: str) -> Optional[str]:
    raw = raw.strip().lower()
    mapping = {
        "1": "kid", "kid": "kid", "k": "kid", "child": "kid",
        "2": "teen", "teen": "teen", "t": "teen", "teenager": "teen",
        "3": "adult", "adult": "adult", "a": "adult", "grownup": "adult",
    }
    return mapping.get(raw)


def gift_picker(app, day: Optional[date] = None) -> None:
    """Interactive gift picker: budget + recipient -> 1988 suggestions.

    All output goes through ``app.ansi_scroll``; prompts use ``input()``.
    A blank budget cancels back to the guide menu.
    """
    d = _day(day)
    app.ansi_scroll("THE 1988 GIFT PICKER", 0.01)
    app.ansi_scroll("--------------------", 0.01)
    app.ansi_scroll("Answer two questions and get era-appropriate", 0.01)
    app.ansi_scroll("suggestions. (Blank budget cancels.)", 0.01)
    app.ansi_scroll("", 0.01)

    budget: Optional[float] = None
    while budget is None:
        raw = input("Budget in dollars (e.g. 50)? ").strip()
        if raw == "":
            app.ansi_scroll("Gift picker cancelled.", 0.01)
            return
        try:
            value = float(raw.replace("$", "").replace(",", ""))
        except ValueError:
            app.ansi_scroll("Enter a dollar amount, like 25 or 100.", 0.01)
            continue
        if value <= 0:
            app.ansi_scroll("The budget has to be more than zero.", 0.01)
            continue
        budget = value

    recipient: Optional[str] = None
    while recipient is None:
        app.ansi_scroll("", 0.01)
        app.ansi_scroll("Who is the gift for?", 0.01)
        app.ansi_scroll("  1  Kid (ages 5-8)", 0.01)
        app.ansi_scroll("  2  Teen", 0.01)
        app.ansi_scroll("  3  Adult", 0.01)
        recipient = _parse_recipient(input("Recipient (1-3)? "))
        if recipient is None:
            app.ansi_scroll("Pick 1, 2, or 3.", 0.01)

    picks = pick_gifts(budget, recipient, d)
    label = _RECIPIENT_LABELS[recipient]
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(
        f"GIFT PICKER -- ${budget:,.0f} budget, {label}", 0.01
    )
    app.ansi_scroll("=" * 40, 0.01)
    if picks:
        for index, gift in enumerate(picks, 1):
            app.ansi_scroll(f"{index}. {gift.name}", 0.01)
            app.ansi_scroll(f"   {gift.price_note}", 0.01)
            app.ansi_scroll(f"   {gift.blurb}", 0.01)
            app.ansi_scroll("", 0.01)
        app.ansi_scroll("Happy shopping -- and order early!", 0.01)
    else:
        app.ansi_scroll("Nothing in the catalog fits that budget --", 0.01)
        app.ansi_scroll("but these come closest:", 0.01)
        for index, gift in enumerate(cheapest_for(recipient), 1):
            app.ansi_scroll(
                f"{index}. {gift.name} -- {gift.price_note}", 0.01
            )
    app.ansi_scroll("", 0.01)
    input("Press Enter to return to the guide. ")


def giftguide_menu(app, day: Optional[date] = None) -> None:
    """Interactive '1988 Holiday Shopping Guide' submenu.

    Follows the yearend_menu() convention: numbered sections, text_page
    for each, plus the interactive gift picker, M to return. All
    interactive output goes through ``app.ansi_scroll``.
    """
    d = _day(day)
    sections = giftguide_menu_lines(d)
    while True:
        app.clear()
        app.header_bar("news")
        app.ansi_scroll("1988 HOLIDAY SHOPPING GUIDE - DECEMBER 1988 ARCHIVE", 0.01)
        app.ansi_scroll("---------------------------", 0.01)
        for index, (title, _lines) in enumerate(sections, 1):
            app.ansi_scroll(f"{index}  {title}", 0.01)
        app.ansi_scroll(f"{len(sections) + 1}  Gift Picker (interactive)", 0.01)
        app.ansi_scroll("M  Back", 0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return
        if choice.isdigit():
            number = int(choice)
            if 1 <= number <= len(sections):
                title, lines = sections[number - 1]
                app.text_page("news", title.upper(), lines)
                continue
            if number == len(sections) + 1:
                gift_picker(app, d)
                continue
        app.ansi_scroll("Enter a number from the list, or M.", 0.01)


if __name__ == "__main__":
    for title, lines in giftguide_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
