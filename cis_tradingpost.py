"""Trading Post classifieds for the December 1988 simulation setting.

Pure content + logic module: a three-category classified ads board
(FOR SALE / WANTED / TRADE) seeded with ~15 period-plausible ads --
modems, 8-bit micros, dot-matrix printers, floppies, LPs, concert
tickets, and computer books -- all priced in 1988 dollars.

Users may place their own ads; ads persist in ``tradingpost.json``
(beside this module, mirroring the forums.json load/save pattern) and
expire 30 days after the simulated date they were placed. All content
functions accept an optional ``day`` parameter defaulting to the
session-aware ``cis_dynamic.simulation_day()``; the ``tradingpost_menu``
entry point follows the ``sports_menu()`` convention and drives the
board through the ``app`` module it is handed (``clear``,
``header_bar``, ``ansi_scroll``, ``text_page``).

Global setting rule: nothing after December 1988. Seed ads are dated
early/mid December 1988 and expire on that basis; no ad may reference
a 1989-or-later date or event.
"""
from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cis_session import read_input as input

import cis_dynamic
import cis_storage


# ---------------------------------------------------------------------------
# Storage (mirrors the forums.json load/save pattern in compuserve.py)
# ---------------------------------------------------------------------------
# Repo root derived from this file -- never hardcode absolute paths.
REPO_ROOT = Path(__file__).resolve().parent
# Patchable in tests so a run never touches the real tradingpost.json.
BASE_DIR = REPO_ROOT
TRADINGPOST_FILENAME = "tradingpost.json"
AD_LIFETIME_DAYS = 30
_SCHEMA_VERSION = 1
_MISSING = object()


def _load_data() -> Dict:
    """Load the tradingpost.json payload, seeding it on first run."""
    data = cis_storage.load_json(BASE_DIR, TRADINGPOST_FILENAME, default=_MISSING)
    if data is _MISSING or not isinstance(data, dict) or "ads" not in data:
        data = {"version": _SCHEMA_VERSION, "ads": seed_ads()}
        _save_data(data)
    return data


def _save_data(data: Dict) -> None:
    cis_storage.write_json_atomic(BASE_DIR, TRADINGPOST_FILENAME, data)


# ---------------------------------------------------------------------------
# Seed ads (all December 1988; plausible period prices, not exact quotes)
# ---------------------------------------------------------------------------
# Format: (category, title, price (USD), contact handle, body, placed date).
# price=None means "make offer / free".
_SEED_AD_DEFS: List[Tuple[str, str, Optional[float], str, str, str]] = [
    # -- FOR SALE ---------------------------------------------------------
    ("FOR SALE", "Hayes Smartmodem 1200", 200.0, "MODEM_MAVEN",
     "External 1200-baud modem in original box with manuals and cables. "
     "Works perfectly -- I'm upgrading to a 2400. Bell 212A / 103 compatible.",
     "1988-12-03"),
    ("FOR SALE", "Commodore 64 + 1541 disk drive", 150.0, "DISK_DRIVE_DAN",
     "Breadbox C64 with 1541 drive, datasette, and a box of 20 disks "
     "of games and utilities. Both drives aligned, clean bill of health.",
     "1988-12-05"),
    ("FOR SALE", "Apple IIe, 128K, dual drives", 275.0, "BYTE_BANDIT",
     "Enhanced IIe with 128K, two Disk II drives, monochrome monitor, "
     "and AppleWorks. Keyboard and power supply solid.",
     "1988-12-06"),
    ("FOR SALE", "Atari 520ST + color monitor", 325.0, "PIXEL_PETE",
     "520ST with 512K, SC1224 color monitor, and GEM desktop. Great for "
     "MIDI -- built-in ports. Mouse included.",
     "1988-12-08"),
    ("FOR SALE", "Epson LX-80 dot-matrix printer", 175.0, "PRINT_QUEEN",
     "Near-letter-quality 9-pin dot-matrix, 100 cps. Fresh ribbon, "
     "tractor feed, all manuals. Quiet for a dot-matrix.",
     "1988-12-09"),
    ("FOR SALE", "Epson FX-85 wide-carriage printer", 225.0, "PRINT_QUEEN",
     "132-column 9-pin dot-matrix, 160 cps draft. Ideal for spreadsheets "
     "and program listings. Spare ribbon thrown in.",
     "1988-12-10"),
    ("FOR SALE", "5.25-inch floppies, box of 10 DSDD", 12.0, "FLOPPY_FAN",
     "Unopened box of ten double-sided, double-density 5.25-inch disks. "
     "Perfect for backups of your BBS downloads.",
     "1988-12-11"),
    ("FOR SALE", "Classic rock vinyl, 20 LPs", 30.0, "WAX_WALLY",
     "Lot of twenty LPs: Zeppelin, Floyd, Stones, the Who. Sleeves VG+, "
     "vinyl plays clean. Sold as a lot only.",
     "1988-12-12"),
    ("FOR SALE", "Concert tickets: Def Leppard, Hysteria tour", 40.0, "STAGE_DAVE",
     "Pair of tickets, lower level, for the Hysteria tour stop this month. "
     "Face value $19.50 each -- selling at cost, can't make the show.",
     "1988-12-13"),
    ("FOR SALE", "K&R 'The C Programming Language'", 15.0, "COMPILER_CARL",
     "Kernighan & Ritchie's classic, first edition, good condition. "
     "Essential reading if you're moving past BASIC.",
     "1988-12-14"),
    ("FOR SALE", "Flight Simulator II (C64)", 25.0, "CHIP_HOUND",
     "SubLOGIC Flight Simulator II on 5.25-inch disk with manual and "
     "keyboard overlay. Flies great on a 1541.",
     "1988-12-15"),
    # -- WANTED -------------------------------------------------------------
    ("WANTED", "Hayes 2400-baud modem", 300.0, "BBS_BOB",
     "Wanted: Hayes-compatible 2400-baud modem for my BBS node. Will pay "
     "up to $300 for a clean unit with box.",
     "1988-12-04"),
    ("WANTED", "Macintosh Plus or SE", 900.0, "DESKTOP_DONNA",
     "Wanted: working Macintosh Plus or SE, any keyboard, any drives. "
     "Cash buyer, will pick up in the metro area.",
     "1988-12-07"),
    # -- TRADE ----------------------------------------------------------------
    ("TRADE", "Apple IIc for Amiga 500", None, "SOFTSWAPPER",
     "Will trade my Apple IIc (128K, one drive, monitor) straight across "
     "for an Amiga 500 in comparable shape. Talk to me.",
     "1988-12-02"),
    ("TRADE", "BYTE magazines for C64 software", None, "SYSOP_SAM",
     "Trading a stack of 1986-87 BYTE magazines for original C64 games "
     "or utilities on disk. Send your list.",
     "1988-12-16"),
]

