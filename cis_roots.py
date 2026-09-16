"""Roots & Branches Genealogy Forum content module.

Section spec, December 1988 seed posts, and period-correct research
tips for the ``roots`` forum ("Roots & Branches Genealogy Forum").
Seed-post field format matches computer_communities.json message
entries (content_id/section/date/author/subject/body/parent); the
coordinator appends them to that file and cis_communities.install()
merges them into forums.json on startup.

Period rules enforced by this module:
* Census coverage is limited to the schedules released by December 1988
  (1790 through 1910). Later schedules are never listed as available.
* Research methods are period-correct only: microfilm/microfiche readers,
  SASE letters to county courthouses, DAR lineage books, LDS Family
  History Centers, NARA regional archives, the SSDI on microfiche, and
  NARA passenger-list microfilm.
* Nothing in this module references anything after December 1988: no
  web-based family trees, no networked genealogy services, no genetic
  testing for genealogy, and no post-1988 resource of any kind.
"""

FORUM_ID = "roots"
FORUM_TITLE = "Roots & Branches Genealogy Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("roots_start", "Getting Started"), ...}
# The coordinator wires this into FORUM_CATALOG["roots"]["sections"].
SECTIONS = {
    "1": ("roots_start", "Getting Started"),
    "2": ("roots_nara", "NARA & Archives"),
    "3": ("roots_census", "Census Records"),
    "4": ("roots_fhc", "Family History Centers"),
    "5": ("roots_surnames", "Surname Registry"),
    "6": ("roots_military", "Military Records"),
}

