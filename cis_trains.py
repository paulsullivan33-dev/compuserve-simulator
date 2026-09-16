"""Model Railroading Forum content module.

Section spec and December 1988 seed posts for the ``trains`` forum
("Model Railroading Forum"): Layout Design, DCC & Wiring, Locomotives,
Scenery, Prototype Research, and Buy/Sell/Trade.

Period rules enforced by this module:
* Command control is framed as EARLY command control, not modern DCC.
  As of December 1988 the NMRA has not published a digital command
  control standard -- posts discuss the carrier-control systems
  actually available in the 1980s (CTC-16, Dynatrol, Hornby Zero 1)
  as expensive, limited, proprietary choices, and treat any talk of
  an NMRA standard as speculation and opinion, not fact. Decoder,
  consisting, and sound-onboard talk in the modern sense is absent.
  Ordinary DC block wiring with cab control remains the norm.
* Equipment is 1988-plausible: Athearn blue-box kits, Atlas and Kato
  ready-to-run, Roundhouse, Bachmann, brass imports (PFM, United,
  Key, Overland), Kadee couplers, nickel-silver rail. No post-1988
  product lines are mentioned.
* Scales mentioned are HO, N, O, and O-27/Lionel -- no Z-scale
  renaissance talk, no post-1988 scale trends.
* Christmas garden layouts and holiday train talk are December-
  appropriate; hobby press is Model Railroader, Railroad Model
  Craftsman, TRAINS, and club newsletters.
* Nothing references the internet, websites, blogs, email, eBay,
  digital product announcements, or anything else after December
  1988. Buying and selling is done by mail, at shows, and through
  magazine classifieds.
"""

from pathlib import Path

# Repo root, derived so paths are never hardcoded.
REPO_ROOT = Path(__file__).resolve().parent

