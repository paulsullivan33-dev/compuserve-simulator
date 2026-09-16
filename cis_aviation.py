"""Aviation Forum content module.

Section spec and December 1988 seed posts for the ``aviation`` forum
("Aviation Forum"): private pilots, IFR training, aircraft
ownership, Flight Simulator, trip reports, and hangar talk.

Period rules enforced by this module:
* General aviation is December 1988: Cessna 152/172N Skyhawk, Piper
  Cherokee/Archer II, Beech Bonanza V35B/A36, Mooney 201 (M20J),
  Cessna 182, Piper Arrow. Navigation is VOR, ADF, DME, and Loran-C
  (II Morrow); weather comes from Flight Service briefings and
  transcribed TWEB. No glass-cockpit GPS, no moving-map tablets,
  no flight-planning apps.
* Flight Simulator 3.0 (Microsoft/subLOGIC, 1988) is the current
  release: EGA graphics, scenery disks, frame rates on 286-class
  machines, analog joysticks on the game port.
* Trip memories are summer 1988 (EAA Oshkosh fly-in, Wittman
  Field). Nothing references anything after December 1988.
"""

FORUM_ID = "aviation"
FORUM_TITLE = "Aviation Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("aviation_private", "Private Pilots"), ...}
# The coordinator wires this into FORUM_CATALOG["aviation"]["sections"].
SECTIONS = {
    "1": ("aviation_private", "Private Pilots"),
    "2": ("aviation_ifr", "IFR Training"),
    "3": ("aviation_ownership", "Aircraft Ownership"),
    "4": ("aviation_sim", "Flight Simulator"),
    "5": ("aviation_trips", "Trip Reports"),
    "6": ("aviation_hangar", "Hangar Talk"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "aviation-1988-001",
        "section": "aviation_private",
        "date": "12/01/88",
        "author": "AviatorSysop",
        "subject": "Welcome to the Aviation Forum",
        "body": (
            "Welcome aboard, pilots and pilots-to-be. This is the place "
            "for all things flying: student questions and checkride "
            "stories in Private Pilots, instrument training in IFR "
            "Training, the joys and bills of Aircraft Ownership, our "
            "Flight Simulator corner for the Microsoft Flight Simulator "
            "3.0 crowd, Trip Reports from your cross-countries, and "
            "general Hangar Talk. New here? Introduce yourself, tell us "
            "what you fly (or what you are learning in), and your home "
            "field. House rule: no scud-running stories told as advice. "
            "Fly safe."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-002",
        "section": "aviation_private",
        "date": "12/02/88",
        "author": "SOLOFLIER",
        "subject": "Soloed today! N7342G and me",
        "body": (
            "It finally happened -- this afternoon my instructor hopped "
            "out at the hold-short line, said 'three takeoffs and "
            "landings, stay in the pattern,' and I soloed N7342G, our "
            "club's 152. First takeoff I climbed like a homesick angel "
            "and had to remind myself to breathe. The landings were not "
            "pretty but they were all on the runway and the airplane is "
            "reusable, which my CFI tells me is the whole grading "
            "system. Back at the hangar they cut my shirttail and hung "
            "it on the bulletin board. Twenty-two hours total time and "
            "I am still grinning. For the students still pre-solo: it "
            "really does happen exactly when your instructor stops "
            "touching the controls."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-003",
        "section": "aviation_private",
        "date": "12/04/88",
        "author": "TAILDRAGGER88",
        "subject": "Cross-country solo next week -- planning tips?",
        "body": (
            "My long cross-country solo is scheduled for next week: "
            "about 160 nm each way with a fuel stop, in a 172N. I have "
            "the sectional marked up, checkpoints picked every 10-15 "
            "miles, and my nav log filled out with the E6B. For those "
            "who have done it: what actually helped, and what was a "
            "waste of time? My CFI insists I file a flight plan with "
            "Flight Service and get a full standard briefing the "
            "morning of. Also, dead reckoning vs. pilotage -- did you "
            "guys mostly fly the compass heading, or just follow the "
            "highway and the checkpoints? Trying not to overthink it, "
            "but I want to do this right."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-004",
        "section": "aviation_ifr",
        "date": "12/06/88",
        "author": "SIXPACKIFR",
        "subject": "IFR written next month -- how did you study?",
        "body": (
            "Sitting for the instrument written in January and working "
            "through the ASA test prep book now. The question bank is "
            "huge -- regs, weather theory, IFR charts and approach "
            "plates, holding entries, lost-comm procedures. For those "
            "who passed recently: did you just grind practice tests "
            "until the scores stuck, or did you study the underlying "
            "material first and then test? I keep hearing 'learn the "
            "bank, pass the test, learn to fly IFR from your CFII,' "
            "which feels cynical, but the holding-pattern entry "
            "questions alone are eating my lunch. Any study system that "
            "actually worked for you?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-005",
        "section": "aviation_ifr",
        "date": "12/08/88",
        "author": "APPROACHPLATE",
        "subject": "Building instrument time on the cheap: safety pilots?",
        "body": (
            "Working on the instrument rating and the Hobbs meter is "
            "killing me. A few pilots at the field suggested splitting "
            "time: I fly under the hood as the sole manipulator, a "
            "private-pilot friend rides along as safety pilot, and we "
            "each log the time we are entitled to. Done right, my "
            "hourly cost gets cut nearly in half. For those doing "
            "this: how do you handle the logging so both logbooks are "
            "defensible, and how do you pick a safety pilot you trust "
            "to actually watch for traffic? Also, does hood time in "
            "the right seat of a 172 feel different enough to matter, "
            "or should I always fly from the left?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-006",
        "section": "aviation_ownership",
        "date": "12/05/88",
        "author": "TIEDOWN",
        "subject": "100-hour inspection bill shock -- is this normal?",
        "body": (
            "Our club's Cherokee just came out of its 100-hour and the "
            "bill was just under nine hundred dollars. Compressions "
            "were fine, but they found a cracked exhaust stack, two "
            "tires that 'would not make another hundred hours,' and "
            "the seat-rail AD inspection that has to be logged every "
            "100 hours now. I know 100-hours are the price of renting "
            "the airplane out, but this feels steep for an airplane "
            "that flew fine going in. Owners and club mechanics: what "
            "does a typical 100-hour run you, and what separates the "
            "honest squawks from the shop padding the ticket? Trying "
            "to decide if we need a second quote next time."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-007",
        "section": "aviation_ownership",
        "date": "12/09/88",
        "author": "PARTNERPAUL",
        "subject": "4-way Cherokee partnership math -- check my numbers",
        "body": (
            "Four of us are looking at a 1979 Archer II, mid-time "
            "engine, decent paint, asking in the high thirties. The "
            "plan: each partner buys in for a quarter of the price "
            "plus a $1,500 reserve contribution, then we charge "
            "ourselves a dry hourly rate to cover the engine reserve "
            "and share fixed costs (hangar, insurance, annual) four "
            "ways. Back of the envelope, fixed costs run about $550 a "
            "month total, so roughly $140 each, plus maybe $35 an hour "
            "dry into the reserve. For those in partnerships: does "
            "that math hold up in the real world, and what broke your "
            "budget the first year -- the annual, the insurance, or "
            "the thing nobody saw coming? Also, how do you handle "
            "scheduling conflicts in the summer?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-008",
        "section": "aviation_ownership",
        "date": "12/11/88",
        "author": "PREBUYPRO",
        "subject": "Pre-buy on a '79 172N -- what to watch for?",
        "body": (
            "Seriously considering a 1979 172N, about 2,400 hours total "
            "time and 900 since major on the O-320-H2AD. Price looks "
            "fair, logs look complete, and the owner says the annual "
            "is fresh. Before I pay for a pre-buy with an independent "
            "A&P, what are the model-specific gotchas? I know the H2AD "
            "has the lifter/cam history to check, and I want the seat "
            "rails and the spar carry-through looked at for corrosion. "
            "The panel has a Loran-C unit the owner swears by -- is "
            "that a plus or just a box I will be paying to remove in "
            "two years? What would you put on the pre-buy checklist "
            "that a generic annual might miss?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-009",
        "section": "aviation_sim",
        "date": "12/07/88",
        "author": "PIXELPILOT",
        "subject": "Flight Simulator 3.0 on a 286 -- what frame rates?",
        "body": (
            "Finally upgraded to Flight Simulator 3.0 and I am trying "
            "to figure out what machine it really wants. On my 10 MHz "
            "286 with EGA I get maybe 5 to 8 frames a second over "
            "detailed scenery, less turning final at Meigs with the "
            "windows up. It is flyable, but barely. For those running "
            "3.0: what are you getting, and what made the biggest "
            "difference -- a faster 286, more memory, or just turning "
            "down the scenery density? Wondering whether a 16 MHz "
            "machine is worth it, or if I should just fly the "
            "sparser areas and enjoy the smoother ride."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-010",
        "section": "aviation_sim",
        "date": "12/12/88",
        "author": "EGAACE",
        "subject": "FS 3.0 scenery disks -- which to buy first?",
        "body": (
            "The new scenery disks for 3.0 are stacking up and I can "
            "only justify one this Christmas. The Western European "
            "Tour disk looks amazing in the screenshots -- the Alps "
            "in EGA actually look like mountains -- but most of my "
            "flying is still the default Chicago area and the San "
            "Francisco disk. For those who have bought in: which disk "
            "gave you the most flying for the money, and do the older "
            "scenery disks still work properly under 3.0? Also, does "
            "anyone actually fly the Learjet across the Atlantic on "
            "the European disk, or is that a twelve-hour exercise in "
            "watching pixels?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-011",
        "section": "aviation_sim",
        "date": "12/14/88",
        "author": "SCRNFLY",
        "subject": "CH Flightstick vs. Kraft joystick for FS 3.0?",
        "body": (
            "Keyboard flying in 3.0 is getting old and I want a real "
            "stick on the game port. The shop has the CH Products "
            "Flightstick and the Kraft KC3 side by side, about the "
            "same money. The CH has that nice tall grip and the "
            "trigger plus top button, but the Kraft feels a little "
            "tighter on center. For those flying 3.0 with a stick: "
            "which did you pick, and how is the calibration holding "
            "up? Any tricks for getting the null zone right so the "
            "Sopwith does not wander off on the runway? Also curious "
            "whether anyone is using rudder pedals with the sim yet, "
            "or if that is overkill for a desktop."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-012",
        "section": "aviation_trips",
        "date": "12/10/88",
        "author": "OSHKOSHORBUST",
        "subject": "Oshkosh '88 memories -- Dallas to OSH in a 172",
        "body": (
            "Still thinking about the trip to Oshkosh back in August. "
            "Flew our club 172 up from Dallas over two days: first leg "
            "to the Ozarks, overnight in Springfield, then the long "
            "haul across Iowa and Wisconsin into the NOTAM arrival. "
            "Nothing prepares you for the conga line on final to "
            "Wittman -- rock your wings, keep it tight, land on the "
            "colored dot they give you. We camped under the wing for "
            "five days, walked ten miles a day through the homebuilt "
            "rows and the warbird line, and watched the night airshow "
            "from a lawn chair. Already saving for next year. Who else "
            "made it in '88, and what was your route?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-013",
        "section": "aviation_trips",
        "date": "12/16/88",
        "author": "RUNWAYROVER",
        "subject": "$100 hamburger run: Fredericksburg",
        "body": (
            "Needed an excuse to fly last Saturday, so three of us "
            "took the Archer down to Fredericksburg for the famous "
            "pie run. Cold front had just passed, sky was that "
            "impossible Texas winter blue, and the headwind home made "
            "sure the 'hundred-dollar hamburger' lived up to its "
            "name. Gillespie County was busy -- looked like half the "
            "Hill Country had the same idea. Pro tip: get there "
            "before 11 or the wait eats your whole afternoon, and "
            "lean aggressively on the way home because that norther "
            "will cost you 20 knots. What is your go-to $100 "
            "hamburger destination? I need a new one for January."
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-014",
        "section": "aviation_hangar",
        "date": "12/13/88",
        "author": "CROSSWINDKID",
        "subject": "Winter flying tips for a new private pilot",
        "body": (
            "Got my ticket in October and now winter is here. The "
            "172 flies like a rocket in the cold dense air, but I "
            "am nervous about the stuff I have not dealt with yet: "
            "carb ice on descent, frost on the wings (I know -- "
            "polish it off, no exceptions), preheating when it is "
            "below freezing, and short winter days turning a day "
            "trip into a night return. Experienced cold-weather "
            "pilots: what is in your winter survival kit, how cold "
            "is too cold to start without preheat, and any tricks "
            "for keeping the windshield clear on the ground? Also, "
            "does anyone actually enjoy flying in January, or is "
            "everyone just enduring it?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-015",
        "section": "aviation_hangar",
        "date": "12/18/88",
        "author": "RUDDERKICK",
        "subject": "Bonanza V-tail vs. straight-tail -- settle it",
        "body": (
            "Hangar debate last night got heated, so I am bringing it "
            "here: the V-tail Bonanza versus the straight-tail. The "
            "V-tail crowd says it is the best-looking airplane ever "
            "built and cruises faster on the same fuel; the "
            "straight-tail crowd says the 36 is the honest load-"
            "hauler and the old 'doctor killer' talk was always "
            "about pilots, not airframes. Having flown behind both, "
            "I think the V-tail demands more rudder discipline in "
            "turbulence and rewards it with speed. Where do you "
            "land? And for the owners: what does a mid-70s V35B "
            "actually cost to keep in annual these days versus an "
            "A36 of the same vintage?"
        ),
        "parent": None,
    },
    {
        "content_id": "aviation-1988-016",
        "section": "aviation_hangar",
        "date": "12/20/88",
        "author": "NIGHTOWL172",
        "subject": "Night cross-country jitters",
        "body": (
            "Did my first real night cross-country last week and I "
            "have to admit it rattled me more than I expected. "
            "Departing a lit runway into a black hole over the "
            "countryside, the horizon just... disappears, and you "
            "are on the gauges whether you planned to be or not. "
            "I kept the VOR needles centered and the checkpoints "
            "came up on time, but my scan was ragged and I was "
            "behind the airplane the whole way. Night-current "
            "pilots: does it ever feel routine, or do you just get "
            "better at managing the workload? Any personal minimums "
            "you set for night VFR -- moonlight, ceilings, routes "
            "over lit ground only?"
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
