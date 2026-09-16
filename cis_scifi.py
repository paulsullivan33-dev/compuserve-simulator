"""Comics & Sci-Fi Forum content module.

Section spec and December 1988 seed posts for the ``scifi`` forum
("Comics & Sci-Fi Forum"): comic books, Star Trek, Doctor Who,
movies & TV, books, and conventions.

Period rules enforced by this module:
* Setting is December 1988. Star Trek: The Next Generation season 2
  is airing (fall 1988); discussion covers aired season 2 episodes
  ("Where Silence Has Lease", "Elementary, Dear Data", "The Outrageous
  Okona") plus season 2 changes (Guinan, Dr. Pulaski, Riker's beard).
  "The Measure of a Man" (Feb 1989) and season 3 are never mentioned.
* Comics discussion is 1988-current: Watchmen (1986-87, collected
  edition), Batman: The Killing Joke (1988), post-Crisis DC continuity.
  The 1989 Batman film is never referenced as released.
* Doctor Who season 25 (1988, Seventh Doctor and Ace) is airing;
  "Remembrance of the Daleks", "Silver Nemesis", and the currently
  airing "The Greatest Show in the Galaxy" (Dec 14-28, 1988).
* Films are 1988 releases: They Live, Alien Nation. Books are
  1987-88: Asimov's Prelude to Foundation (1988), Heinlein's To Sail
  Beyond the Sunset (1987), Gibson's Mona Lisa Overdrive (Oct 1988).
  1989 conventions are discussed only as upcoming plans.
* Nothing references anything after December 1988: no internet, no
  DVDs, no streaming, no post-1988 films, shows, comics, or games.
"""