SEED_POSTS = [
    {
        "content_id": "roots-1988-001",
        "section": "roots_start",
        "date": "12/01/88",
        "author": "RootsSysop",
        "subject": "Welcome to Roots & Branches -- read this first",
        "body": (
            "Welcome to the Roots & Branches Genealogy Forum! Whether you "
            "are chasing your first family line or you have been at this "
            "for twenty years, you will find help here. A few ground rules "
            "and suggestions:\n\n"
            "1. Start with yourself and work backward, one generation at a "
            "time. Record full names, dates, and places on pedigree charts "
            "and family group sheets.\n"
            "2. Talk to your oldest relatives NOW, while you can. A "
            "tape-recorded interview beats a courthouse record every time.\n"
            "3. Cite your sources. 'Grandma said so' is a clue, not proof.\n"
            "4. Use the Surname Registry section to post the names you are "
            "researching -- surname, dates, and place.\n\n"
            "Browse the section list, introduce yourself, and happy hunting!"
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-002",
        "section": "roots_start",
        "date": "12/03/88",
        "author": "FamilySleuth",
        "subject": "New to genealogy -- where do I actually begin?",
        "body": (
            "I want to trace my family but I am overwhelmed. I have my "
            "grandparents' names and not much else. Where do I start without "
            "spending a fortune? Is there a book or magazine that explains "
            "the basics? I live near Dallas if that matters for libraries "
            "or archives. Any advice for a total beginner would be "
            "appreciated."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-003",
        "section": "roots_start",
        "date": "12/04/88",
        "author": "RootsSysop",
        "subject": "RE: New to genealogy -- where do I actually begin?",
        "body": (
            "FamilySleuth, here is the standard beginner drill:\n\n"
            "1. Fill out a pedigree chart starting with yourself. Interview "
            "parents, aunts, uncles -- ask about full names (including "
            "maiden names), birth/marriage/death dates and places.\n"
            "2. Gather home sources: family Bibles, old letters, photo "
            "albums, funeral cards, military discharge papers.\n"
            "3. Get a beginner book. The public library will have several; "
            "ask the reference desk for the genealogy shelf. Everton's "
            "Genealogical Helper magazine is a good monthly to browse.\n"
            "4. Write to county courthouses for birth, marriage, and death "
            "certificates -- always enclose a self-addressed stamped "
            "envelope (SASE) and the fee.\n"
            "5. Visit your nearest LDS Family History Center (see the "
            "Family History Centers section) -- the volunteers will get you "
            "onto microfilm fast.\n\n"
            "Work backward one generation at a time and document everything."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-004",
        "section": "roots_start",
        "date": "12/05/88",
        "author": "PaperTrail",
        "subject": "Organizing paper files -- binders vs. file folders?",
        "body": (
            "After a year of collecting, I am drowning in paper: census "
            "printouts from the microfilm reader, courthouse letters, "
            "photocopies of pension files. How do you all organize? I am "
            "torn between a binder per surname and plain manila folders in "
            "a file cabinet. Also, do you keep a research log? I keep "
            "re-searching the same microfilm rolls because I forgot I "
            "already looked. There has to be a better system."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-005",
        "section": "roots_nara",
        "date": "12/06/88",
        "author": "LoneStarRoots",
        "subject": "Which NARA regional archive holds my records?",
        "body": (
            "I need naturalization and federal court records for ancestors "
            "in Texas and Oklahoma. I know the National Archives has "
            "regional branches -- is there one near Dallas? More generally, "
            "how do I find out which regional archive covers which states "
            "before I write or drive over? I would rather not guess wrong "
            "and waste a trip."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-006",
        "section": "roots_nara",
        "date": "12/07/88",
        "author": "ArchivalDan",
        "subject": "RE: Which NARA regional archive holds my records?",
        "body": (
            "LoneStarRoots, you are in luck: the National Archives regional "
            "branch in Fort Worth serves Texas, Oklahoma, Arkansas, and "
            "Louisiana, so your people are covered right there. Each "
            "regional archive publishes a guide to its holdings -- write "
            "ahead and ask for it, and describe the records you want so the "
            "staff can confirm they hold them. For military and pension "
            "files, though, those stay in Washington -- you order copies by "
            "mail on the NATF forms (see the Military Records section). "
            "Always write first; the archivists will tell you exactly what "
            "to bring."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-007",
        "section": "roots_census",
        "date": "12/08/88",
        "author": "CensusTaker",
        "subject": "Soundex microfilm -- how do I actually use it?",
        "body": (
            "I finally sat down at a microfilm reader with the Soundex "
            "index and felt lost. I am looking for my great-grandfather in "
            "the 1900 census, surname KOWALSKI in Illinois. Can someone walk "
            "me through the Soundex coding? I know it groups similar-sounding "
            "names, but how do I turn KOWALSKI into a code, and what do I do "
            "with the code once I have it? The 1900 and 1910 censuses are "
            "Soundexed (and 1880 partially), right?"
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-008",
        "section": "roots_census",
        "date": "12/09/88",
        "author": "BrickWallBetty",
        "subject": "RE: Soundex microfilm -- how do I actually use it?",
        "body": (
            "CensusTaker, the Soundex is your best friend once it clicks. "
            "Take the first letter of the surname (K), then code the "
            "consonants: KOWALSKI becomes K-420. Find the microfilm roll for "
            "the state and code range, then scan the cards alphabetically by "
            "given name within the code. Each card gives the enumeration "
            "district, sheet, and line -- then you pull the actual census "
            "roll. Yes: Soundex microfilm exists for the 1880 (partial), "
            "1900, and 1910 censuses at NARA and most large libraries. Bring "
            "dimes for the reader-printer -- you will want copies."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-009",
        "section": "roots_census",
        "date": "12/10/88",
        "author": "OhioBound",
        "subject": "1890 census destroyed -- what are the workarounds?",
        "body": (
            "Just learned the hard way that the 1890 federal census was "
            "destroyed in a 1921 fire -- the one census I needed most, of "
            "course. My Ohio family vanishes between 1880 and 1900. What do "
            "experienced researchers use as a substitute for 1890? I have "
            "heard mention of a special veterans schedule and city "
            "directories. What actually works?"
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-010",
        "section": "roots_census",
        "date": "12/11/88",
        "author": "BuckeyeGene",
        "subject": "RE: 1890 census destroyed -- what are the workarounds?",
        "body": (
            "OhioBound, the 1890 gap is every genealogist's rite of "
            "passage. Substitutes that actually work:\n\n"
            "- The special 1890 schedule of Union veterans and widows "
            "survives for about half the states -- check if Ohio's is on "
            "microfilm at your library.\n"
            "- City directories for 1890-1891 list addresses and "
            "occupations year by year.\n"
            "- Tax lists, voter registrations, and church records.\n"
            "- State censuses: some states took their own (Ohio did not in "
            "1890, unfortunately).\n"
            "- County histories with biographical sketches.\n\n"
            "Layer two or three of these and you can usually bridge the "
            "1880-1900 gap."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-011",
        "section": "roots_fhc",
        "date": "12/12/88",
        "author": "UtahBound",
        "subject": "First visit to a Family History Center -- what to expect?",
        "body": (
            "There is an LDS Family History Center twenty minutes from me "
            "and I finally want to go. What should I expect? Do I need to "
            "be a church member? Can I just walk in and use the microfilm "
            "readers? I have a list of rolls I want from the Family History "
            "Library Catalog -- can they get them, and what does it cost? "
            "Any etiquette tips so I do not embarrass myself on day one?"
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-012",
        "section": "roots_fhc",
        "date": "12/13/88",
        "author": "MicrofilmMabel",
        "subject": "RE: First visit to a Family History Center -- what to expect?",
        "body": (
            "UtahBound, welcome aboard! The centers are open to everyone, "
            "no membership needed, and the volunteers are wonderful. You "
            "can order any microfilm listed in the Family History Library "
            "Catalog on microfiche -- rental is a few dollars per roll and "
            "the film stays at the center for several weeks. Call ahead for "
            "hours, since most are staffed by volunteers. Bring a notebook, "
            "pencils (no pens near the readers, please), and coins for the "
            "copy machine. Start with the IGI on microfiche -- the "
            "International Genealogical Index -- to see if your surnames "
            "are already extracted."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-013",
        "section": "roots_surnames",
        "date": "12/14/88",
        "author": "ChicagoRoots",
        "subject": "Surname registry: KOWALSKI, Chicago 1880-1920",
        "body": (
            "Posting to the registry per the sysop's instructions:\n\n"
            "Surname: KOWALSKI (also spelled KOWALSKY, KOVALSKI)\n"
            "Place: Chicago, Cook County, Illinois\n"
            "Dates: arrived about 1882, in Chicago by the 1900 census\n"
            "Seeking: parents of STANLEY KOWALSKI (b. ~1860 Poland), "
            "marriage record to MARY NOWAK (~1885, St. Stanislaus parish?), "
            "and the passenger list for the 1882 arrival.\n\n"
            "Willing to trade lookups in Chicago-area microfilm. Contact "
            "me here in the forum."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-014",
        "section": "roots_surnames",
        "date": "12/16/88",
        "author": "CorkToBoston",
        "subject": "Surname registry: SULLIVAN, County Cork to Boston",
        "body": (
            "Surname: SULLIVAN (O'SULLIVAN in some records)\n"
            "Place: Skibbereen parish, County Cork, Ireland -> Boston, "
            "Massachusetts\n"
            "Dates: emigrated about 1849-1851, in Boston by 1860 census\n"
            "Seeking: baptismal records for DANIEL SULLIVAN (b. ~1825) and "
            "wife HONORA, passenger arrival record (Boston, ~1850), and any "
            "connection to Sullivans remaining in Skibbereen.\n\n"
            "I have Boston city directories 1860-1880 on microfilm notes "
            "and will gladly share lookups."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-015",
        "section": "roots_military",
        "date": "12/18/88",
        "author": "RevWarRick",
        "subject": "Revolutionary War pension files -- what is actually in them?",
        "body": (
            "I am thinking of ordering my 4th-great-grandfather's "
            "Revolutionary War pension file from the National Archives. "
            "Before I send the NATF Form 80 and the fee, what can I expect "
            "to get? Are these just a few pages, or can they really run to "
            "dozens of pages? I have heard they sometimes include family "
            "details you cannot find anywhere else."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-016",
        "section": "roots_military",
        "date": "12/19/88",
        "author": "PensionFileFan",
        "subject": "RE: Revolutionary War pension files -- what is actually in them?",
        "body": (
            "RevWarRick, order it -- pension files are genealogy gold. A "
            "Revolutionary War pension file (the M804 microfilm series) can "
            "run 20 to 60 pages: the veteran's own narrative of his "
            "service, affidavits from comrades, marriage records, children's "
            "birth dates, and sometimes letters in the widow's hand. The "
            "NATF Form 80 costs $10 and you mail it to Washington. Be "
            "patient -- turnaround is several weeks. One file broke a "
            "ten-year brick wall for me with a single deposition naming "
            "four siblings."
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-017",
        "section": "roots_military",
        "date": "12/20/88",
        "author": "DraftDigger",
        "subject": "WWI draft cards on microfilm -- anyone used them?",
        "body": (
            "I found out my great-grandfather's WWI draft registration card "
            "is on microfilm (the M1509 series, I think). For those who "
            "have used them: what information is actually on the card? I am "
            "hoping for a birth date and physical description. Are these at "
            "NARA regional branches, or do I need to go through the Family "
            "History Center? Any tips for finding the right roll?"
        ),
        "parent": None,
    },
    {
        "content_id": "roots-1988-018",
        "section": "roots_military",
        "date": "12/22/88",
        "author": "ServiceRecordSam",
        "subject": "RE: WWI draft cards on microfilm -- anyone used them?",
        "body": (
            "DraftDigger, the WWI draft cards are fantastic -- nearly every "
            "man born roughly 1872-1900 registered, so coverage is "
            "excellent. Each card gives full name, home address, birth date "
            "and place, occupation and employer, nearest relative, and a "
            "physical description including height, build, and eye and hair "
            "color. The M1509 microfilm is at NARA and many large libraries "
            "and Family History Centers -- the rolls are arranged by state, "
            "then county and draft board. Bring the 1910 or 1900 census "
            "entry so you know which board's roll to pull."
        ),
        "parent": None,
    },
]


def section_spec():
    """Return the forum section spec for coordinator wiring."""
    return dict(SECTIONS)


def seed_posts():
    """Return a copy of the seed posts for forum seeding."""
    return [dict(post) for post in SEED_POSTS]


RESEARCH_TIPS = [
    {
        "title": "Start with what you know",
        "body": (
            "Begin with yourself and work backward one generation at a "
            "time. Fill in pedigree charts and family group sheets from "
            "home sources -- Bibles, letters, photos -- before spending a "
            "dime on records."
        ),
    },
    {
        "title": "Interview your oldest relatives",
        "body": (
            "A tape-recorded interview with a grandparent is worth a dozen "
            "courthouse trips. Ask about full maiden names, places of "
            "birth, and family stories -- then verify each claim against "
            "records."
        ),
    },
    {
        "title": "Always enclose a SASE",
        "body": (
            "When writing to a county courthouse or archive, always include "
            "a self-addressed stamped envelope and the exact fee. Clerks "
            "answer SASE letters first, and a polite, specific request gets "
            "a better answer than a vague one."
        ),
    },
    {
        "title": "Learn the Soundex",
        "body": (
            "The Soundex microfilm indexes the 1880 (partial), 1900, and "
            "1910 censuses by how surnames sound, not how they are spelled. "
            "Master the coding -- it finds ancestors whose names the census "
            "taker mangled."
        ),
    },
    {
        "title": "Use the Family History Center near you",
        "body": (
            "LDS Family History Centers are open to everyone and will rent "
            "any microfilm in the Family History Library Catalog for a few "
            "dollars a roll. The volunteers will teach you the readers, and "
            "the IGI on microfiche is the fastest first search there is."
        ),
    },
    {
        "title": "Order pension files, not just service records",
        "body": (
            "A compiled service record says where a soldier served. A "
            "pension file says who he was -- depositions, marriage records, "
            "children's births. Send NATF Form 80 to the National Archives "
            "in Washington; the $10 fee is the best money in genealogy."
        ),
    },
]


def render_tips():
    """Return a printable rendering of the research tips."""
    lines = ["GENEALOGY RESEARCH TIPS", "=" * 23, ""]
    for i, tip in enumerate(RESEARCH_TIPS, 1):
        lines.append(f"{i}. {tip['title']}")
        lines.append(f"   {tip['body']}")
        lines.append("")
    return "\n".join(lines).rstrip()
