"""Pets & Animals Forum content module.

Section spec and December 1988 seed posts for the ``pets`` forum
("Pets & Animals Forum"): dogs, cats, birds, fish & aquariums,
small pets, and a vet Q&A section.

Period rules enforced by this module:
* Pet care culture is 1988-plausible: Purina Dog Chow, Alpo,
  Gaines-Burgers, Friskies and 9-Lives (Morris the cat) for cats,
  Milk-Bone dog biscuits, Hartz and Sergeant's flea collars,
  Johnny Cat and Tidy Cat litter. No post-1988 pet foods, gadgets,
  or products (no "premium holistic" brands, no pet GPS, no
  microchip-as-standard talk).
* Holiday pet safety is the December 1988 advice of the day:
  chocolate, poinsettias, tinsel/ribbon, turkey bones, and
  antifreeze are the hazards named. Nothing post-1988.
* Breeds and hobbies are 1988-plausible: cocker spaniels and
  poodles top the AKC registrations, parakeets/budgies and
  cockatiels are the pet-shop birds, and aquarium keepers run
  Metaframe tanks with Tetra food and undergravel filters.
* Nothing references the internet, websites, blogs, email, pet
  webcams, or anything else after December 1988. Advice comes
  from the family vet, the pet-shop owner, Dog World and Cat
  Fancy magazines, and the neighbor with six cats.
"""

