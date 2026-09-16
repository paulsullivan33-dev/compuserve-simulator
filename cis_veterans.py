"""Veterans Forum content module.

Section spec and December 1988 seed posts for the ``veterans`` forum
("Veterans Forum"). Seed-post field format matches
computer_communities.json message entries
(content_id/section/date/author/subject/body/parent); the coordinator
appends them to that file and cis_communities.install() merges them
into forums.json on startup.

Period rules enforced by this module:
* Respectful tone throughout.
* VA Benefits content is 1988-era only: the Montgomery GI Bill (1984),
  VA home loans, the Agent Orange Registry, and VA medical care.
* The Wall is the Vietnam Veterans Memorial in Washington, D.C.,
  dedicated in 1982. Remembrance posts, rubbing requests, and
  panel/line references are period-appropriate.
* Service Stories carry WWII / Korea / Vietnam-era voices. Nothing in
  this module references anything after December 1988 -- no later
  conflicts, benefits, or legislation appear anywhere here.
"""

FORUM_ID = "veterans"
FORUM_TITLE = "Veterans Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("veterans_stories", "Service Stories"), ...}
# The coordinator wires this into FORUM_CATALOG["veterans"]["sections"].
SECTIONS = {
    "1": ("veterans_stories", "Service Stories"),
    "2": ("veterans_reunions", "Reunions & Buddy Finder"),
    "3": ("veterans_benefits", "VA Benefits"),
    "4": ("veterans_wall", "The Wall Remembrance"),
}

