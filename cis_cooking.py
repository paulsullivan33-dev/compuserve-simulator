"""Cooking Forum content module.

Section spec and December 1988 seed posts for the ``cooking`` forum
("Cooking Forum"): recipes, holiday baking, cast iron & cookware,
microwave cooking, canning & preserving, and restaurant talk.

Period rules enforced by this module:
* Recipes and equipment are 1988-plausible: stand mixers (KitchenAid),
  Cuisinart food processors, Rival Crock-Pot slow cookers, Presto
  pressure canners, Ball/Kerr Mason jars, Lodge and vintage
  Griswold/Wagner cast iron, Revere Ware copper-bottom, CorningWare,
  Pyrex, Magnalite, Le Creuset, Calphalon. No post-1988 equipment
  is ever mentioned (no air fryers, no Instant Pot or electric
  pressure cookers, no sous vide circulators, no silicone baking
  accessories marketed online).
* Microwaves are fine -- countertop microwaves (Amana Radarange,
  Sharp Carousel, Litton, GE, Panasonic) were mainstream by 1988
  and microwave cookbooks were bestsellers.
* Restaurant talk covers 1988-era chains: Red Lobster, Olive Garden,
  Outback Steakhouse (first opened 1988), Applebee's, Chili's,
  Bennigan's, Chi-Chi's, Steak and Ale, Fuddruckers, Sizzler,
  Ponderosa, TGI Friday's, Boston Chicken, Pizza Hut, Domino's.
* Nothing references the internet, websites, blogs, YouTube, email,
  or anything else after December 1988. Recipes come from
  cookbooks, magazines (Bon Appetit, Gourmet, Better Homes and
  Gardens), the Pillsbury Bake-Off, and family index cards.
"""

FORUM_ID = "cooking"
FORUM_TITLE = "Cooking Forum"

# Section spec, mirroring the FORUM_CATALOG shape:
#   {"1": ("cooking_recipes", "Recipes"), ...}
# The coordinator wires this into FORUM_CATALOG["cooking"]["sections"].
SECTIONS = {
    "1": ("cooking_recipes", "Recipes"),
    "2": ("cooking_baking", "Holiday Baking"),
    "3": ("cooking_castiron", "Cast Iron & Cookware"),
    "4": ("cooking_microwave", "Microwave Cooking"),
    "5": ("cooking_canning", "Canning & Preserving"),
    "6": ("cooking_restaurants", "Restaurant Talk"),
}