FORUM_ID = "scifi"
FORUM_TITLE = "Comics & Sci-Fi Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("scifi_comics", "Comic Books"), ...}
# The coordinator wires this into FORUM_CATALOG["scifi"]["sections"].
SECTIONS = {
    "1": ("scifi_comics", "Comic Books"),
    "2": ("scifi_trek", "Star Trek"),
    "3": ("scifi_who", "Doctor Who"),
    "4": ("scifi_movies", "Movies & TV"),
    "5": ("scifi_books", "Books"),
    "6": ("scifi_cons", "Conventions"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "scifi-1988-001",
        "section": "scifi_comics",
        "date": "12/01/88",
        "author": "STARBEACON",
        "subject": "Welcome to the Comics & Sci-Fi Forum",
        "body": (
            "Welcome, true believers and starfarers. This is the place for "
            "four-color talk and speculative fiction of every stripe. Six "
            "sections: Comic Books for capes-and-tights debate, Star Trek "
            "for all things Federation (TNG season 2 is on now), Doctor "
            "Who for the Seventh Doctor's latest, Movies & TV for what is "
            "playing and airing, Books for Asimov through Zelazny, and "
            "Conventions for planning your 1989 con season. Spoiler tags "
            "are a courtesy, not a rule -- assume a two-week grace period "
            "after air date. Make it so."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-002",
        "section": "scifi_comics",
        "date": "12/03/88",
        "author": "BRONZEAGE",
        "subject": "The Killing Joke -- does it work for you?",
        "body": (
            "Finally read the Moore/Bolland Batman one-shot from earlier "
            "this year and I am still turning it over. The Joker's 'one "
            "bad day' origin is chilling precisely because it might be a "
            "lie -- 'sometimes I remember it one way, sometimes another.' "
            "But I have to ask: was what happened to Barbara Gordon "
            "necessary to the story, or shock for shock's sake? Bolland's "
            "art is jaw-dropping either way. Where does this rank for you "
            "among this year's Bat-books?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-003",
        "section": "scifi_comics",
        "date": "12/05/88",
        "author": "FOURCOLOR",
        "subject": "Watchmen trade paperback -- the ending debate",
        "body": (
            "Picked up the collected edition of Watchmen over the holiday "
            "and read all twelve issues in two sittings. Rorschach's "
            "journal framing, the pirate comic interludes, the "
            "symmetrical issue -- this is comics doing things only comics "
            "can do. The question for the group: does Ozymandias' plan "
            "hold up? 'I did it thirty-five minutes ago' is the coldest "
            "line in the book, but is Veidt right that the lie saves the "
            "world? And does Rorschach mailing the journal undo it? "
            "No wrong answers, but defend your position."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-004",
        "section": "scifi_comics",
        "date": "12/08/88",
        "author": "KINGKIRBY",
        "subject": "Two years after Crisis -- is the DCU better?",
        "body": (
            "It has been a couple of years since Crisis on Infinite Earths "
            "rewrote the DC Universe, and I want a temperature check. The "
            "Man of Steel relaunch gave us a Superman who feels human "
            "again, Wally West carrying the Flash mantle has heart, and "
            "the new Wonder Woman is superb. But Hawkman continuity is a "
            "maze and I still miss the multiverse some days. For those "
            "who were reading before the Crisis: was the reboot worth it, "
            "or did we lose more than we gained?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-005",
        "section": "scifi_trek",
        "date": "12/06/88",
        "author": "WARPCORE",
        "subject": "Season 2 check-in: Guinan, Pulaski, and the beard",
        "body": (
            "Half a season into year two and the show feels different in "
            "good ways. Whoopi Goldberg as Guinan is inspired -- that "
            "Ten Forward scene with the kid last month had real warmth. "
            "Dr. Pulaski is prickly where Crusher was gentle, and the "
            "friction with Data is interesting to watch. And can we "
            "acknowledge the beard? Riker grew it in 'The Child' and "
            "suddenly the first officer looks like he means business. "
            "The writing feels more confident overall. Agree or disagree: "
            "season 2 is already stronger than season 1?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-006",
        "section": "scifi_trek",
        "date": "12/07/88",
        "author": "TREKKIE88",
        "subject": "'Elementary, Dear Data' -- Moriarty lives!",
        "body": (
            "Monday's episode was the best of the season so far. Data "
            "playing Holmes to Geordi's Watson in the holodeck, and then "
            "Pulaski's challenge backfires when Moriarty walks off the "
            "page -- self-aware, furious, and out of the Doctor's control. "
            "The arch-villain realizing he is a fictional character is a "
            "terrific sci-fi idea, and the actor nailed the menace. "
            "Questions: is Moriarty truly conscious, or just a very good "
            "simulation? And did anyone else catch how Data's 'I do not "
            "dream' moment landed?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-007",
        "section": "scifi_trek",
        "date": "12/13/88",
        "author": "STARFLEETCMDR",
        "subject": "'The Outrageous Okona' -- light fun or filler?",
        "body": (
            "Last night's episode divided my household. Okona the rogue "
            "smuggler is charming, the comedy subplot with the android "
            "wanting to be funny lands some good laughs, and Data doing "
            "stand-up is a highlight. But after the highs of 'Where "
            "Silence Has Lease' and 'Elementary, Dear Data,' this felt "
            "like a breather episode. The guest star turn was fun, though. "
            "Where do you stand: does Trek need the occasional romp, or "
            "should every hour push the envelope?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-008",
        "section": "scifi_who",
        "date": "12/04/88",
        "author": "TARDISFAN",
        "subject": "Season 25 so far -- 'Remembrance of the Daleks'",
        "body": (
            "The Seventh Doctor's second season opened strong with "
            "'Remembrance of the Daleks' back in October. Dalek civil war "
            "on the streets of 1963 London, Ace smashing Daleks with a "
            "baseball bat (instant legend), and the Coal Hill School "
            "callback to the very first episode -- that gave me chills. "
            "The Doctor is playing a much deeper game this season, "
            "manipulating events rather than reacting. Are we seeing a "
            "darker Doctor emerge, or is this just McCoy settling into "
            "the role? 'The Happiness Patrol' was divisive, but "
            "Remembrance was top-tier Who."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-009",
        "section": "scifi_who",
        "date": "12/15/88",
        "author": "REGENERATE",
        "subject": "'The Greatest Show in the Galaxy' -- airing now",
        "body": (
            "Part one aired last night and we are off to the Psychic "
            "Circus. Creepy clowns, a sinister ringmaster, and Ace "
            "confronting her fear of clowns -- the show is leaning into "
            "horror this season and I am here for it. 'Silver Nemesis' "
            "gave us the 25th anniversary Cybermen-vs-Neo-Nazis romp a "
            "few weeks back, but this feels meatier. No spoilers past "
            "part one, please -- three parts to go. Predictions for what "
            "the Gods of Ragnarok actually want?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-010",
        "section": "scifi_movies",
        "date": "12/02/88",
        "author": "MOVIEMAVEN",
        "subject": "They Live -- Carpenter's rowdy satire",
        "body": (
            "Caught John Carpenter's They Live last month and it is "
            "stuck in my head. Roddy Piper as a drifter who finds "
            "sunglasses that reveal the aliens hiding in plain sight -- "
            "yuppies as literal monsters, subliminal billboards, the "
            "whole consumer-culture-as-invasion bit. The alley fight over "
            "putting the glasses on goes on forever and I loved every "
            "second of it. 'I have come here to chew bubblegum and kick "
            "tail, and I am all out of bubblegum.' Dumb, brilliant, or "
            "both? Discuss."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-011",
        "section": "scifi_movies",
        "date": "12/09/88",
        "author": "CELLULOIDSF",
        "subject": "Alien Nation -- the buddy-cop formula with Newcomers",
        "body": (
            "Saw Alien Nation back in October and it has grown on me. "
            "James Caan as the veteran cop, Mandy Patinkin under all that "
            "makeup as the first Newcomer detective in LA -- the "
            "Tenctonese as stand-ins for every immigrant group at once, "
            "the milk-souring-on-alcohol detail, the whole 'you want me "
            "to partner with THAT' setup. Yes, it is a buddy-cop movie "
            "wearing alien makeup, but the world-building is better than "
            "the formula demands. Anybody else think this deserved more "
            "attention than it got?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-012",
        "section": "scifi_movies",
        "date": "12/12/88",
        "author": "CHANNELSURFER",
        "subject": "Sci-fi TV this month -- what else is on?",
        "body": (
            "Between TNG and Doctor Who my week is full, but what else "
            "is everyone watching? The syndicated War of the Worlds "
            "series (the one that pretends the 1953 invasion really "
            "happened) has a great pilot even if the weekly plots are "
            "uneven. Beauty and the Beast on CBS is quietly the most "
            "romantic show on television. And for the Anglophiles: the "
            "BBC's Red Dwarf, which started earlier this year, is the "
            "funniest spaceship comedy I have seen in ages -- Lister and "
            "Rimmer bickering three million years from Earth. What am I "
            "missing?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-013",
        "section": "scifi_books",
        "date": "12/10/88",
        "author": "FOUNDATIONFAN",
        "subject": "'Prelude to Foundation' -- Asimov goes back to Trantor",
        "body": (
            "Asimov's new one finally answers the question we have asked "
            "for decades: how did Hari Seldon invent psychohistory? "
            "Young Seldon on the run across Trantor, Dors Venabili "
            "stealing every scene, the slow assembly of the ideas that "
            "become the Foundation. It reads like a thriller wearing a "
            "history book's clothes. Placement debate: read it first as "
            "chronology suggests, or after the original trilogy as "
            "publication order demands? I say publication order -- the "
            "mysteries land harder when you know where Seldon ends up."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-014",
        "section": "scifi_books",
        "date": "12/14/88",
        "author": "HEINLEINER",
        "subject": "Heinlein's 'To Sail Beyond the Sunset'",
        "body": (
            "Finished Heinlein's latest (last year's novel, Maureen "
            "Johnson Long's life story) and I need to talk about it. "
            "Tying Maureen back into Time Enough for Love and The Number "
            "of the Beast rewards the long-time reader -- the Long "
            "family saga keeps expanding. Late Heinlein is not for "
            "everyone: the lectures are longer, the libertarian streak "
            "wider. But when he is on, nobody writes a competent hero "
            "like him. Is this a fitting capstone, or do you prefer the "
            "middle-period novels?"
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-015",
        "section": "scifi_books",
        "date": "12/16/88",
        "author": "MIRRORSHADES",
        "subject": "'Mona Lisa Overdrive' -- the Sprawl trilogy ends",
        "body": (
            "Gibson's third Sprawl novel (out in October) closes the "
            "loop on Neuromancer and Count Zero, and Molly is back -- "
            "older, harder, going by Sally now. The four interwoven "
            "narratives are a trickier structure than Neuromancer's "
            "straight run, and the ending's metaphysics will fuel "
            "arguments for years. Hot take: Count Zero is the most "
            "readable, Neuromancer the most important, and Mona Lisa "
            "the most ambitious. Rank the trilogy and defend your order."
        ),
        "parent": None,
    },
    {
        "content_id": "scifi-1988-016",
        "section": "scifi_cons",
        "date": "12/20/88",
        "author": "CONVENTIONEER",
        "subject": "Planning 1989 -- which cons are on your list?",
        "body": (
            "Time to start planning next year's con season. The big one "
            "on my calendar is Noreascon 3, the Worldcon in Boston over "
            "Labor Day weekend -- already saving for the hotel. Closer "
            "to home I am eyeing the regional media cons in the spring "
            "and at least one comics show before summer. Questions for "
            "the veterans: how early do you book Worldcon hotels, and "
            "is it worth springing for the full attending membership "
            "versus day passes? Also: costume builders, what are you "
            "working on for '89? I am torn between a Starfleet uniform "
            "and something from the Doctor Who rogues' gallery."
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
