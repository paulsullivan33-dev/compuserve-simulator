"""Photography Forum content module.

Section spec and December 1988 seed posts for the ``photo`` forum
("Photography Forum"): General (the section key ``photography_general``
predates this module and is preserved for wiring compatibility),
Cameras & Lenses, Darkroom, Composition & Technique, and Film &
Processing.

Period rules enforced by this module:
* Camera talk is 1988-plausible: the Nikon F4 was announced September 8,
  1988 (the first professional Nikon with a practical autofocus
  system), so members can be talking about seeing one at Photokina in
  October 1988 or waiting for stock. The Canon EOS 650 (first EOS
  body, EF mount, introduced March 2, 1987) and EOS 620 are current
  models; the FD-to-EF mount break is still fresh debate material.
  Minolta Maxxum 7000, Pentax and Olympus SLRs, and compact zoom
  point-and-shoots (Canon Sure Shot, Olympus Infinity, Pentax Zoom
  70) are all current. No post-1988 bodies (no EOS-1, no Nikon F5,
  no autofocus flagships announced in 1989 or later).
* Film talk is 1988-plausible: Kodak Gold (launched 1986) versus
  Fuji color negative films, Tri-X pushed in D-76 or HC-110, Kodachrome
  and Ektachrome slides. Disc film (introduced 1982) is in visible
  decline -- post authors treat this as observation and opinion, not
  a cited market fact. 110 cartridges and 126 are still around but
  fading from the serious conversation.
* Darkroom talk: enlargers (Beseler, Omega), D-76 vs. HC-110 vs.
  Rodinal, fiber vs. RC paper, safelights, ventilation gripes.
* Composition: the rule of thirds, leading lines, shooting Christmas
  lights on a tripod with slow film -- nothing requiring a camera or
  technique that postdates December 1988.
* Nothing references the internet, websites, blogs, email, digital
  cameras, scanners-as-consumer-gear, Photoshop (the pre-1.0 1988
  prototype was not a consumer product), or anything else after
  December 1988. Sources are camera magazines (Popular Photography,
  Modern Photography, Shutterbug), camera-store counters, and club
  meetings.
"""

from pathlib import Path

# Repo root, derived so paths are never hardcoded.
REPO_ROOT = Path(__file__).resolve().parent

FORUM_ID = "photo"
FORUM_TITLE = "Photography Forum"