CATEGORIES = ["FOR SALE", "WANTED", "TRADE"]


def seed_ads() -> List[Dict]:
    """Return a fresh copy of the seed ads, each with a TP- id."""
    ads = []
    for number, (category, title, price, contact, body, placed) in enumerate(
            _SEED_AD_DEFS, start=1):
        ads.append({
            "id": f"TP-{number:04d}",
            "category": category,
            "title": title,
            "price": price,
            "contact": contact,
            "body": body,
            "placed": placed,
        })
    return ads


# ---------------------------------------------------------------------------
# Day helpers
# ---------------------------------------------------------------------------
def _day(day: Optional[date]) -> date:
    """Resolve the simulation day, defaulting to the session-aware one."""
    if day is not None:
        return day
    try:
        return cis_dynamic.simulation_day()
    except Exception:
        return date(1988, 12, 15)


def _parse_placed(value: str) -> Optional[date]:
    try:
        year, month, day = (int(part) for part in value.split("-"))
        return date(year, month, day)
    except (ValueError, AttributeError, TypeError):
        return None


def is_expired(ad: Dict, day: Optional[date] = None) -> bool:
    """An ad expires 30 days after the simulated date it was placed."""
    placed = _parse_placed(ad.get("placed", ""))
    if placed is None:
        return False
    return (_day(day) - placed).days > AD_LIFETIME_DAYS


# ---------------------------------------------------------------------------
# Ad operations
# ---------------------------------------------------------------------------
def load_ads() -> List[Dict]:
    """All ads on file, oldest first."""
    return copy.deepcopy(_load_data().get("ads", []))


def active_ads(day: Optional[date] = None) -> List[Dict]:
    """Ads that have not expired, oldest first."""
    return [ad for ad in load_ads() if not is_expired(ad, day)]


def ads_in_category(category: str, day: Optional[date] = None) -> List[Dict]:
    """Active ads for one category, oldest first."""
    return [ad for ad in active_ads(day) if ad.get("category") == category]


def _next_id(ads: List[Dict]) -> str:
    biggest = 0
    for ad in ads:
        ad_id = str(ad.get("id", ""))
        if ad_id.startswith("TP-"):
            try:
                biggest = max(biggest, int(ad_id[3:]))
            except ValueError:
                continue
    return f"TP-{biggest + 1:04d}"


def place_ad(category: str, title: str, price: Optional[float],
             contact: str, body: str,
             day: Optional[date] = None) -> Dict:
    """Append a user ad and persist it; returns the stored ad dict."""
    data = _load_data()
    ads = data.get("ads", [])
    ad = {
        "id": _next_id(ads),
        "category": category,
        "title": title.strip(),
        "price": price,
        "contact": (contact or "ANONYMOUS").strip().upper() or "ANONYMOUS",
        "body": body.strip(),
        "placed": _day(day).isoformat(),
    }
    ads.append(ad)
    data["ads"] = ads
    _save_data(data)
    return copy.deepcopy(ad)