SEED_POSTS = [
    {
        "content_id": "veterans-1988-001",
        "section": "veterans_stories",
        "date": "12/01/88",
        "author": "SARGE88",
        "subject": "Welcome to the Veterans Forum",
        "body": (
            "Welcome, brothers and sisters in arms. This forum is a place "
            "for all who served -- Army, Navy, Air Force, Marines, and Coast "
            "Guard -- to swap stories, track down old buddies, get straight "
            "answers about VA benefits, and remember those who did not come "
            "home. Take a look around: Service Stories for your memories, "
            "Reunions & Buddy Finder for tracking down your unit, VA "
            "Benefits for the latest on the GI Bill and VA programs, and "
            "The Wall Remembrance for honoring our fallen. Introduce "
            "yourselves and mind your manners -- this is hallowed ground."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-002",
        "section": "veterans_stories",
        "date": "12/02/88",
        "author": "OMAHA_44",
        "subject": "Omaha Beach, June 6, 1944",
        "body": (
            "I was nineteen when our Higgins boat dropped its ramp on Omaha "
            "Beach. Forty-four years later I can still hear the engines and "
            "feel the cold Channel water. Half the boys from my squad never "
            "made it past the shingle. I go back every few years to "
            "Normandy to stand at the cemetery at Colleville and read the "
            "names. To the young folks here: freedom was bought at a price, "
            "and I have spent my life trying to be worthy of the men who "
            "paid it. God rest them all."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-003",
        "section": "veterans_stories",
        "date": "12/04/88",
        "author": "CHOSIN50",
        "subject": "Chosin Reservoir, winter of 1950",
        "body": (
            "Thirty-eight years ago this month we were fighting our way out "
            "of the Chosin Reservoir in forty-below cold. Men froze to their "
            "sleeping bags. We called ourselves the Chosin Few, and every "
            "year there are fewer of us at the reunion. Korea is called the "
            "Forgotten War, but nobody who was there has forgotten a thing. "
            "If any 1st Marine Division vets from that winter are reading "
            "this, I would be proud to hear from you. Semper Fi."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-004",
        "section": "veterans_stories",
        "date": "12/06/88",
        "author": "HUE_68",
        "subject": "Hue City, Tet 1968",
        "body": (
            "Twenty years ago this coming February my platoon fought house "
            "to house through Hue City. It was the hardest month of my life "
            "and the proudest. I lost my best friend on the third day, and "
            "I think of him every single day since. Coming home was harder "
            "than I expected -- nobody wanted to talk about it then. I am "
            "glad there is a place like this now where a man can tell his "
            "story among people who understand. Welcome home, brothers. It "
            "is never too late to hear it."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-005",
        "section": "veterans_reunions",
        "date": "12/03/88",
        "author": "GRUNT67",
        "subject": "Looking for 1/7 Cav buddies, 1967-68",
        "body": (
            "Trying to locate anyone who served with B Company, 1st "
            "Battalion, 7th Cavalry in Vietnam, 1967 to 1968. I was a "
            "squad leader, went by the nickname Tex. I have been thinking "
            "about Smitty from Ohio and Deacon from Georgia -- we came home "
            "on the same freedom bird in March of 68. If you know them or "
            "served alongside us, please reply here. Twenty years is too "
            "long to lose touch."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-006",
        "section": "veterans_reunions",
        "date": "12/05/88",
        "author": "FLATOP63",
        "subject": "USS Enterprise (CVN-65) reunion -- Norfolk, July 1989",
        "body": (
            "Mark your calendars: the USS Enterprise Association reunion "
            "will be held in Norfolk, Virginia, July 14-16, 1989. All "
            "plankowners and crew from every cruise are invited -- bring "
            "your families. Events include a memorial service, a tour of "
            "the ship if she is in port, and the Saturday night banquet. "
            "Dues are $25 per person; contact the association through the "
            "address in the latest newsletter. I was aboard for the 1965-66 "
            "cruise and would love to see some familiar faces."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-007",
        "section": "veterans_reunions",
        "date": "12/08/88",
        "author": "DOCMEDIC",
        "subject": "Searching for 71st Evac Hospital nurses, 1969",
        "body": (
            "I was a corpsman with the 71st Evacuation Hospital at Pleiku in "
            "1969, and I have never forgotten the nurses who worked those "
            "long nights beside us. I am trying to find Lieutenant Karen "
            "M., a surgical nurse from Pennsylvania, and the rest of the "
            "night-shift crew. You saved a lot of young lives, and some of "
            "us would like to say thank you properly after all these years. "
            "Please reply here if you can help."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-008",
        "section": "veterans_reunions",
        "date": "12/10/88",
        "author": "AIRBORNE82",
        "subject": "82nd Airborne Division Assn. reunion, Fayetteville",
        "body": (
            "The 82nd Airborne Division Association will hold its annual "
            "reunion in Fayetteville, North Carolina, August 10-13, 1989. "
            "All paratroopers past and present are welcome, all eras. "
            "There will be a memorial ceremony at the division museum, a "
            "picnic, and the traditional Saturday dance. Registration is "
            "$35 and includes the banquet. I jumped with the 505th in the "
            "early 60s and have not missed a reunion in ten years. Airborne, "
            "all the way -- hope to see you there."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-009",
        "section": "veterans_benefits",
        "date": "12/07/88",
        "author": "COLLEGEBOUND",
        "subject": "Montgomery GI Bill -- how do I apply?",
        "body": (
            "I got out of the Army in June and want to start college in "
            "January using the Montgomery GI Bill. I had the $100 a month "
            "taken out of my pay for my first twelve months in, so I should "
            "be eligible under the 1984 law. What is the actual process? Do "
            "I apply through the VA regional office first, or enroll in "
            "school and let the school certify me? Any advice from someone "
            "who has already navigated the paperwork would be appreciated. "
            "I want to get this right the first time."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-010",
        "section": "veterans_benefits",
        "date": "12/09/88",
        "author": "HOMESTEAD",
        "subject": "VA home loan questions",
        "body": (
            "My wife and I are looking at our first house and I want to use "
            "my VA home loan benefit. I served four years in the Navy, "
            "honorable discharge in 1984. Am I correct that there is no "
            "down payment required and no private mortgage insurance? Also, "
            "can the entitlement be reused if I sell the house later? The "
            "lender I talked to did not seem to know much about VA loans, "
            "so I would rather hear from veterans who have actually used "
            "one. Thanks in advance."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-011",
        "section": "veterans_benefits",
        "date": "12/12/88",
        "author": "JUNGLE69",
        "subject": "Agent Orange Registry exam -- my experience",
        "body": (
            "For anyone who served in Vietnam and has been putting it off: "
            "I finally went in for my Agent Orange Registry exam at the VA "
            "medical center last month. It is free, it took about half a "
            "day, and the doctor went through a full history and physical. "
            "The registry was set up so the VA can track health effects, "
            "and getting the exam on record is the smart move whether you "
            "feel fine or not. Call your local VA and ask for the Agent "
            "Orange coordinator -- they will schedule you. Take care of "
            "yourselves, brothers."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-012",
        "section": "veterans_benefits",
        "date": "12/14/88",
        "author": "DAKTO67",
        "subject": "VA medical care eligibility?",
        "body": (
            "Question for the group: I have a service-connected knee injury "
            "rated at 30 percent from Vietnam, 1967. Am I eligible for VA "
            "medical care for the knee only, or for general care too? I "
            "have been paying out of pocket for everything and only just "
            "learned I might qualify for treatment at the VA hospital. "
            "Also, is there a means test involved these days? I do not want "
            "to take a slot from someone who needs it more, but my knee is "
            "getting worse. Straight answers appreciated."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-013",
        "section": "veterans_wall",
        "date": "12/11/88",
        "author": "BROTHERINK",
        "subject": "Found my buddy's name on the Wall",
        "body": (
            "I finally made the trip to Washington last month and stood "
            "before the Vietnam Veterans Memorial. I found my buddy Danny "
            "on Panel 23E, and I made a rubbing of his name to bring home "
            "to his mother. The Wall is exactly as powerful as everyone "
            "says -- 58,000 names, and every one of them somebody's son or "
            "daughter. I left my unit patch at the base of his panel. If "
            "you have never been, go. It heals something in you."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-014",
        "section": "veterans_wall",
        "date": "12/13/88",
        "author": "PANEL23E",
        "subject": "Rubbing request -- Panel 12W, Line 114",
        "body": (
            "Is anyone planning a trip to Washington, D.C., soon? I am "
            "hoping someone can make a pencil rubbing of a name on the "
            "Vietnam Veterans Memorial for me: Panel 12W, Line 114. He was "
            "my platoon sergeant in 1968, and I cannot make the trip myself "
            "this year. I will gladly cover postage and supplies. Please "
            "reply here if you can help -- it would mean the world to his "
            "family and to me."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-015",
        "section": "veterans_wall",
        "date": "12/16/88",
        "author": "VIGILANT",
        "subject": "Veterans Day at the Wall",
        "body": (
            "I spent Veterans Day, November 11th, at the Vietnam Veterans "
            "Memorial this year, and I wanted to share it with those who "
            "could not be there. Hundreds of us stood in the cold as the "
            "wreaths were laid and the names of the fallen were read. "
            "Strangers helped each other find panels. A Gold Star mother "
            "next to me was tracing her son's name with her fingertip, and "
            "not a dry eye in sight. We remember them. We will always "
            "remember them."
        ),
        "parent": None,
    },
    {
        "content_id": "veterans-1988-016",
        "section": "veterans_wall",
        "date": "12/17/88",
        "author": "CANDLELIGHT",
        "subject": "A candle for the MIAs",
        "body": (
            "This Christmas season, I am lighting a candle for the men "
            "still listed as missing in action -- ours and every family's "
            "who never got an answer. The Wall carries their names too, "
            "marked with the cross that means missing, and their families "
            "visit those panels with the same grief and the same pride. "
            "Until every one of them is accounted for, we keep the faith "
            "and we keep their memory alive. You are not forgotten."
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