# Seed posts. Field format matches computer_communities.json message
# entries: content_id/section/date/author/subject/body/parent.
SEED_POSTS = [
    {
        "content_id": "cooking-1988-001",
        "section": "cooking_recipes",
        "date": "12/01/88",
        "author": "KitchenSysop",
        "subject": "Welcome to the Cooking Forum",
        "body": (
            "Pull up a chair. This is the place to swap recipes, talk "
            "cookware, and argue about the proper way to season a skillet. "
            "We have sections for everyday recipes, holiday baking (it is "
            "December, so expect cookie fever), cast iron and cookware, "
            "microwave cooking, canning and preserving, and restaurant "
            "talk. When you post a recipe, list your measurements -- cups "
            "and teaspoons, please, no metric conversions required. And "
            "cite your source: grandmother's index card, the red-checked "
            "Better Homes and Gardens cookbook, Bon Appetit, wherever it "
            "came from. Happy cooking."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-002",
        "section": "cooking_microwave",
        "date": "12/03/88",
        "author": "NUKEMAMA",
        "subject": "Microwave fudge -- five minutes, no fail",
        "body": (
            "For everyone making holiday candy: stop standing over a "
            "double boiler. My microwave fudge has never failed me. One "
            "pound powdered sugar, 1/2 cup cocoa, 1/4 teaspoon salt, 1/4 "
            "cup milk, 1/2 cup butter, 1 teaspoon vanilla, 1 cup chopped "
            "walnuts. Combine everything but vanilla and nuts in a 2-quart "
            "glass casserole. Microwave on HIGH 3 minutes, stir, then 2 "
            "more minutes. Beat in vanilla, fold in nuts, spread in a "
            "buttered 8-inch pan. Sets up firm in about an hour. I use a "
            "Sharp Carousel and it comes out perfect every Christmas. "
            "Anyone tried the peanut-butter-chip variation?"
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-003",
        "section": "cooking_baking",
        "date": "12/05/88",
        "author": "FRUITCAKEFAN",
        "subject": "In defense of fruitcake",
        "body": (
            "Every December the fruitcake jokes start, and every December "
            "I defend the poor thing. A PROPER fruitcake -- dark, aged "
            "with brandy since October, full of pecans and candied cherries "
            "-- is magnificent. The problem is the grocery-store doorstop "
            "version that gets regifted for a decade. Mine uses a full "
            "pound of butter, a cup of dark rum in the batter, and then it "
            "rests wrapped in cheesecloth, getting a tablespoon of rum "
            "every week until Christmas. Slice it thin with sharp cheddar. "
            "Tell me I am wrong."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-004",
        "section": "cooking_castiron",
        "date": "12/04/88",
        "author": "SKILLETKING",
        "subject": "Seasoning a rusty skillet -- the full rescue",
        "body": (
            "Found a crusty old Wagner Ware skillet at a flea market for "
            "three dollars and brought it back from the dead. Here is the "
            "method: scrub off the rust with steel wool and hot water (no "
            "soap on this step), dry it on a warm burner immediately, then "
            "rub the thinnest possible coat of Crisco over the whole thing "
            "-- inside, outside, handle. Bake upside down at 450 for an "
            "hour, let it cool in the oven, repeat three times. It is now "
            "black as midnight and fried an egg this morning that slid "
            "right out. Grandmother's Griswold #8 is next on the bench."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-005",
        "section": "cooking_baking",
        "date": "12/07/88",
        "author": "COOKIEPLATE",
        "subject": "Spritz cookies -- which press?",
        "body": (
            "It is not Christmas at my house without spritz. I have been "
            "using my mother's old Mirro cookie press for twenty years "
            "and the disks are finally wearing out. Before I buy a new "
            "one: is the new Mirro as good as the old ones? Anyone using "
            "the electric press? My recipe, for the record: 1 cup butter, "
            "2/3 cup sugar, 1 egg, 1 teaspoon vanilla, 2-1/4 cups flour. "
            "Press onto ungreased sheets, bake at 400 for 6-8 minutes. The "
            "Christmas-tree disk with green sugar is the one the kids "
            "fight over."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-006",
        "section": "cooking_recipes",
        "date": "12/06/88",
        "author": "PASTRYCHEF",
        "subject": "Cuisinart pie crust -- 30 seconds flat",
        "body": (
            "If you own a Cuisinart and you are still cutting butter in "
            "with a pastry blender, you are working too hard. Two and a "
            "half cups flour, a teaspoon of salt, a tablespoon of sugar in "
            "the work bowl -- pulse to mix. Add a cup of cold butter cut "
            "in chunks plus a quarter cup of Crisco, pulse until it looks "
            "like coarse meal. Then drizzle in ice water through the feed "
            "tube with the machine running until it just comes together. "
            "Thirty seconds, perfect flaky crust, and your hands stay warm. "
            "Chill it an hour before rolling. Who else is team food "
            "processor for pastry?"
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-007",
        "section": "cooking_canning",
        "date": "12/08/88",
        "author": "JARLADY",
        "subject": "Cranberry-orange preserves for gift baskets",
        "body": (
            "Making up gift baskets this year and cranberry-orange "
            "preserves are the star. Four cups cranberries, two cups sugar, "
            "juice and grated peel of two oranges, a cup of water. Simmer "
            "until the berries pop and it sheets off a spoon, about 15 "
            "minutes. Ladle into hot sterilized half-pint Ball jars, wipe "
            "the rims, process 10 minutes in a boiling-water bath. They "
            "seal with that beautiful POP. Tie a ribbon around the lid and "
            "you have a gift that beats anything from a store. Made 24 "
            "jars last weekend."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-008",
        "section": "cooking_restaurants",
        "date": "12/10/88",
        "author": "STEAKNIGHT",
        "subject": "Outback Steakhouse -- the new place in town?",
        "body": (
            "There is a new steakhouse that just opened here -- Outback "
            "Steakhouse, Australian theme, big portions. Had the prime "
            "rib special last Friday and it was genuinely good: thick "
            "cut, proper char, and the bloomin' onion appetizer is a "
            "spectacle. Prices are reasonable, cheaper than Steak and Ale "
            "for comparable quality. It is loud in there on a Friday night "
            "but the service was fast. Has anyone else tried one? They "
            "seem to be expanding quickly."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-009",
        "section": "cooking_recipes",
        "date": "12/09/88",
        "author": "CROCKPOTCARL",
        "subject": "Crock-Pot holiday party strategy",
        "body": (
            "Hosting the office party and my Rival Crock-Pot is doing the "
            "heavy lifting. The plan: Swedish meatballs in the morning "
            "(frozen meatballs, grape jelly, chili sauce -- do not knock it "
            "until you try it), then rinse it out and do hot spiced cider "
            "for the evening crowd. Two dishes, one pot, zero stress. The "
            "low-and-slow setting means I can actually talk to my guests "
            "instead of babysitting the stove. What is everyone else "
            "making in the slow cooker this season?"
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-010",
        "section": "cooking_restaurants",
        "date": "12/12/88",
        "author": "DINNEROUT",
        "subject": "Olive Garden vs. Red Lobster -- anniversary pick",
        "body": (
            "Anniversary dinner dilemma: Olive Garden or Red Lobster? Both "
            "are running holiday specials. Olive Garden has the unlimited "
            "salad and breadsticks going for it, and the fettuccine alfredo "
            "is comfort in a bowl. Red Lobster has the cheddar biscuits "
            "and the popcorn shrimp is hard to beat. For a quiet table and "
            "good service, which would you pick? Leaning Olive Garden "
            "because my wife loves the minestrone, but I could be swayed."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-011",
        "section": "cooking_microwave",
        "date": "12/11/88",
        "author": "TURKEYTIMER",
        "subject": "Microwave vs. oven for the big bird -- a caution",
        "body": (
            "Public service announcement before anyone gets ambitious: do "
            "NOT try to roast your Christmas turkey in the microwave. I "
            "know the Amana Radarange manual has a poultry chart, and yes, "
            "a 10-pound bird technically fits, but it comes out pale and "
            "rubbery and the skin never crisps. Where the microwave DOES "
            "earn its keep on Christmas: reheating gravy without scorching, "
            "melting butter for basting, warming dinner rolls in 30 "
            "seconds, and softening the cream cheese for the holiday dip. "
            "Use the right tool for the right job."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-012",
        "section": "cooking_castiron",
        "date": "12/13/88",
        "author": "FLEAMARKETFIND",
        "subject": "Griswold vs. Lodge -- is vintage worth the hunt?",
        "body": (
            "I keep hearing that old Griswold and Wagner Ware skillets are "
            "better than anything new because the cooking surface was "
            "milled smooth at the factory. Is it true, or nostalgia? New "
            "Lodge is affordable, pre-seasoned, and made in Tennessee, but "
            "the surface is pebbly compared to my aunt's 1940s Griswold. "
            "For those who own both: does the vintage smooth surface "
            "actually cook better, or does a well-seasoned new pan catch up "
            "after a year of bacon and cornbread? Flea market season is "
            "coming and I need a strategy."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-013",
        "section": "cooking_baking",
        "date": "12/14/88",
        "author": "GINGERBREAD",
        "subject": "Gingerbread house that survives until Christmas",
        "body": (
            "Third annual gingerbread house with the grandkids, and this "
            "year it will NOT collapse on December 23rd. Lessons learned: "
            "use construction-grade gingerbread (extra flour, bake it hard "
            "-- nobody is eating the walls), royal icing as mortar made "
            "with meringue powder so it sets like concrete, and let the "
            "walls dry overnight before adding the roof. Candy canes for "
            "the fence, gumdrops on the roofline, shredded coconut for "
            "snow. My 1986 house slid off its base; the 1987 one is still "
            "standing in my memory as a warning."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-014",
        "section": "cooking_canning",
        "date": "12/15/88",
        "author": "PRESSUREPETE",
        "subject": "Pressure canner safety -- green beans done right",
        "body": (
            "With everyone putting up the last of the fall harvest, a "
            "reminder from your friendly canning nag: green beans are LOW "
            "ACID and must go in a pressure canner, never a water bath. "
            "My Presto runs at 10 pounds of pressure (check your gauge "
            "yearly at the extension office), pints for 20 minutes, quarts "
            "for 25. Raw-pack or hot-pack, your choice, but do not cut "
            "corners on the time. Botulism does not care how good your "
            "grandmother's recipe tasted. Tomatoes are fine in a water "
            "bath only with added lemon juice. Stay safe out there."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-015",
        "section": "cooking_restaurants",
        "date": "12/17/88",
        "author": "CHIMICHANGA",
        "subject": "Chi-Chi's -- worth it for the fried ice cream?",
        "body": (
            "Took the family to Chi-Chi's last night. The sizzling fajita "
            "platter is theater and the kids loved it, the chimichangas "
            "were crisp without being greasy, and yes -- the fried ice "
            "cream is worth the trip by itself. Service was friendly if a "
            "little slow on a Saturday. Prices are fair for the portions. "
            "How does it stack up against El Torito or the local "
            "family-owned places in your town? I am trying to decide if it "
            "becomes our regular Mexican spot or stays a special-occasion "
            "place."
        ),
        "parent": None,
    },
    {
        "content_id": "cooking-1988-016",
        "section": "cooking_recipes",
        "date": "12/20/88",
        "author": "CHRISTMASEVE",
        "subject": "Christmas Eve menu -- help me finalize",
        "body": (
            "Five days out and I need a sanity check on the Christmas Eve "
            "menu for twelve. Appetizers: shrimp cocktail and the cheese "
            "ball rolled in pecans. Main: standing rib roast with Yorkshire "
            "pudding -- doing it in the Magnalite roaster. Sides: the "
            "green bean casserole with the French's onions on top (it is "
            "tradition, do not fight me), mashed potatoes in the KitchenAid, "
            "and my sister's ambrosia salad. Dessert: the Buche de Noel "
            "from the December Bon Appetit. Am I missing anything? And "
            "what time do you put a 12-pound roast in for a 7 o'clock "
            "dinner?"
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