# ---------------------------------------------------------------------------
# Display lines
# ---------------------------------------------------------------------------
def _format_price(price) -> str:
    if price is None:
        return "MAKE OFFER"
    try:
        value = float(price)
    except (TypeError, ValueError):
        return "MAKE OFFER"
    if value.is_integer():
        return f"${int(value)}"
    return f"${value:0.2f}"


def category_lines(category: str, day: Optional[date] = None) -> List[str]:
    """Display lines for one category's active ads."""
    ads = ads_in_category(category, day)
    lines = [f"{category} -- {len(ads)} ad{'s' if len(ads) != 1 else ''}",
             "-" * 60, ""]
    if not ads:
        lines.append("No ads in this category yet. Place the first one!")
        return lines
    for ad in ads:
        price = _format_price(ad.get("price")).rjust(10)
        lines.append(f"{ad.get('id', '')}  {ad.get('title', '')}{price}")
        lines.append(f"    Contact: {ad.get('contact', 'ANONYMOUS')}"
                     f"    Placed: {ad.get('placed', '')}")
        for body_line in str(ad.get("body", "")).splitlines():
            lines.append(f"    {body_line}")
        lines.append("")
    return lines


def tradingpost_menu_lines(day: Optional[date] = None) -> List[Tuple[str, List[str]]]:
    """All categories as (title, lines) pairs for the menu wire-up."""
    return [(category, category_lines(category, day)) for category in CATEGORIES]


# ---------------------------------------------------------------------------
# Interactive menu (app follows the sports_menu convention: the module it
# is handed supplies clear/header_bar/ansi_scroll/text_page)
# ---------------------------------------------------------------------------
def tradingpost_menu(app) -> None:
    """Trading Post classifieds submenu: browse categories or place an ad."""
    while True:
        app.clear()
        app.header_bar("tradingpost")
        app.ansi_scroll("TRADING POST CLASSIFIEDS", 0.01)
        app.ansi_scroll("------------------------", 0.01)
        app.ansi_scroll("Buy, sell, and trade with fellow members.", 0.01)
        app.ansi_scroll("Ads expire 30 days after placement.", 0.01)
        app.ansi_scroll("", 0.01)
        for index, category in enumerate(CATEGORIES, 1):
            count = len(ads_in_category(category))
            app.ansi_scroll(f"{index}  {category} ({count} ads)", 0.01)
        app.ansi_scroll("4  Place an ad", 0.01)
        app.ansi_scroll("M  Back", 0.01)
        choice = input("Choice: ").strip().upper()
        if choice == "M":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            title, lines = tradingpost_menu_lines()[int(choice) - 1]
            app.text_page("tradingpost", title, lines)
        elif choice == "4":
            _place_ad_flow(app)
        else:
            app.ansi_scroll("Enter 1-4, or M to go back.", 0.01)


def _place_ad_flow(app) -> None:
    """Walk the user through placing one classified ad."""
    app.ansi_scroll("", 0.01)
    app.ansi_scroll("PLACE AN AD", 0.01)
    for index, category in enumerate(CATEGORIES, 1):
        app.ansi_scroll(f"{index}  {category}", 0.01)
    choice = input("Category (1-3): ").strip()
    if choice not in ("1", "2", "3"):
        app.ansi_scroll("No ad placed -- pick a category next time.", 0.01)
        return
    category = CATEGORIES[int(choice) - 1]

    title = input("Ad title (60 chars): ").strip()[:60]
    if not title:
        app.ansi_scroll("No ad placed -- an ad needs a title.", 0.01)
        return

    price_text = input("Price in dollars (blank = make offer): ").strip()
    price: Optional[float] = None
    if price_text:
        try:
            price = round(float(price_text.replace("$", "").replace(",", "")), 2)
            if price < 0:
                price = 0.0
        except ValueError:
            app.ansi_scroll("No ad placed -- price must be a number.", 0.01)
            return

    contact = input("Contact handle: ").strip() or "ANONYMOUS"
    body = input("Description (one line): ").strip()[:200]
    if not body:
        app.ansi_scroll("No ad placed -- an ad needs a description.", 0.01)
        return

    ad = place_ad(category, title, price, contact, body)
    app.ansi_scroll("", 0.01)
    app.ansi_scroll(f"Ad {ad['id']} placed under {category}.", 0.01)
    app.ansi_scroll("It will run for 30 days. Good luck!", 0.01)
    input("Press ENTER to continue. ")


if __name__ == "__main__":
    for title, lines in tradingpost_menu_lines(date(1988, 12, 15)):
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