FORUM_ID = "trains"
FORUM_TITLE = "Model Railroading Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("trains_layout", "Layout Design"), ...}
# The coordinator wires this into FORUM_CATALOG["trains"]["sections"].
SECTIONS = {
    "1": ("trains_layout", "Layout Design"),
    "2": ("trains_dcc", "DCC & Wiring"),
    "3": ("trains_locos", "Locomotives"),
    "4": ("trains_scenery", "Scenery"),
    "5": ("trains_prototype", "Prototype Research"),
    "6": ("trains_trade", "Buy/Sell/Trade"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "trains-1988-001",
        "section": "trains_layout",
        "date": "12/01/88",
        "author": "SysopSwitchman",
        "subject": "Welcome to the Model Railroading Forum -- all aboard",
        "body": (
            "Welcome to the roundhouse. This forum has six sections: "
            "Layout Design (track plans, benchwork, room-size debates), "
            "DCC & Wiring (block wiring, cab control, and the new "
            "command-control systems -- note that as of late 1988 the NMRA "
            "has NOT settled on a digital standard, so buyer beware), "
            "Locomotives (brass versus plastic, steam versus diesel), "
            "Scenery (plaster, foam, and backdrops), Prototype Research "
            "(magazines, photos, and railfan trips), and Buy/Sell/Trade "
            "(hobbyist to hobbyist, be honest about condition). Whether "
            "you run HO, N, O, or a Lionel loop under the tree, pull up "
            "a chair and tell us what is on your rails."
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-002",
        "section": "trains_layout",
        "date": "12/03/88",
        "author": "TREELOOP",
        "subject": "The Christmas garden layout -- who is running trains under the tree?",
        "body": (
            "It is December, so the most important layout in America is "
            "the one around the Christmas tree. Ours is O-27 on a 4x6 "
            "plywood sheet with cotton batting snow, a Plasticville "
            "village, and my 1975 Lionel steamer pulling four cars -- the "
            "kids are three and five and they believe the engineer waves "
            "at them. Every year I tell myself I will build a proper "
            "scenic base for it, and every year the tree goes up and the "
            "plywood goes down bare. For those with permanent layouts: do "
            "you build a separate holiday loop, or does the main railroad "
            "get Christmas decorations? And O-gaugers: what is the one "
            "accessory your tree layout cannot live without?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-003",
        "section": "trains_dcc",
        "date": "12/04/88",
        "author": "BLOCKOPERATOR",
        "subject": "Command control in 1988 -- CTC-16, Dynatrol, or stick with blocks?",
        "body": (
            "I keep reading about command control -- run two trains on "
            "the same track, independent control, no block toggles -- "
            "and I keep not buying it, because the choices scare me. "
            "CTC-16 is the hobbyist-built system from the magazine "
            "articles: clever, cheap if you can solder, but you are on "
            "your own when it breaks. Dynatrol is a commercial system "
            "with real support, but it is proprietary and pricey. Hornby's "
            "Zero 1 has been around for years across the pond. And hanging "
            "over all of it: my understanding is the NMRA has not picked "
            "a standard yet, so anything I buy today could be orphaned "
            "tomorrow. That is my read of the situation -- correct me if "
            "I am wrong. For a 12x16 HO layout with two operators: is "
            "command control worth the risk in December 1988, or do I "
            "wire blocks and wait?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-004",
        "section": "trains_dcc",
        "date": "12/06/88",
        "author": "CABCONTROL",
        "subject": "DC block wiring done right -- my cab-control recipe",
        "body": (
            "Until the command-control people settle their standards war, "
            "the rest of us are wiring blocks, so let us do it properly. "
            "My recipe for a two-cab HO layout: divide the main into "
            "blocks no longer than your longest train plus a little, gap "
            "ONE rail per block boundary (insulated rail joiners, do not "
            "just cut and hope), feed each block through a DPDT "
            "center-off toggle to select cab A, cab B, or off, and run a "
            "heavy bus wire under the benchwork so voltage does not sag "
            "at the far end. Label every toggle on a track diagram taped "
            "to the fascia -- future you will thank present you. Common "
            "rail versus two-rail gapping is a religious war I will not "
            "start here. What is your block length rule of thumb, and "
            "what wiring mistake taught you the most?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-005",
        "section": "trains_locos",
        "date": "12/07/88",
        "author": "BRASSHUNTER",
        "subject": "Brass vs. plastic -- the debate that will outlive us all",
        "body": (
            "Time to have the fight. Brass imports -- PFM, United, Key, "
            "Overland -- are gorgeous, heavy, and priced like used cars. "
            "A brass 2-8-0 will pull the paint off the walls and look "
            "right doing it. Plastic -- Athearn, Atlas, Kato -- costs a "
            "tenth as much, runs out of the box, and the new Kato and "
            "Atlas diesels run smoother than half the brass I have owned. "
            "My position: brass for the locomotive you will photograph "
            "for the rest of your life, plastic for the fleet that "
            "actually earns its keep in operating sessions. Brass owners: "
            "what did you pay, and was it worth it? Plastic loyalists: "
            "which model finally convinced you brass was optional?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-006",
        "section": "trains_locos",
        "date": "12/09/88",
        "author": "BLUEBOXBOB",
        "subject": "Athearn blue-box kits -- still the best value in HO?",
        "body": (
            "I built three Athearn blue-box kits this month -- an F7, a "
            "GP38-2, and a 40-foot boxcar -- total cost under sixty bucks, "
            "total bench time about six pleasant evenings. Are they "
            "perfect? No: the handrails are chunky, the paint is thick, "
            "and the motors growl like a coffee grinder until you break "
            "them in. But they run, they pull, parts are everywhere, and "
            "a kid can afford them. Meanwhile the hobby press keeps "
            "raving about the new Kato and Atlas ready-to-run diesels "
            "with their silky drives and fine detailing -- at two to "
            "three times the price. So the question: for someone "
            "building a fleet on a budget in 1988, is the blue box still "
            "king, or has ready-to-run finally caught up on value?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-007",
        "section": "trains_scenery",
        "date": "12/12/88",
        "author": "PLASTERCLOTH",
        "subject": "Scenery that does not look like a wedding cake -- ground foam technique",
        "body": (
            "My first layout looked like a wedding cake -- white plaster "
            "hills with green sawdust glued on top. My current one "
            "does not, and the difference is layering. The method: shape "
            "the landform with crumpled newspaper and plaster cloth, "
            "paint the dried shell an earth brown (not white -- white "
            "shows through everything), then apply ground foam in at "
            "least three colors -- a dark base, a mid green, and a dry "
            "grass highlight -- with matte medium, not just white glue, "
            "so it stays put. Clump foliage for bushes, lichen for the "
            "cheap seats in the background. The single biggest upgrade "
            "for me was painting the plaster before foaming. What is "
            "the one scenery technique that took your layout from "
            "toy-like to believable?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-008",
        "section": "trains_locos",
        "date": "12/11/88",
        "author": "STEAMFOREVER",
        "subject": "Steam vs. diesel -- where do your loyalties lie?",
        "body": (
            "Every model railroader eventually picks a side, so declare "
            "yours. Steam: the romance, the sound (in our imaginations), "
            "the variety -- no two Consolidations alike, and a brass "
            "Pacific on the point of a passenger train is the most "
            "beautiful thing in the hobby. But steam models are "
            "fiddly, expensive, and short on pulling power in plastic. "
            "Diesel: the Athearn F-units and GPs run all day, MU "
            "together, and let you model the transition era or the "
            "modern road freights. Less romance, more reliability. I am "
            "a steam man with a diesel fleet for operating nights, which "
            "I realize is a coward's answer. What is your era, your "
            "road, and which side of the great divide are you on?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-009",
        "section": "trains_prototype",
        "date": "12/15/88",
        "author": "RAILFANRESEARCH",
        "subject": "Prototype research on a budget -- magazines, photos, and field trips",
        "body": (
            "I am modeling the Santa Fe in 1952 and I am drowning in "
            "questions: what color were the boxcars really, which "
            "depots had the curved tile roofs, did the way freights "
            "really stop at my town? My research stack: back issues of "
            "Model Railroader and Railroad Model Craftsman (the club "
            "library sells old ones for a quarter), TRAINS magazine for "
            "the prototype side, Morning Sun color books at the hobby "
            "shop (expensive but worth it), and -- best of all -- a "
            "Saturday railfan trip with a camera and a notebook. The "
            "local historical society had Sanborn maps showing every "
            "siding in 1951. How do you research your prototype? Any "
            "favorite books, photo collections, or field-trip tricks "
            "for nailing the details?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-010",
        "section": "trains_scenery",
        "date": "12/14/88",
        "author": "BACKDROPPAINTER",
        "subject": "Painting backdrops -- clouds without the cartoon look",
        "body": (
            "My backdrop clouds look like a cartoon -- white blobs on "
            "blue, and every visitor notices. I need help from the "
            "artists. What I have tried: latex house paint for the sky "
            "(a light blue, darker at the top), and clouds dabbed on "
            "with a sea sponge. What I get: sheep. What I want: the "
            "soft, distant, slightly gray-bottomed clouds in the "
            "magazine photos. I have read about airbrushing the sky "
            "gradient and dry-brushing the clouds, about keeping distant "
            "hills bluer and paler than the foreground, and about "
            "stopping the backdrop at the horizon instead of painting "
            "down to the benchwork. Backdrop veterans: what is the "
            "technique, the brush, or the color mix that finally made "
            "yours look like sky instead of wallpaper?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-011",
        "section": "trains_trade",
        "date": "12/18/88",
        "author": "SELLINGSTEAM",
        "subject": "FOR SALE: PFM brass 2-8-0 Consolidation, painted, runs well",
        "body": (
            "For sale to a good home: PFM brass 2-8-0 Consolidation, "
            "factory painted black, in the original box with foam. Runs "
            "smoothly, pulls ten cars on level track, drivers quartered "
            "correctly -- I had my repairman go through it last spring "
            "and it has run maybe two hours since. Selling because I am "
            "switching eras and the Consolidation does not fit the new "
            "plan. Asking $225 plus postage, or trade toward a brass "
            "Pacific in similar condition. I can describe any flaws "
            "honestly by mail -- no surprises, hobbyist to hobbyist. "
            "First reasonable offer takes it before the January show."
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-012",
        "section": "trains_trade",
        "date": "12/19/88",
        "author": "LIONELKID",
        "subject": "WANTED: postwar Lionel 736 Berkshire or 681 turbine",
        "body": (
            "Wanted for my son's Christmas (do not tell him): a postwar "
            "Lionel 736 Berkshire or a 681 turbine in good running "
            "condition. Cosmetics secondary -- it will be run hard by a "
            "seven-year-old under supervision -- but it must run "
            "reliably and the whistle tender would be a huge bonus. I "
            "know what these go for at shows, so no dreamers please, but "
            "I will pay a fair price for an honest runner. Have for "
            "trade: several postwar freight cars and a 1033 transformer "
            "in good shape. Can arrange pickup within driving distance "
            "of Chicago or pay insured postage. Help me make a kid's "
            "Christmas."
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-013",
        "section": "trains_layout",
        "date": "12/20/88",
        "author": "GRADECHASER",
        "subject": "Helix design -- how steep is too steep?",
        "body": (
            "I need to get from staging under the layout up to the main "
            "deck -- about 18 inches of rise -- and the only way is a "
            "helix in the corner. The conventional wisdom I keep hearing: "
            "keep grades under 2 percent, which at 18 inches of rise "
            "means a LOT of turns at any reasonable radius. My longest "
            "train is eight 40-foot cars plus a four-axle diesel. For "
            "those running helixes: what radius and grade did you build, "
            "and what will your locomotives actually pull up it? Did "
            "you double-track it, and do you regret it? I am trying to "
            "decide between a 24-inch radius at 2 percent and a 30-inch "
            "radius that eats the whole corner of the room."
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-014",
        "section": "trains_dcc",
        "date": "12/21/88",
        "author": "CHRISTMASLIST",
        "subject": "Should command control be on my Christmas list? (opinion wanted)",
        "body": (
            "My family keeps asking what I want for Christmas and I keep "
            "staring at the command-control ads. Here is my dilemma, and "
            "I want opinions, not sales pitches: everything available "
            "right now -- CTC-16, Dynatrol, the rest -- is proprietary. "
            "My understanding is that the NMRA is talking about a common "
            "digital standard but has not published one as of late 1988, "
            "so a system I buy this Christmas could be the Betamax of "
            "model railroading by 1990. That is my read; tell me if I "
            "have it wrong. The alternative is asking for $300 worth of "
            "turnout motors, wire, and toggles and wiring proper blocks. "
            "Less exciting under the tree, more useful for the next "
            "decade. What would you put on the list?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-015",
        "section": "trains_locos",
        "date": "12/22/88",
        "author": "DETAILNUT",
        "subject": "Detailing plastic diesels -- sunshades, grabs, and MU hoses",
        "body": (
            "The new plastic diesels run beautifully but they still look "
            "a little naked next to brass, so I have been on a detailing "
            "kick. This month's victim: an Athearn GP38-2. Added so far: "
            "wire grab irons (the molded ones got shaved off), sunshades "
            "over the cab windows, MU hoses and coupler cut bars on the "
            "pilots, a winterization hatch on the roof, and a proper "
            "horn. Next: windshield wipers and a beacon. Total parts "
            "cost about $12 and four evenings, and it looks like a "
            "different locomotive. The trick I learned: paint the "
            "detail parts BEFORE installing them, and use a pin vise, "
            "not a motor tool, for the grab-iron holes. What is your "
            "go-to detailing upgrade -- the one part that makes the "
            "biggest visual difference for the money?"
        ),
        "parent": None,
    },
    {
        "content_id": "trains-1988-016",
        "section": "trains_prototype",
        "date": "12/23/88",
        "author": "WEATHEREDBOXCAR",
        "subject": "Weathering freight cars -- what the prototype photos taught me",
        "body": (
            "Spent last weekend with a stack of prototype photos and my "
            "airbrush, and the photos humbled me. Real boxcars are not "
            "'boxcar red' -- they are ten different faded reds, with "
            "rust streaking down from every latch and ladder, dust "
            "caked on the lower panels, and roofwalks silvered by the "
            "sun. My old weathering was just a dusting of grimy black "
            "over everything, which made every car look like it had "
            "been in the same fire. New approach: fade the base color "
            "first with a thin overspray of the body color lightened "
            "with gray, then rust streaks with thinned burnt umber "
            "drawn downward, then chalk dust on the underframe. The "
            "prototype photo is the boss -- I keep one taped to the "
            "spray booth. What is your weathering sequence, and what "
            "mistake do you see beginners make most?"
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