FORUM_ID = "pets"
FORUM_TITLE = "Pets & Animals Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("pets_dogs", "Dogs"), ...}
# The coordinator wires this into FORUM_CATALOG["pets"]["sections"].
SECTIONS = {
    "1": ("pets_dogs", "Dogs"),
    "2": ("pets_cats", "Cats"),
    "3": ("pets_birds", "Birds"),
    "4": ("pets_fish", "Fish & Aquariums"),
    "5": ("pets_small", "Small Pets"),
    "6": ("pets_vet", "Ask the Vet"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "pets-1988-001",
        "section": "pets_dogs",
        "date": "12/01/88",
        "author": "SysopPets",
        "subject": "Welcome to the Pets & Animals Forum",
        "body": (
            "Come on in and wipe your paws -- this is the place for pet "
            "people. Six sections: Dogs (breeds, training, and the "
            "eternal puppy question), Cats (Morris would approve), Birds "
            "(budgies to cockatiels), Fish & Aquariums (tanks, filters, "
            "and fin rot), Small Pets (hamsters, gerbils, rabbits, and "
            "guinea pigs), and Ask the Vet (for general questions -- "
            "your real vet always gets the final word on sick animals). "
            "With Christmas three weeks out, expect holiday safety talk. "
            "Introduce your pets and tell us what they are getting in "
            "their stockings."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-002",
        "section": "pets_dogs",
        "date": "12/03/88",
        "author": "PUPPYPLAN",
        "subject": "A Christmas puppy -- wonderful idea or terrible idea?",
        "body": (
            "Every December our kids start campaigning for a puppy under "
            "the tree, and every December I waver. This year they want a "
            "cocker spaniel because the neighbor's is the sweetest dog "
            "alive. My head says a puppy is a fifteen-year commitment, "
            "not a present, and Christmas morning chaos is the worst "
            "possible time to housebreak anything. My heart says look at "
            "those eyes in the pet-shop window. For those who have done "
            "the Christmas puppy: how did it go, honestly? And for the "
            "trainers here -- if we do it, is it better to bring the "
            "puppy home a week BEFORE Christmas so the house is calm, or "
            "am I overthinking this?"
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-003",
        "section": "pets_vet",
        "date": "12/04/88",
        "author": "TINSELGUARD",
        "subject": "Holiday hazards -- chocolate, poinsettia, tinsel, turkey bones",
        "body": (
            "Posting our vet's handout because every December somebody "
            "learns this the hard way. Chocolate is toxic to dogs (the "
            "darker the worse) -- keep the candy dish high and the "
            "stockings dog-proof. Poinsettias will upset stomachs, so "
            "put them out of reach. Tinsel and ribbon look like toys to "
            "cats but can tangle in their intestines -- use garland "
            "instead if your cat is a chewer. No turkey or chicken bones "
            "for any pet; they splinter. And antifreeze tastes sweet and "
            "kills fast, so wipe up garage spills immediately. Our clinic "
            "sees at least one of each every holiday season. Tape this to "
            "your fridge and have a safe Christmas."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-004",
        "section": "pets_cats",
        "date": "12/05/88",
        "author": "NINELIVES",
        "subject": "Cat vs. Christmas tree -- my annual defeat",
        "body": (
            "It is December 5th and my tree has fallen over twice. The "
            "culprit is a nine-pound tabby who believes the ornaments "
            "are prey and the tinsel is spaghetti. Last year I lost "
            "three glass balls and a string of lights. My current "
            "strategy: unbreakable ornaments on the lower branches, no "
            "tinsel at all (see the vet section thread), the tree tied "
            "to the wall with fishing line, and a squirt bottle on "
            "standby. Fellow cat owners -- what actually works? Someone "
            "at work swears by putting orange peels around the base. I "
            "am desperate enough to try citrus warfare."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-005",
        "section": "pets_dogs",
        "date": "12/06/88",
        "author": "CHOWHOUND",
        "subject": "Dog food debate -- Purina Dog Chow vs. the expensive stuff",
        "body": (
            "The pet store just started carrying these pricey new kibbles "
            "that cost twice what Purina Dog Chow costs, and the clerk "
            "gave me a lecture about corn fillers. My last dog lived to "
            "15 on Dog Chow and table scraps, glossy coat and all, so I "
            "am skeptical. But my sister's poodle supposedly stopped "
            "scratching when she switched to the fancy bag. Is there "
            "real science here or is this marketing? What are you "
            "feeding -- Dog Chow, Alpo, Gaines-Burgers, the canned "
            "stuff, or one of the expensive new brands -- and have you "
            "ever seen an actual difference in the dog?"
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-006",
        "section": "pets_birds",
        "date": "12/07/88",
        "author": "BUDGIEBOB",
        "subject": "Teaching my parakeet to talk -- day 40 of 'pretty bird'",
        "body": (
            "Forty days of repeating 'pretty bird' to my blue budgie, "
            "Pete, and yesterday I swear he said something back. It "
            "sounded like static with ambition, but my wife heard it "
            "too. My method: ten minutes every morning before work, "
            "same phrase, lots of praise, and the cage in the living "
            "room where he hears us talk all evening. The pet-shop "
            "owner says males learn faster and a mirror helps keep "
            "them chatty. For the experienced bird people: how long "
            "before your first bird said its first clear word? And "
            "is it true that leaving the radio on while I am at work "
            "helps, or does Pete just learn to imitate the weather "
            "report?"
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-007",
        "section": "pets_fish",
        "date": "12/08/88",
        "author": "TANKGIRL",
        "subject": "Setting up my first 20-gallon tank -- the nitrogen cycle talk",
        "body": (
            "I am setting up a 20-gallon Metaframe tank for Christmas "
            "and the aquarium shop gave me the nitrogen cycle lecture, "
            "which I am now inflicting on you beginners. The short "
            "version: a new tank is not ready for fish on day one. The "
            "undergravel filter needs weeks to grow the bacteria that "
            "eat the ammonia fish produce, or your fish die in poisoned "
            "water. Start with a few hardy danios, feed lightly, test "
            "the water, and add more fish slowly over a month. Patience "
            "is the whole hobby. My plan: Tetra food, a good heater "
            "since the tank is near a drafty window, and plastic plants "
            "until I learn what I am doing. Veterans -- what is the "
            "one beginner mistake you wish someone had stopped you from "
            "making?"
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-008",
        "section": "pets_small",
        "date": "12/09/88",
        "author": "GERBILGANG",
        "subject": "Hamster vs. gerbil -- best first pet for a 7-year-old?",
        "body": (
            "My daughter wants a pet for Christmas and we have agreed "
            "on something small that lives in her room. The contenders: "
            "a hamster (cute, but I hear they are nocturnal and bite "
            "when woken up) or a pair of gerbils (diurnal, social, but "
            "need company so you must get two). The pet shop pushes "
            "hamsters because the cages are cheaper. Parents who have "
            "survived this decision: which did you pick, how much of "
            "the care actually fell on YOU, and what does the cage "
            "smell like after a week? Be honest -- I am the one who "
            "will be cleaning it."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-009",
        "section": "pets_cats",
        "date": "12/10/88",
        "author": "LITTERDUTY",
        "subject": "The litter box wars -- Johnny Cat vs. Tidy Cat vs. the new scoopables",
        "body": (
            "Three cats, three litter boxes, one small apartment -- I am "
            "the world's leading authority on cat litter and I am tired. "
            "Johnny Cat is cheap and my cats like it, but the dust is "
            "awful. Tidy Cat clumps better but tracks everywhere. Now "
            "the store has these new 'scoopable' litters that cost a "
            "fortune and promise you only scoop the clumps. Has anyone "
            "tried them with multiple cats? Do they really control odor "
            "for a week, or is that a single-cat fantasy? Also accepting "
            "litter box placement wisdom -- mine are in the bathroom and "
            "guests have started commenting."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-010",
        "section": "pets_dogs",
        "date": "12/12/88",
        "author": "OBEDIENCE88",
        "subject": "Puppy kindergarten -- is obedience class worth it?",
        "body": (
            "Our 4-month-old beagle has learned exactly three things: "
            "sit (sometimes), come (never), and how to steal socks "
            "(professionally). The kennel club is offering a six-week "
            "puppy kindergarten starting in January -- basic commands, "
            "socialization with other puppies, and they teach the OWNERS "
            "more than the dogs, or so they claim. It costs $60, which "
            "is real money, but the private trainer quoted me three "
            "times that. Graduates of puppy class: did it actually "
            "work, or did your dog just learn to misbehave in a group "
            "setting? And at what age did your dog finally become the "
            "dog you hoped for -- be honest, I need hope."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-011",
        "section": "pets_vet",
        "date": "12/13/88",
        "author": "WORRIEDMOM",
        "subject": "My dog ate ribbon off a present -- wait or vet NOW?",
        "body": (
            "It happened -- despite reading the holiday hazards thread, "
            "my cocker spaniel just ate about six inches of curling "
            "ribbon off a wrapped present while we were decorating. She "
            "seems fine right now, tail wagging, trying to eat more "
            "ribbon. Our vet's office is closed until morning. From "
            "what I have read, ribbon is dangerous because it can saw "
            "through intestines, and you should NEVER pull it if you "
            "see it hanging out. So my plan: no food tonight, watch her "
            "like a hawk, and call the vet first thing in the morning "
            "unless she vomits repeatedly or her belly gets hard and "
            "painful, in which case it is the emergency clinic. Does "
            "that sound right? Posting in case someone else's dog does "
            "this tonight."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-012",
        "section": "pets_birds",
        "date": "12/14/88",
        "author": "COCKATIELCARL",
        "subject": "Cockatiel vs. parakeet -- upgrading from my budgie",
        "body": (
            "Pete the budgie (see my talking thread) has converted me "
            "into a bird person, and now I am eyeing a cockatiel at the "
            "pet shop. Bigger bird, bigger personality, that crest, and "
            "they whistle tunes -- the shop's cockatiel does the Andy "
            "Griffith theme and I nearly handed over my wallet on the "
            "spot. But the cage costs three times as much, they live "
            "15-plus years, and I hear they are dust machines that need "
            "daily misting. Cockatiel owners: is the jump from budgie "
            "worth it? What surprised you most in the first month? And "
            "can a cockatiel and a budgie share a room without driving "
            "each other crazy?"
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-013",
        "section": "pets_cats",
        "date": "12/16/88",
        "author": "FINICKYFELINE",
        "subject": "My cat only eats 9-Lives -- am I raising a snob?",
        "body": (
            "Morris the cat has nothing on my Whiskers. I have tried "
            "Friskies, the store brand, and the expensive cans, and she "
            "sniffs each one like a restaurant critic and walks away. "
            "Only 9-Lives -- the beef flavor, not chicken, do not insult "
            "her -- disappears from the bowl. The vet says she is "
            "healthy and a picky cat is better than a cat that eats "
            "string, but I worry she is missing something nutritionally "
            "on one flavor of one brand. Cat people: is this normal, "
            "or have I created a monster by caving every time? Any "
            "tricks for expanding a finicky cat's menu without a hunger "
            "strike? She held out for two days once and I caved first."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-014",
        "section": "pets_fish",
        "date": "12/17/88",
        "author": "GOLDFISHGUS",
        "subject": "The carnival goldfish is still alive -- now what?",
        "body": (
            "My son won a goldfish at the school carnival in October "
            "and against all odds it is still alive in a one-gallon "
            "bowl on the kitchen counter. I have been doing partial "
            "water changes and feeding Tetra flakes sparingly, but the "
            "poor thing deserves better and I am now accidentally in "
            "the aquarium hobby. Questions: how big a tank does one "
            "goldfish actually need (the pet shop says ten gallons "
            "minimum -- true?), and can it live with tropical fish or "
            "does it need cold water roommates only? Also, is it true "
            "they live for years if you do it right? I need to know "
            "what I signed up for."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-015",
        "section": "pets_small",
        "date": "12/19/88",
        "author": "BUNNYHUTCH",
        "subject": "Indoor rabbit -- litter training really works",
        "body": (
            "Reporting back because six months ago I asked about rabbits "
            "and got great advice: yes, a rabbit can be litter trained, "
            "and yes, ours now uses her box better than the cat uses "
            "his. The keys were spaying (calmed her down enormously), "
            "a big litter box with hay in it, and protecting every "
            "electrical cord in the house because rabbits chew like it "
            "is their job -- which it is. She has the run of the "
            "living room when we are home and a big hutch at night. "
            "Timothy hay, fresh greens, and rabbit pellets from the "
            "feed store. If you are considering a house rabbit: they "
            "are wonderful and they are work. Ask me anything."
        ),
        "parent": None,
    },
    {
        "content_id": "pets-1988-016",
        "section": "pets_dogs",
        "date": "12/21/88",
        "author": "SENIORDOG",
        "subject": "My 13-year-old lab -- making the golden years golden",
        "body": (
            "With all the puppy talk this month, a word for the old "
            "dogs. My chocolate lab is 13, deaf as a post, and moves "
            "like a rusty gate in the morning -- but once she warms up "
            "she still trots to the mailbox with me every day, and her "
            "tail has never stopped. What works for us: a foam pad by "
            "the heat vent instead of the cold floor, shorter walks "
            "twice a day instead of one long one, softened kibble with "
            "warm water, and the vet checks her arthritis every spring. "
            "She does not play fetch anymore; she supervises it. If you "
            "have a senior dog, tell me about them -- the gray muzzles "
            "deserve a thread of their own this Christmas."
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
