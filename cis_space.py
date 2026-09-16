"""Space & Astronomy Forum content module.

Section spec and December 1988 seed posts for the ``space`` forum
("Space & Astronomy Forum"): shuttle & spaceflight, deep sky
observing, planets & probes, amateur telescopes, NASA & space
news, and star parties.

Period rules enforced by this module:
* Spaceflight news is December 1988: STS-26 Discovery return-to-
  flight (Sep 29 - Oct 3, 1988, deployed TDRS-3), STS-27 Atlantis
  classified DoD flight (Dec 2 - 6, 1988, tile damage on orbit),
  the Soviet shuttle Buran's uncrewed flight (Nov 15, 1988, two
  orbits, automatic landing), Mir EO-3 crew Titov and Manarov's
  year-long mission ending Dec 21, 1988 (new endurance record),
  the French Aragatz visit, EO-4 crew Volkov and Krikalev.
  Nothing references anything after December 1988.
* Planetary probes: Phobos 1 lost after a bad command on Aug 28
  (contact lost Sep 2, 1988, recovery efforts ended Nov 3, 1988),
  Phobos 2 still on course for Mars orbit insertion in January
  1989, Voyager 2 closing on its August 1989 Neptune encounter
  after the January 1986 Uranus flyby. Magellan (May 1989) and
  Galileo (late 1989) are discussed only as scheduled launches.
  No Hubble (April 1990) or any post-1988 mission is mentioned.
* Amateur gear is 1988-era: Celestron C8, Meade 2080/LX3,
  Dobsonian Newtonians, film astrophotography (piggyback, hand
  guiding, Tri-X, hypered film, Kodak 103a). No digital cameras,
  no internet, no post-1988 equipment.
"""

