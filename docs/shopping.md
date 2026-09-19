# Shopping: Comp-U-Store and the Trading Post

## Comp-U-Store

Comp-U-Store contains a fictional 76-item 1988 mail-order catalog covering computers, modems,
cables, media, printers, software, books, accessories, and upgrades. Choose `GO SHOP`,
then Comp-U-Store. Enter an item number for its description, availability, compatibility,
and a simulated owner's report when available. Use `C` to choose a category, `S` to
search, `D` for rotating December specials, `K` for IBM PC/XT, IBM PC AT, Macintosh
Plus, Macintosh SE, Commodore 64, Amiga 500, or TRS-80 Model I/III compatibility guidance,
`A` to add an item and quantity, `V` to review the order, `R` to remove an item, and `O`
to send the order. `F` and `B` page through the catalog.

Use `PC` to see thirteen complete configurations: XT-compatible Starter and Office 20,
286-compatible Office, Macintosh Plus, Macintosh SE 1/20, Commodore 64C Disk Starter,
Amiga 500 512K and 1MB Color, Apple IIe 128K, expanded ROM 01 IIgs, Atari 1040STF,
Tandy 1000 HX 640K, and Tandy 102 portable bundles. Descriptions list included displays,
drives, memory, keyboards, cables, and software. The 64C starter needs your TV or
an additional monitor. `K` accepts a computer SKU (for example `2004`) or system
name and finds matching products. Read accessory prerequisites: a VGA monitor
needs a VGA card, and the 1MB Amiga bundle already includes its trapdoor expansion.
Prices and bundles are reconstructed simulation offerings, not original merchant quotes.

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


## Active computer and download limits

After delivery, use `GO SETUP`. `USE EQ-0001` selects one of your own delivered
computers; `ATTACH EQ-0002` fits an owned compatible accessory. Use the actual IDs
listed on your screen. `DETACH id` removes an accessory, and `OFF` returns to
legacy unrestricted downloads and your saved terminal preferences.

Your setup persists per account, including each computer's attachments and
downloaded-file ledger. It displays RAM, drives, display, terminal width, modem,
used capacity and accumulated simulated transfer time. Selection applies the
machine's 40/80-column width; fitting a modem applies its baud rate. Most desktop
bundles need a purchased modem and the correct cable/interface. The Tandy 102 has
its own 300-baud modem. An accessory cannot be fitted to two computers at once.

Active hardware limits apply to library and Access downloads. Incompatible or
unknown software platforms are rejected; text documentation is portable. Catalog
archive payloads remain reconstructed samples, not executable computer emulation.
An explicit minimum-memory requirement is checked when present. Downloads require
free capacity; replacing a filename charges only the new size. `DELETE filename`
in Setup frees the simulated space while retaining exported host copies.

Storage uses a simplified download budget: one disk per supplied drive, the
supplied hard disk, or the portable's 24K free RAM budget. Adding supported storage
increases it. This is not a sector-level filesystem or disk-swapping emulator.
Server-side PER files do not use this local download budget. Modem rate and B/X
protocol overhead determine the recorded duration. Progress is accelerated (fast
mode skips waiting); the full modeled duration is shown in seconds, not added to
real session billing. Returning the active computer makes it unavailable until
you choose another computer or turn hardware limits off.

---

[Back to the user guide](../USER_GUIDE.md)