# Section spec, mirroring the FORUM_CATALOG shape. The "1" key
# ("photography_general", "General") matches the pre-existing inline
# entry in compuserve.py and must not change.
SECTIONS = {
    "1": ("photography_general", "General"),
    "2": ("photo_cameras", "Cameras & Lenses"),
    "3": ("photo_darkroom", "Darkroom"),
    "4": ("photo_composition", "Composition & Technique"),
    "5": ("photo_film", "Film & Processing"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "photo-1988-001",
        "section": "photography_general",
        "date": "12/01/88",
        "author": "SysopShutter",
        "subject": "Welcome to the Photography Forum",
        "body": (
            "Say cheese -- the Photography Forum is open. General is for "
            "introductions, club news, and anything that does not fit "
            "elsewhere; Cameras & Lenses covers bodies, glass, and the "
            "autofocus wars; Darkroom is for enlargers, chemistry, and "
            "printing talk; Composition & Technique is about making "
            "better pictures with whatever you own; and Film & Processing "
            "covers emulsions, labs, and the eternal Kodak-versus-Fuji "
            "argument. Introduce yourself: what are you shooting, and "
            "what is on your film shelf right now?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-002",
        "section": "photo_cameras",
        "date": "12/03/88",
        "author": "NIKONNUT",
        "subject": "The Nikon F4 -- has anyone actually HELD one yet?",
        "body": (
            "Nikon made it official back in September -- the F4 is real, "
            "the first pro Nikon with a real autofocus system, built-in "
            "motor drive, and a shutter that goes to 1/8000. The magazines "
            "have been drooling since Photokina in October. My dealer "
            "says his first bodies arrive after the holidays and the "
            "waiting list is already a page long. So who here has actually "
            "put hands on one at a show or a demo day? Is the autofocus "
            "actually usable for sports, or is it the usual first-"
            "generation promise? And at roughly twice what I paid for my "
            "F3, is anyone trading up on day one? I am trying to talk "
            "myself out of it."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-003",
        "section": "photo_cameras",
        "date": "12/05/88",
        "author": "FDFOREVER",
        "subject": "Canon abandoned us -- the FD mount betrayal, 18 months on",
        "body": (
            "It has been a year and a half since Canon dropped the EOS 650 "
            "with that all-electronic EF mount, and I am still bitter. "
            "Twenty years of FD lenses -- a 50mm f/1.4, an 85mm f/1.8, a "
            "35-105 zoom -- and none of them mount on the new bodies "
            "without losing everything that made them good. Canon says the "
            "fully electronic mount was the only way to get serious "
            "autofocus, and the EOS 650's focus speed is, I admit, scary "
            "fast. But Nikon kept the F mount and added autofocus around "
            "it. Minolta started clean too, but at least they had no "
            "legacy to betray. FD shooters: are you buying adapters and "
            "staying manual, jumping to EOS, or switching brands out of "
            "spite? I need a plan before my T90 dies."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-004",
        "section": "photo_darkroom",
        "date": "12/08/88",
        "author": "DARKROOMDAN",
        "subject": "Building my first darkroom -- enlarger advice needed",
        "body": (
            "After two years of paying the lab $8 a roll for processing "
            "plus prints, I am converting the spare bathroom into a "
            "darkroom. I shoot 35mm black and white, mostly Tri-X. The "
            "classifieds have a Beseler 23C and an Omega B600, both with "
            "50mm lenses, both around $150. Which one would you take? "
            "The Beseler is built like a tank but huge; the Omega is "
            "lighter and I have heard the alignment holds well. Also: "
            "safelight (OC amber, right?), trays, tongs, a timer, and "
            "what chemistry to start with -- D-76 for film, Dektol for "
            "paper, and fixer? Anything I am forgetting that will send me "
            "back to the camera store on day one?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-005",
        "section": "photo_cameras",
        "date": "12/07/88",
        "author": "PROGRAMSHOOTER",
        "subject": "Program mode is not cheating -- a defense",
        "body": (
            "I am tired of the sneering at the camera club whenever "
            "someone admits to shooting in program mode. My Maxxum 7000 "
            "has a computer in it that meters six ways and picks a "
            "shutter-aperture combination faster and more accurately than "
            "I ever could with a handheld meter and a prayer. I shoot "
            "aperture priority when depth of field matters and shutter "
            "priority for the kids' soccer, but for grab shots at a party, "
            "program mode with a bounce flash gets the picture -- and the "
            "picture is the point. The old guard with their match-needle "
            "Canons can keep their purity; I will keep my keepers. "
            "Program shooters, stand up and be counted."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-006",
        "section": "photo_film",
        "date": "12/14/88",
        "author": "GRAINWATCHER",
        "subject": "Kodak Gold vs. Fuji -- the great color negative debate",
        "body": (
            "It is time we settled this like adults, with test rolls. "
            "Kodak Gold 100 and 200 have been my standard since they came "
            "out a couple of years ago -- warm skin tones, forgiving "
            "latitude, and every drugstore on earth stocks it. But my "
            "brother-in-law shot Fuji on our vacation and his greens and "
            "blues practically glow; my Gold shots of the same lake look "
            "muddy by comparison. The Fuji camp says finer grain and "
            "punchier color; the Kodak camp says natural skin tones and "
            "better pushability. So: for family snapshots and travel, "
            "which are you loading, and why? Bonus question: does anyone "
            "still shoot Kodacolor VR, or has Gold fully replaced it in "
            "your bag?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-007",
        "section": "photo_film",
        "date": "12/16/88",
        "author": "DISCDATADUMP",
        "subject": "Is disc film finally dead? (my opinion: yes)",
        "body": (
            "Opinion time, so take this as one photographer's read of the "
            "shelves, not a market report: disc film looks finished to "
            "me. The camera counter at my drugstore, which had a whole "
            "endcap of disc cameras in 1984, is down to one dusty model "
            "and a peg of film. The negatives are tiny, the grain is the "
            "size of golf balls, and every 35mm compact with a decent "
            "lens embarrasses it. I know disc was supposed to be the "
            "foolproof future -- drop in the disc, no threading -- but "
            "the pictures were never good enough to justify it. Anyone "
            "still shooting disc in December 1988? Defend it if you can. "
            "And 110 users: is your format next, or does the pocket "
            "camera keep it alive?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-008",
        "section": "photo_darkroom",
        "date": "12/10/88",
        "author": "PRINTMAKER",
        "subject": "D-76 vs. HC-110 vs. Rodinal -- pick your developer",
        "body": (
            "Every darkroom thread eventually comes down to chemistry, so "
            "let us have the developer debate properly. D-76 (or ID-11, "
            "same thing in a different bag) is the old reliable: full "
            "film speed, fine grain, every book ever written assumes you "
            "are using it. HC-110 is the syrup in the little bottle that "
            "lasts forever -- convenient, sharp, great for Tri-X pushed "
            "to 800 in dilution B. Rodinal is the cult choice: ancient "
            "formula, razor-sharp grain with slow films like Pan F, and "
            "a bottle that outlives its owner. I have been a D-76 man for "
            "a decade but the Rodinal whispers are getting to me. What is "
            "in your graduate right now, and what film-developer pairing "
            "would you defend to the death?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-009",
        "section": "photo_composition",
        "date": "12/11/88",
        "author": "THIRDSRULE",
        "subject": "Beyond the rule of thirds -- what actually improved your photos?",
        "body": (
            "We all learned the rule of thirds in week one: put the "
            "horizon on a third, put the subject off-center, done. But "
            "what composition idea actually changed your photography "
            "after the basics? For me it was learning to get closer -- "
            "filling the frame instead of photographing my family as "
            "tiny figures in a landscape -- and learning that the "
            "background ruins more pictures than bad exposure does. Now "
            "I check the edges of the viewfinder before I check the "
            "meter. What was your breakthrough? Leading lines, framing "
            "with doorways, shooting at dawn instead of noon? The "
            "beginners among us (welcome!) want the stuff the books "
            "bury on page 90."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-010",
        "section": "photo_composition",
        "date": "12/13/88",
        "author": "TRIPODTESS",
        "subject": "Shooting the Christmas lights -- my annual ritual and recipe",
        "body": (
            "Every December I do the same thing and every December it "
            "works, so here is my Christmas-lights recipe for anyone "
            "trying it this week. Tripod -- non-negotiable. Slow film: "
            "Kodachrome 64 for the saturated reds and greens, or "
            "Ektachrome 100 if you want a little more speed. Shoot at "
            "dusk, not full dark, so the houses have some shape instead "
            "of floating in black. Expose for the lights and let the "
            "shadows go; bracket a stop each way because meters lie about "
            "Christmas. Cable release or self-timer to avoid shake. And "
            "turn off your flash -- it will kill the glow and light up "
            "nothing but the bushes. Post your results when the slides "
            "come back; I want to see how the new Fuji slide films handle "
            "the reds."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-011",
        "section": "photo_film",
        "date": "12/17/88",
        "author": "PUSHERMAN",
        "subject": "Pushing Tri-X to 1600 -- grain you can hang wallpaper with",
        "body": (
            "Shot my daughter's school play last night on Tri-X rated at "
            "1600 and developed in HC-110 dilution B, and you know what? "
            "The grain is enormous and I love it. There is something "
            "honest about a frame that looks like it was carved out of "
            "sand -- you can feel the darkness in the picture. The "
            "drama teacher wants an 8x10 for the lobby and I am slightly "
            "terrified, but the contact sheet has real energy. For the "
            "pushers here: what is your ceiling? 800? 1600? 3200 and "
            "pray? And which developer keeps the shadows from going "
            "completely empty at those speeds? My rule so far: expose "
            "for the shadows, develop for the highlights, and accept "
            "the grain as the price of admission."
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-012",
        "section": "photo_cameras",
        "date": "12/19/88",
        "author": "POCKETCAM",
        "subject": "Compact zoom point-and-shoots -- has the SLR had its day?",
        "body": (
            "Heresy alert: I am starting to think the compact zoom "
            "point-and-shoot is the real camera of 1988 and my SLR is "
            "becoming a shelf queen. My Pentax Zoom 70 goes from 35 to "
            "70mm, focuses itself, exposes itself, winds and rewinds "
            "itself, and fits in a coat pocket. The Canon Sure Shots and "
            "the Olympus Infinity zooms are the same story -- real "
            "lenses, real automation, no camera bag. Yes, the SLR still "
            "wins for fast action and real wide angles, and the little "
            "zoom lenses are slow. But for travel, parties, and everyday "
            "life, the compact goes along and the SLR stays home. Who "
            "else has quietly switched? SLR loyalists: what keeps you "
            "carrying the weight?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-013",
        "section": "photo_darkroom",
        "date": "12/20/88",
        "author": "FIBERFAN",
        "subject": "Fiber paper vs. RC -- is the extra work worth it?",
        "body": (
            "I have been printing on RC (resin-coated) paper for two "
            "years: wash for four minutes, squeegee, done. Now the "
            "camera club's exhibition chairman tells me fiber-based paper "
            "is the only 'serious' paper and my RC prints look 'commercial'. "
            "So I tried a box of fiber: an hour of washing, curling like "
            "a potato chip, and a flattening press I do not own. BUT -- "
            "and it is a big but -- the blacks are deeper and the print "
            "has a weight and presence the RC never had. My opinion: RC "
            "for proofing and everyday prints, fiber for the ones that "
            "matter. Fiber printers: what is your washing and drying "
            "routine, and how do you keep the curl under control without "
            "a dry-mount press?"
        ),
        "parent": None,
    },
    {
        "content_id": "photo-1988-014",
        "section": "photo_cameras",
        "date": "12/22/88",
        "author": "USEDFINDER",
        "subject": "Used camera bargains -- what the autofocus boom did to prices",
        "body": (
            "Silver lining of the autofocus mania: the used counter is "
            "full of beautiful manual-focus bodies that everyone is "
            "dumping. I saw a Canon A-1 with a 50mm f/1.4 for $175, a "
            "Nikon FM2 body for $200, and a Minolta X-700 kit for $150 -- "
            "all in clean condition, all being traded in toward EOS and "
            "Maxxum bodies. The dealers are practically begging people "
            "to take the manual stuff. My take: if you know how to focus "
            "and meter, this is the golden age of used bargains. What "
            "have you found on the used shelf lately? And what is the "
            "one manual-focus body you would grab before the prices "
            "figure out they are not obsolete?"
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
