"""Health & Fitness Forum content module.

Section spec and December 1988 seed posts for the ``fitness`` forum
("Health & Fitness Forum"): aerobics, running, weight training,
nutrition, sports medicine/injuries, and mind & body.

Period rules enforced by this module:
* Exercise culture is 1988-plausible: Jane Fonda workout tapes
  (the 1982 original, the 1985 New Workout, the 1987 Low Impact tape),
  Kathy Smith videos, Richard Simmons' "Sweatin' to the Oldies"
  (1988), Jazzercise classes, leg warmers and leotards, Reebok
  Freestyle high-tops for aerobics. No post-1988 videos, gadgets,
  or crazes (no step-aerobics boom, no ThighMaster, no Tae Bo).
* Strength training debates are Nautilus machines (Arthur Jones)
  versus barbells and dumbbells; home equipment is Soloflex,
  NordicTrack ski machines, Schwinn Air-Dyne bikes. No post-1988
  equipment is ever mentioned.
* Running shoes are 1988-plausible: Nike Air Pegasus and Air Max
  (1987), New Balance 990, Asics Tiger with Gel cushioning, Etonic,
  LA Gear. The Seoul Olympics (September-October 1988) may be
  referenced as recent history.
* Nutrition is 1988-plausible: the oat bran craze ("The 8-Week
  Cholesterol Cure"), low-fat everything, NutraSweet, Pritikin,
  Jane Brody columns, GNC and Weider supplements (protein powder,
  desiccated liver tablets, brewer's yeast). No post-1988 diet
  fads or products.
* Nothing references the internet, websites, blogs, email, heart-
  rate monitors with downloads, fitness apps, or anything else
  after December 1988. Advice comes from magazines (Shape, Men's
  Health is 1986 so it qualifies, Runner's World, Muscle & Fitness),
  books, YMCA classes, and gym buddies.
"""