FORUM_ID = "space"
FORUM_TITLE = "Space & Astronomy Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("space_shuttle", "Shuttle & Spaceflight"), ...}
# The coordinator wires this into FORUM_CATALOG["space"]["sections"].
SECTIONS = {
    "1": ("space_shuttle", "Shuttle & Spaceflight"),
    "2": ("space_deepsky", "Deep Sky Observing"),
    "3": ("space_planets", "Planets & Probes"),
    "4": ("space_scopes", "Amateur Telescopes"),
    "5": ("space_nasa", "NASA & Space News"),
    "6": ("space_starparty", "Star Parties"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "space-1988-001",
        "section": "space_shuttle",
        "date": "12/01/88",
        "author": "OrbitSysop",
        "subject": "Welcome to the Space & Astronomy Forum",
        "body": (
            "Welcome aboard. This forum covers the night sky and the "
            "machines we send into it. Shuttle & Spaceflight is for the "
            "return-to-flight missions; Deep Sky Observing for what you "
            "can see with your own eyes and eyepieces; Planets & Probes "
            "for Voyager, Phobos, and everything robotic; Amateur "
            "Telescopes for buying, building, and using scopes; NASA & "
            "Space News for agency and Soviet doings; and Star Parties "
            "for club outings and observing trips. Post your location, "
            "your scope (or lack of one), and what is currently keeping "
            "you up at night. Clear skies."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-002",
        "section": "space_shuttle",
        "date": "12/02/88",
        "author": "SKYWATCHER",
        "subject": "Two months after STS-26 -- where do we stand?",
        "body": (
            "Hard to believe it has been two months since Discovery "
            "lifted off on September 29 and brought the shuttle back to "
            "flight. Hauck, Covey, Lounge, Nelson, and Hilmers did a "
            "picture-perfect four-day mission, deployed TDRS-3, and came "
            "home to Edwards on October 3 with no major problems. Watching "
            "that launch after thirty-two months grounded was something "
            "else. The question now: can NASA keep the pace? There is talk "
            "of eight flights next year. Anyone heard firm dates for "
            "STS-29 (Discovery again, TDRS-4) and the Magellan launch?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-003",
        "section": "space_shuttle",
        "date": "12/07/88",
        "author": "APERTURE8",
        "subject": "Atlantis home safe -- what was that tile story?",
        "body": (
            "STS-27 is down safe at Edwards after Tuesday's landing, "
            "wrapping up the classified DoD flight (Gibson, Gardner, "
            "Mullane, Ross, and Shepherd, launched December 2). But the "
            "word from the tracking sites and the press is that Atlantis "
            "came home with serious tile damage -- hundreds of damaged "
            "tiles and one missing tile clean over an antenna plate. "
            "Scary stuff, and it raises questions about how well the "
            "improved ascent inspections are working. Anyone know whether "
            "the December 2 launch photo showed debris striking the "
            "orbiter? Hope this gets a thorough review before the next "
            "flight."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-004",
        "section": "space_nasa",
        "date": "12/05/88",
        "author": "REDSHIFT",
        "subject": "Buran flies -- unmanned, two orbits, lands itself",
        "body": (
            "The Soviets did it on November 15: their shuttle Buran flew "
            "an entirely unmanned test flight, two orbits, and landed "
            "itself at Baikonur under automatic control, reportedly in "
            "heavy crosswinds and even changing its own approach direction "
            "on final. Whatever you think of the politics, that is a "
            "serious technical achievement -- no American orbiter has ever "
            "flown uncrewed. Questions: does Buran have main engines of "
            "its own (looks like it relies on the Energia core, unlike "
            "our SSMEs), and do we think the Soviets will fly it manned "
            "any time soon? The race just got interesting again."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-005",
        "section": "space_nasa",
        "date": "12/11/88",
        "author": "NEPTUNE2",
        "subject": "Phobos 1: the official word",
        "body": (
            "Sad confirmation on the Soviet Mars shot: Moscow has "
            "announced it will make no further attempts to contact "
            "Phobos 1. The probe went silent on September 2 after a "
            "faulty ground command on August 28 accidentally shut down "
            "its attitude thrusters -- the solar panels drifted off the "
            "Sun and the batteries died. Phobos 2, launched July 12, is "
            "still healthy and on course for Mars orbit insertion next "
            "month, with the low pass over the moon Phobos and the two "
            "landers still ahead of it. One mission down, but the real "
            "science is still in front of Phobos 2. Fingers crossed for "
            "January."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-006",
        "section": "space_planets",
        "date": "12/04/88",
        "author": "NEPTUNE2",
        "subject": "Voyager 2: Neptune in the sights",
        "body": (
            "Eight months to go. Voyager 2 is closing on Neptune for the "
            "August 1989 encounter -- the last of the grand tour flybys. "
            "We are talking about a planet we have never seen up close: "
            "dark blue methane atmosphere, maybe supersonic winds, and "
            "the big moon Triton with that cantaloupe terrain and "
            "possible nitrogen geysers. After the January 1986 Uranus "
            "flyby (remember Miranda, the most bizarre moon yet seen?), "
            "Neptune should be the grand finale. The imaging team says "
            "they are still improving the enhancement techniques that "
            "made the Uranus pictures so sharp. Who else is counting "
            "the months?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-007",
        "section": "space_planets",
        "date": "12/14/88",
        "author": "SIDEREAL",
        "subject": "Phobos 2's plan for Mars -- how the encounter works",
        "body": (
            "For those following the surviving Soviet probe: Phobos 2 "
            "arrives at Mars next month. The plan, as the Soviets have "
            "described it: enter Mars orbit, study the planet and its "
            "plasma environment, then maneuver down to within 50 meters "
            "of the surface of the moon Phobos and drop two landers -- "
            "one that hops across the surface on spring legs and one "
            "stationary package. The moonlet is only about 27 km across, "
            "so this is precision flying with 1988-era computers. If "
            "Phobos 1 had survived we would have two probes doing it. As "
            "it is, everything rides on Phobos 2. Anybody know the "
            "expected dates for the Mars orbit insertion burn?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-008",
        "section": "space_nasa",
        "date": "12/22/88",
        "author": "REDSHIFT",
        "subject": "One year in space -- Titov and Manarov are home",
        "body": (
            "Yesterday the Soviets brought down Soyuz TM-6 with Vladimir "
            "Titov and Musa Manarov after 365 days, 22 hours, 39 minutes "
            "aboard Mir -- the first humans to spend a full year in "
            "space, and a new endurance record. They broke Romanenko's "
            "326-day record on December 15 by the required margin. French "
            "cosmonaut Jean-Loup Chretien rode down with them, ending the "
            "Aragatz visit (including the December 9 spacewalk with "
            "Volkov, the first EVA by a non-Soviet, non-American). The new "
            "long-duration crew, Volkov and Krikalev, plus Polyakov, keep "
            "Mir occupied. A year in weightlessness -- and the Soviets "
            "are doing it routinely now. Impressive, whatever else you "
            "say about them."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-009",
        "section": "space_deepsky",
        "date": "12/03/88",
        "author": "GEMINID",
        "subject": "Geminids peak next week -- observing tips",
        "body": (
            "Mark your calendars: the Geminid meteor shower peaks the "
            "night of December 13-14. This is the best shower of the "
            "year for most of us -- slow, bright, often colorful meteors, "
            "sometimes over a hundred an hour under dark skies, and the "
            "radiant near Castor climbs high before midnight. Tips from "
            "years of watching: lie flat in a sleeping bag, face south "
            "and up, give your eyes twenty minutes to dark-adapt (no "
            "white flashlights -- red only), and bring a friend to call "
            "out the fireballs. Best after 10 PM when the radiant is "
            "high. Who has a dark site picked out?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-010",
        "section": "space_deepsky",
        "date": "12/09/88",
        "author": "ORIONHAWK",
        "subject": "Winter's showpiece sky",
        "body": (
            "December evenings belong to Orion. From a dark site you get "
            "the Hunter rising in the east by 9 PM: Betelgeuse red on "
            "the shoulder, Rigel blue-white at the foot, the Belt, and "
            "the sword with M42, the Orion Nebula -- the finest deep-sky "
            "object in the northern winter sky, visible in binoculars. "
            "Above Orion rides Taurus with Aldebaran and the Hyades, and "
            "the Pleiades (M45) glittering higher up. To the northeast "
            "Capella blazes in Auriga, and Castor and Pollux stand over "
            "Orion in Gemini. New observers: start with 7x50 binoculars "
            "and a planisphere before you buy anything. The sky does the "
            "heavy lifting this month."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-011",
        "section": "space_scopes",
        "date": "12/06/88",
        "author": "APERTURE8",
        "subject": "C8 vs. Meade 2080 vs. Dobsonian -- where to put $1000?",
        "body": (
            "Christmas money burning a hole in my pocket and I have about "
            "a thousand to spend. Choices I am weighing: a Celestron C8 "
            "(the 8-inch Schmidt-Cassegrain, compact and portable, great "
            "all-arounder), a Meade 2080 in the same class, or a big "
            "Dobsonian -- you can get 8 or even 10 inches of light-gathering "
            "Newtonian on a simple alt-az mount for the same money or less. "
            "The SCTs win on portability and tracking for photography; "
            "the Dob wins on raw aperture per dollar and simplicity. I "
            "observe mostly deep sky from a suburban driveway. For those "
            "who went the Dob route: do you miss having a clock drive? "
            "And for SCT owners: how is the cool-down time in winter?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-012",
        "section": "space_scopes",
        "date": "12/10/88",
        "author": "STARRYNITE",
        "subject": "First scope advice for a beginner?",
        "body": (
            "Total beginner here, bitten by the Geminids. What should a "
            "first telescope be? I keep reading that a 4.25-inch or "
            "6-inch Newtonian reflector on a simple mount is the classic "
            "starter -- affordable, easy to use, shows the Moon, planets, "
            "and brighter deep-sky objects. The department-store 60mm "
            "refractors with wobbly mounts get terrible reviews. Should "
            "I buy new or hunt the used market? Also: is it crazy to "
            "start with just good binoculars and a star chart for a few "
            "months? Budget is tight (student), so every dollar counts."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-013",
        "section": "space_scopes",
        "date": "12/13/88",
        "author": "FILMSTRO",
        "subject": "Astrophotography with film: getting started",
        "body": (
            "Since there is no shortcut around it yet, "
            "we do it the hard way: film. For beginners, piggyback "
            "photography is the entry point -- mount a 35mm SLR with a "
            "fast 50mm or 135mm lens on top of your tracking scope and "
            "shoot 5-15 minute exposures of constellations and the Milky "
            "Way. Through the scope, you need an off-axis guider or "
            "guidescope and a steady hand on the slow-motion controls "
            "for 20-60 minute exposures. Film choice: Tri-X pushed for "
            "speed, or gas-hypered (baked in forming gas) film for real "
            "deep-sky work -- the hypering shops advertise in the back of "
            "the magazines. Kodak 103a is the classic long-exposure "
            "emulsion. Who here is guiding by hand, and what is your "
            "longest successful exposure?"
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-014",
        "section": "space_nasa",
        "date": "12/16/88",
        "author": "COSMOKID",
        "subject": "Looking ahead: the 1989 launch manifest",
        "body": (
            "With two shuttle flights under our belts since the return "
            "to flight, next year is shaping up to be the real test of "
            "the recovery. On the schedule as I understand it: STS-29 "
            "on Discovery in February with TDRS-4; then the planetary "
            "science starts -- Magellan to Venus on Atlantis in May, the "
            "first planetary launch from a shuttle; and Galileo to "
            "Jupiter late in the year. Talk is of around eight flights "
            "for 1989. After Challenger, hitting that cadence safely is "
            "the whole ballgame. Which mission are you most excited "
            "about? For me it is Magellan -- mapping Venus with radar "
            "through the clouds is going to rewrite the textbooks."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-015",
        "section": "space_starparty",
        "date": "12/17/88",
        "author": "NIGHTOWL",
        "subject": "Club star party: December 30 at the dark-sky site",
        "body": (
            "Our club is holding its winter star party on Friday, "
            "December 30 at the usual dark-sky site (the ranch turnout "
            "on County Road 12, about 40 miles west of town). Gates open "
            "at sunset, observing starts when it gets properly dark. "
            "Bring red flashlights only (white light = you walk the "
            "perimeter), warm clothes -- it will be below freezing by "
            "midnight -- and a thermos. New members welcome; several of "
            "us are bringing spare scopes and binoculars for look-through. "
            "RSVP in this thread so we know how much coffee to brew. "
            "Geminids may be past peak but Orion will be glorious."
        ),
        "parent": None,
    },
    {
        "content_id": "space-1988-016",
        "section": "space_starparty",
        "date": "12/28/88",
        "author": "LUNARTIC",
        "subject": "Texas Star Party countdown -- first-timer questions",
        "body": (
            "I have finally decided: I am going to the Texas Star Party "
            "in May at the Prude Ranch in the Davis Mountains. "
            "First-timer questions for the veterans: how dark is it "
            "really compared to my suburban backyard (honestly)? What "
            "should I bring besides the obvious (red flashlight, warm "
            "gear, dew shield)? Is it worth driving my 8-inch out, or "
            "should I travel light and borrow eyepiece time at other "
            "people's scopes? And the big one: how far in advance do I "
            "need to register? Five months feels like forever and like "
            "no time at all."
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
