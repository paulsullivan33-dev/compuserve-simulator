"""Guitar & Music Forum content module.

Section spec and December 1988 seed posts for the ``guitar`` forum
("Guitar & Music Forum"): electrics, acoustics, amps & effects,
tablature exchange, MIDI & home recording, and what's spinning.

Period rules enforced by this module:
* Gear is 1988-era only: Fender American Standard Stratocaster (1987+),
  Gibson Les Paul Standard, Marshall JCM800, Roland JC-120, Fender Twin
  Reverb, Boss DS-1/CE-2/DD-3, Ibanez Tube Screamer TS-9, ProCo RAT,
  Dunlop Cry Baby, Yamaha DX7, Roland D-50, TASCAM Portastudio 4-track
  cassette, Alesis HR-16, Shure SM57/58. No post-1988 gear is ever
  mentioned (no Line 6, no PRS Silver Sky, no Kemper, no Axe-Fx/Fractal,
  no Neural DSP, no YouTube, no internet).
* Music discussion is December 1988: Appetite for Destruction's long
  chart run, ...And Justice for All (Aug 1988), Rattle and Hum
  (Oct 1988), Tracy Chapman (1988), Green (Nov 1988), OU812 (May 1988).
  Nothing references anything after December 1988.
"""

FORUM_ID = "guitar"
FORUM_TITLE = "Guitar & Music Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("guitar_electric", "Electric Guitars"), ...}
# The coordinator wires this into FORUM_CATALOG["guitar"]["sections"].
SECTIONS = {
    "1": ("guitar_electric", "Electric Guitars"),
    "2": ("guitar_acoustic", "Acoustic Guitars"),
    "3": ("guitar_amps", "Amps & Effects"),
    "4": ("guitar_tabs", "Tablature Exchange"),
    "5": ("guitar_midi", "MIDI & Home Recording"),
    "6": ("guitar_spinning", "What's Spinning"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "guitar-1988-001",
        "section": "guitar_electric",
        "date": "12/01/88",
        "author": "SixStringSysop",
        "subject": "Welcome to the Guitar & Music Forum",
        "body": (
            "Welcome, pickers and grinners. This is the place to talk "
            "guitars: electrics, acoustics, amps, pedals, and everything "
            "with strings. We have sections for gear talk, a tablature "
            "exchange (post your own transcriptions, note the tuning), a "
            "MIDI and home-recording corner for the Portastudio crowd, and "
            "a What's Spinning section for whatever is on your turntable "
            "this month. Introduce yourself, list your rig, and mind the "
            "house rule: no flame wars about tonewood. Play nice."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-002",
        "section": "guitar_electric",
        "date": "12/03/88",
        "author": "STRATCAT",
        "subject": "American Standard Strat vs. '62 reissue?",
        "body": (
            "I am finally buying a real Strat and I am torn between the new "
            "American Standard and a '62 vintage reissue. The American "
            "Standard has the 2-point trem and the hotter bridge pickup, "
            "and the necks feel great, but there is something about the "
            "reissue's 7.25-inch radius and vintage frets. I play mostly "
            "blues-rock and some clean funk. Anyone A/B'd them? Is the "
            "reissue worth the extra money, or is that paying for the "
            "headstock decal?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-003",
        "section": "guitar_electric",
        "date": "12/05/88",
        "author": "BURSTBELIEVER",
        "subject": "Les Paul Standard -- how heavy is too heavy?",
        "body": (
            "Tried three Les Paul Standards at the shop yesterday. The "
            "honeyburst weighed a ton but sustained for days; the lighter "
            "one felt better on the shoulder but sounded thinner. All had "
            "the Tim Shaw-era pickups. For those gigging a Paul: what is "
            "your weight limit, and does a wide strap really save your "
            "back on a four-set night? Also, anyone compared the '57 "
            "Goldtop reissue to the Standard? That P-90 growl is calling "
            "my name."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-004",
        "section": "guitar_acoustic",
        "date": "12/04/88",
        "author": "FLATPICKER",
        "subject": "D-28 vs. J-45 for bluegrass flatpicking",
        "body": (
            "Saving up for a lifetime dreadnought and I have it narrowed "
            "to a Martin D-28 and a Gibson J-45. I play mostly bluegrass "
            "rhythm and some flatpicked leads. The D-28 has that piano-like "
            "bass and cuts through a jam; the J-45 is warmer and records "
            "beautifully but can get lost next to a banjo. For those who "
            "own one or the other: which did you choose and why? And what "
            "strings are you running -- phosphor bronze lights, or do you "
            "go medium for the volume?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-005",
        "section": "guitar_acoustic",
        "date": "12/08/88",
        "author": "CHURCHGIG",
        "subject": "Takamine with the built-in pickup -- gig-worthy?",
        "body": (
            "I play acoustic at church and small coffeehouses and I am "
            "tired of fighting feedback with a soundhole pickup. The "
            "Takamine EF series with the built-in palathetic pickup keeps "
            "coming up -- under-saddle, preamp in the side, feedback-"
            "resistant. Anyone gigging one? How does it sound through a "
            "PA versus miked with an SM57? I do not want that quacky "
            "piezo tone if I can avoid it."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-006",
        "section": "guitar_amps",
        "date": "12/06/88",
        "author": "STACKATTACK",
        "subject": "JCM800 2204 vs. 2203 -- 50W or 100W?",
        "body": (
            "Looking at a used Marshall JCM800 and I cannot decide between "
            "the 50-watt 2204 and the 100-watt 2203. I play clubs, not "
            "arenas, and I want power-tube grind without killing the front "
            "row. The 50-watter breaks up earlier and weighs less, but "
            "everybody says the 100-watt has bigger iron and tighter bass. "
            "For those running a 2204: do you miss the headroom? And where "
            "do you set the preamp vs. master for classic rock crunch?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-007",
        "section": "guitar_amps",
        "date": "12/09/88",
        "author": "CLEANMACHINE",
        "subject": "JC-120 as a pedal platform",
        "body": (
            "Considering a Roland JC-120 Jazz Chorus as the foundation for "
            "a pedalboard rig. The clean headroom is legendary and the "
            "stereo chorus is gorgeous, but it is solid-state -- will my "
            "Tube Screamer and RAT still feel right through it? I play in "
            "a Top 40 band and need pristine cleans plus convincing dirt "
            "at moderate volume. Anyone running dirt pedals into a JC-120 "
            "nightly? How does it take a DS-1?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-008",
        "section": "guitar_amps",
        "date": "12/11/88",
        "author": "TEXASBLUES",
        "subject": "Tube Screamer into a Twin Reverb -- settings?",
        "body": (
            "Got an Ibanez TS-9 Tube Screamer to push my Twin Reverb into "
            "blues territory. The Twin stays clean forever, which is the "
            "point, but I am still dialing in the Screamer: drive at 9 "
            "o'clock, tone at noon, level maxed seems to be the classic "
            "recipe. What are your TS-9 settings? And for SRV-style bite, "
            "do you stack a second boost or just dig in harder? Using a "
            "Strat with stock single coils, by the way."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-009",
        "section": "guitar_tabs",
        "date": "12/07/88",
        "author": "TABTRADER",
        "subject": "TAB: Sultans of Swing -- intro (standard tuning)",
        "body": (
            "By request, here is my transcription of the Sultans of Swing "
            "intro. Standard tuning, clean Strat on the neck+middle "
            "pickup, fingerpicked.\n\n"
            "E||-------------------------|---------------------------|\n"
            "B||-------------------------|---------------------------|\n"
            "G||--------7-----7-----7----|--------7-----7-----7--------|\n"
            "D||-----7-----7-----7-----7-|-----7-----7-----7-----7-----|\n"
            "A||--5---------------------|--5--------------------------|\n"
            "E||-------------------------|---------------------------|\n\n"
            "That is the skeleton -- Knopfler's fills dance around the D "
            "major shape. Corrections welcome; I worked this out by ear "
            "off the vinyl. Next up if there is interest: the Money for "
            "Nothing riff."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-010",
        "section": "guitar_tabs",
        "date": "12/12/88",
        "author": "JUNGLEJIM",
        "subject": "Request: Sweet Child O' Mine intro tab",
        "body": (
            "Can anyone post a tab for the Sweet Child O' Mine intro? I "
            "have the D-C-G-D shape down but Slash's embellishments are "
            "faster than my ear. Standard tuning, and I know he plays it "
            "on the neck pickup of a Les Paul. Even a rough sketch of the "
            "first four bars would help. Happy to trade -- I have clean "
            "tabs for the Hotel California solo and the Stairway intro "
            "if anyone needs them."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-011",
        "section": "guitar_midi",
        "date": "12/10/88",
        "author": "MIDIMAN",
        "subject": "Layering DX7 and D-50 -- MIDI channel setup",
        "body": (
            "Finally have both a Yamaha DX7 and a Roland D-50 in the home "
            "studio and I want to layer them from one keyboard. The plan: "
            "DX7 as master on channel 1, D-50 receiving on channel 1 with "
            "local off, then split the D-50's upper/lower across two "
            "channels for sequencer overdubs. For those running a two-"
            "keyboard MIDI rig: any gotchas with the D-50's patch changes "
            "eating the DX7's program changes? And is anyone using a "
            "dedicated MIDI patchbay, or just daisy-chaining thru ports?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-012",
        "section": "guitar_midi",
        "date": "12/14/88",
        "author": "FOURTRACK",
        "subject": "Syncing HR-16 drum machine to Portastudio 244",
        "body": (
            "Home recording question: I am tracking on a TASCAM Portastudio "
            "244 (4-track cassette) and I want my Alesis HR-16 drum machine "
            "to stay in sync across takes. I know the 244 has no MIDI sync, "
            "so I am striping SMPTE-ish sync tone from a JL Cooper box to "
            "track 4 and slaving the HR-16 to it. It works, but I lose a "
            "track. Is there a better way short of buying a bigger machine? "
            "How are the rest of you syncing drums to cassette 4-tracks?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-013",
        "section": "guitar_midi",
        "date": "12/16/88",
        "author": "SYNTHAXE",
        "subject": "Guitar synth live -- Casio PG-380 impressions?",
        "body": (
            "Anyone gigging a guitar synth? I tried the Casio PG-380 "
            "(Strat-style with the built-in synth module) at the shop and "
            "the tracking was better than I expected -- the brass and "
            "string patches actually followed my playing. My worry is "
            "live reliability and whether the synth sounds sit in a band "
            "mix or just sound like a novelty. For studio layering it seems "
            "like a no-brainer at the price. Talk me into it or out of it."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-014",
        "section": "guitar_spinning",
        "date": "12/13/88",
        "author": "THRASHFAN",
        "subject": "...And Justice for All -- where is the bass?",
        "body": (
            "Been living with the new Metallica record for three months "
            "now and I have to ask: where is the bass guitar? You can hear "
            "Newsted on exactly none of it -- the whole album is guitars, "
            "drums, and Hetfield's voice fighting for the same midrange. "
            "One is a masterpiece of arrangement, but the mix is so dry it "
            "hurts. Am I crazy, or did they bury the new guy on purpose? "
            "Still, that title track's middle section is the heaviest thing "
            "I have heard all year."
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-015",
        "section": "guitar_spinning",
        "date": "12/15/88",
        "author": "DESERTROCK",
        "subject": "Rattle and Hum -- film and album",
        "body": (
            "Caught Rattle and Hum last weekend and picked up the double "
            "album after. The Sun Studios sessions are the highlight for "
            "me -- the band sounds loose and alive in a way the Joshua "
            "Tree tour sometimes was not. The BB King collaboration on "
            "When Love Comes to Town gave me chills. Is it self-indulgent? "
            "Sure, a little. But as a document of a band at the absolute "
            "peak of its powers, I am glad it exists. What is everyone "
            "else spinning this month?"
        ),
        "parent": None,
    },
    {
        "content_id": "guitar-1988-016",
        "section": "guitar_spinning",
        "date": "12/18/88",
        "author": "FINGERSTYLE",
        "subject": "Tracy Chapman -- Fast Car fingerpicking",
        "body": (
            "The Tracy Chapman debut has been on my turntable all month, "
            "and Fast Car is a masterclass in less-is-more guitar: that "
            "rolling Travis-picked pattern under the whole song, capo up, "
            "never a wasted note. For the fingerstyle players here: are "
            "you playing it with thumbpick and fingers, or bare thumb? I "
            "am getting the pattern clean at tempo but the bass notes keep "
            "overpowering the melody. Also, Talkin' 'bout a Revolution uses "
            "the same vocabulary -- great study piece for beginners."
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