FORUM_ID = "fitness"
FORUM_TITLE = "Health & Fitness Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("fitness_aerobics", "Aerobics"), ...}
# The coordinator wires this into FORUM_CATALOG["fitness"]["sections"].
SECTIONS = {
    "1": ("fitness_aerobics", "Aerobics"),
    "2": ("fitness_running", "Running"),
    "3": ("fitness_weights", "Weight Training"),
    "4": ("fitness_nutrition", "Nutrition"),
    "5": ("fitness_injuries", "Sports Medicine/Injuries"),
    "6": ("fitness_mindbody", "Mind & Body"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "fitness-1988-001",
        "section": "fitness_aerobics",
        "date": "12/01/88",
        "author": "SysopFit",
        "subject": "Welcome to the Health & Fitness Forum",
        "body": (
            "Lace up your high-tops and pull on the leg warmers -- this "
            "is the place to talk fitness, 1988 style. We have six "
            "sections: Aerobics (videos, classes, and choreography "
            "debates), Running (shoes, training, and race reports), "
            "Weight Training (Nautilus versus free weights -- be civil), "
            "Nutrition (oat bran believers welcome), Sports "
            "Medicine/Injuries (we are not doctors, but we have all iced "
            "something), and Mind & Body (yoga, stretching, and stress). "
            "New Year's resolutions are four weeks away, so there is no "
            "better time to start. Tell us what you are training for."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-002",
        "section": "fitness_aerobics",
        "date": "12/02/88",
        "author": "FONDAFAN88",
        "subject": "Jane Fonda vs. Kathy Smith -- which workout tape wins?",
        "body": (
            "My VCR is getting a workout and so am I, but I need a ruling. "
            "Jane Fonda's original Workout tape has the leg lifts that "
            "nearly killed me in 1983, the New Workout from a couple years "
            "back is tougher on the arms, and the Low Impact tape is "
            "kinder to my knees. Meanwhile my neighbor swears by Kathy "
            "Smith's Winning Workout and says Fonda is old news. For "
            "those doing both: which tape actually gets your heart rate up "
            "without wrecking your joints? And does anyone else do these "
            "in Reebok Freestyles, or am I the only one whose high-tops "
            "squeak on the living room carpet?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-003",
        "section": "fitness_running",
        "date": "12/04/88",
        "author": "MILEMAN",
        "subject": "1988 running shoes -- Nike, New Balance, or Asics Tiger?",
        "body": (
            "My old pair has 600 miles on it and my knees are filing a "
            "complaint, so it is shoe-shopping time. The running store "
            "pushed the Nike Air Pegasus on me -- that visible air pocket "
            "looks like the future -- but the New Balance 990 fits my "
            "wide foot like it was built for it, and the Asics Tiger "
            "with the Gel cushioning felt like running on marshmallows. "
            "After watching the Seoul Olympic marathon this fall I am "
            "inspired enough to actually train through winter. What are "
            "you racing in, and how many miles do you retire a pair at? "
            "My wallet hopes the answer is not the most expensive one."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-004",
        "section": "fitness_weights",
        "date": "12/05/88",
        "author": "NAUTILUSNED",
        "subject": "Nautilus machines vs. free weights -- settle it",
        "body": (
            "Every gym I have joined since 1979 has this argument, so "
            "let's have it out properly. The Nautilus camp says Arthur "
            "Jones got it right: the cam gives you full-range resistance, "
            "it is safer than a barbell with no spotter, and you can blast "
            "through a circuit in 30 minutes. The iron camp says machines "
            "do the stabilizing for you, nothing builds real strength "
            "like a barbell squat, and Nautilus is for people afraid of "
            "chalk. I train at a Gold's-style iron gym but my office "
            "building just put in a Nautilus room. For a 40-year-old who "
            "wants to be strong without getting hurt: which side are you "
            "on, and why?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-005",
        "section": "fitness_nutrition",
        "date": "12/06/88",
        "author": "OATBRANBETTY",
        "subject": "The oat bran craze -- miracle or marketing?",
        "body": (
            "Is anyone else's grocery store sold out of oat bran? Ever "
            "since that cholesterol book made the talk-show rounds, my "
            "husband eats a bowl of the stuff every morning and lectures "
            "me about soluble fiber. I will grant that his last checkup "
            "numbers looked better, but I also notice the box costs three "
            "times what oatmeal costs and tastes like warm cardboard "
            "unless you bury it in brown sugar -- which rather defeats the "
            "purpose. Jane Brody wrote it up seriously, so there must be "
            "something to it. Who here has actually stuck with oat bran "
            "for months, and did your cholesterol budge? Recipes that make "
            "it edible are also welcome."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-006",
        "section": "fitness_injuries",
        "date": "12/08/88",
        "author": "SHINSPLINTSAM",
        "subject": "Shin splints are killing my New Year's 5K plan",
        "body": (
            "I am three weeks into training for a New Year's Day 5K and "
            "my shins feel like they are being hit with a hammer every "
            "time my foot lands. Classic beginner mistake, I know -- too "
            "much, too soon, on concrete, in old tennis shoes that were "
            "never running shoes to begin with. I have started icing "
            "after runs and doing toe raises against a wall, and I am "
            "shopping for real shoes this weekend (see the shoe thread). "
            "Question for the veterans: do I run through this or take a "
            "week off? And is there a stretch or drill that actually "
            "fixed it for you? I refuse to be beaten by my own shins."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-007",
        "section": "fitness_weights",
        "date": "12/09/88",
        "author": "HOMEGYMHANK",
        "subject": "Soloflex -- worth fourteen hundred dollars?",
        "body": (
            "Those Soloflex commercials are on every time I watch a ball "
            "game -- the rubber straps, the dramatic lighting, the promise "
            "of a full gym in the corner of the garage for around $1,400. "
            "My health club membership is $35 a month and the drive is 20 "
            "minutes each way, so the math almost works if the machine "
            "lasts. But can rubber straps really replace iron? Does the "
            "bench press attachment feel like a real press, or like doing "
            "push-ups against a giant rubber band? Anyone here actually "
            "own one? I need an honest review before Christmas -- my wife "
            "says it is either the Soloflex or a NordicTrack, and she "
            "gets the tie-breaking vote."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-008",
        "section": "fitness_aerobics",
        "date": "12/10/88",
        "author": "SWEATIN88",
        "subject": "Richard Simmons' 'Sweatin' to the Oldies' -- my verdict",
        "body": (
            "Confession: I bought 'Sweatin' to the Oldies' as a joke gift "
            "for my wife, and now we do it together three nights a week. "
            "Richard Simmons in those short-shorts, shouting encouragement "
            "while regular folks -- not models, regular folks -- dance to "
            "oldies from the 50s and 60s, is the most fun I have had "
            "exercising since Jazzercise came to our church basement in "
            "1984. It is lower impact than my wife's Fonda tapes, which "
            "my knees appreciate, and an hour flies by. Anyone else "
            "secretly -- or not so secretly -- a Simmons convert? Next "
            "I am eyeing that 'Buns of Steel' tape everyone at work is "
            "talking about, but one infomercial-grade obsession at a time."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-009",
        "section": "fitness_running",
        "date": "12/11/88",
        "author": "SEOULSPECTATOR",
        "subject": "After Seoul -- what the Olympic marathon taught this jogger",
        "body": (
            "Watching Bordin and Mota win the Olympic marathons in Seoul "
            "this fall did something to me. Here were runners who looked "
            "like they were out for a Sunday jog while running times I "
            "could not touch on a bicycle, and the announcers kept talking "
            "about patience -- even pacing, no heroics before mile 20. So "
            "I am stealing their strategy for my own humble winter base "
            "training: slow miles, lots of them, no racing my training "
            "partners. For the marathoners here: how many miles a week "
            "did you build to before your first 26.2, and what is the one "
            "piece of Seoul-inspired wisdom you would give a 10K runner "
            "moving up? Joan Benoit gutted out ninth in Seoul on guts "
            "alone -- if that is not motivation, nothing is."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-010",
        "section": "fitness_nutrition",
        "date": "12/12/88",
        "author": "COOKIETRAY",
        "subject": "Surviving December -- the office cookie tray defense plan",
        "body": (
            "It is December 12th and I have already eaten my weight in "
            "fudge. The break room has a permanent cookie tray, the "
            "neighbors keep bringing over tins, and my mother-in-law's "
            "rum balls are, scientifically speaking, irresistible. So "
            "here is my defense plan, offered for critique: eat a real "
            "lunch so I am not starving at 3 PM, allow myself two treats "
            "a day chosen deliberately (not grazed), keep the oat bran "
            "muffins coming for breakfast, and add a 20-minute walk at "
            "lunch to offset the damage. No crash diets until January -- "
            "that way lies madness and a binge on December 26th. What "
            "is your December survival strategy? Anyone doing the "
            "full-abstinence thing, and does it actually work?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-011",
        "section": "fitness_mindbody",
        "date": "12/13/88",
        "author": "DESKJOBDAN",
        "subject": "Yoga for a stiff desk jockey -- where does a beginner start?",
        "body": (
            "I am 45, I sit at a terminal all day, and I can barely touch "
            "my knees, let alone my toes. My doctor says my back would "
            "thank me for stretching, and the YMCA down the street has a "
            "Tuesday night yoga class that looks less intimidating than "
            "the aerobics studio full of 25-year-olds in leotards. But I "
            "have questions: do I need to be flexible to START yoga, or "
            "is that like saying you need to be clean to take a shower? "
            "Is the Richard Hittleman book from the library enough to "
            "learn the basics, or do I need a live teacher so I do not "
            "hurt myself? Fellow stiff beginners -- what worked for you?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-012",
        "section": "fitness_injuries",
        "date": "12/15/88",
        "author": "KNEESQUEAK",
        "subject": "Runner's knee -- RICE and patience, or see the sports doc?",
        "body": (
            "Three miles into my run yesterday, my left knee started "
            "aching right around the kneecap -- dull, then sharper on "
            "downhills and stairs. Dr. Sheehan's column in Runner's World "
            "says this sounds like runner's knee, and the prescription is "
            "the usual: rest, ice, compression, elevation, plus a couple "
            "of Advil and quad-strengthening exercises once the pain "
            "fades. I have done two days of RICE and it is better but not "
            "gone. For those who have been through this: how long did you "
            "rest before running again, and at what point did you give up "
            "and see a sports medicine doctor? I have a 10K in March and "
            "I am trying not to panic."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-013",
        "section": "fitness_weights",
        "date": "12/16/88",
        "author": "RESOLUTIONROB",
        "subject": "New Year's resolution -- first time touching a barbell at 38",
        "body": (
            "I am calling my shot early: on January 2nd I am joining the "
            "gym near my office and learning to lift. I am 38, I have "
            "never touched a barbell, and my current exercise program is "
            "carrying groceries. The plan, subject to your corrections: "
            "three full-body sessions a week, mostly machines at first "
            "while I learn form, then graduate to dumbbells and the "
            "barbell for squats, presses, and rows. Ask the gym for an "
            "orientation session. Do NOT try to max out in week one to "
            "impress anyone. Eat more protein, sleep more, be patient. "
            "Veterans: what do you wish someone had told you in your "
            "first month? And is three days a week enough to actually "
            "change anything?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-014",
        "section": "fitness_running",
        "date": "12/18/88",
        "author": "FROSTRUNNER",
        "subject": "Winter running -- layers, ice, and the 5 AM darkness",
        "body": (
            "It was 22 degrees this morning and I was out there anyway, "
            "so here is my winter running manifesto for the rest of you "
            "lunatics. Layers: polypro or wool against the skin (cotton "
            "kills -- it holds sweat and freezes), a windbreaker on top, "
            "and strip a layer after the first mile when you warm up. "
            "Head and hands lose the most heat -- wear the hat, wear the "
            "gloves. Reflective tape or a vest is non-negotiable in the "
            "dark; drivers cannot see a dark sweatsuit at 5 AM. Shorten "
            "your stride on ice, and if the sidewalks are a skating rink, "
            "take it to the indoor track or the treadmill with zero "
            "shame. Warm up inside before you go out. What is your "
            "coldest run this month, and what is your temperature cutoff?"
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-015",
        "section": "fitness_nutrition",
        "date": "12/19/88",
        "author": "SHAKERBOTTLE",
        "subject": "Protein powder, desiccated liver, brewer's yeast -- the supplement aisle",
        "body": (
            "Wandered into GNC yesterday and the supplement aisle has "
            "gotten out of hand. Weider protein powder in five flavors, "
            "desiccated liver tablets the size of aspirin, brewer's yeast "
            "flakes, amino acid capsules, and a dozen miracle pills with "
            "labels that promise everything short of flight. After the "
            "Seoul steroid scandal this fall, I read every label twice. "
            "My take: food first -- eggs, tuna, milk, peanut butter -- "
            "and the powder is just convenient food, not magic. The liver "
            "tablets taste like a barn and I am not convinced they do "
            "anything a steak does not do better. Who here actually uses "
            "supplements, and which ones survived your own skepticism? "
            "Bonus points if you admit to the ones that did nothing."
        ),
        "parent": None,
    },
    {
        "content_id": "fitness-1988-016",
        "section": "fitness_mindbody",
        "date": "12/22/88",
        "author": "NEWYEARNEWME",
        "subject": "1989 resolution thread -- post your fitness goals",
        "body": (
            "Nine days until 1989, so let us put it in writing where our "
            "forum friends can hold us to it. The rules: one primary goal, "
            "specific enough to measure, plus the habit that gets you "
            "there. Mine: run the Cherry Blossom 10-miler in April, which "
            "means 25 miles a week by February and no skipping the long "
            "run. Runner-up goals: finally learn to meditate without "
            "falling asleep (that Relaxation Response book has been on my "
            "nightstand since summer) and stretch for ten minutes every "
            "night while the news is on. Your turn -- post your 1989 "
            "fitness goal below, and we will check in on each other come "
            "spring. No judgment, just accountability."
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
