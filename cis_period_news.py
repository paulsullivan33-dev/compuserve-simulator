"""Authored December 1988-style dispatches for the historical simulation."""

from datetime import date, timedelta


TOPICS = {
    "WORLD": [
        ("ARMENIAN RELIEF EFFORT CONTINUES", "Rescue crews and relief flights continue work following the destructive Armenian earthquake."),
        ("GORBACHEV OUTLINES SOVIET REDUCTIONS", "The Soviet leader has described planned unilateral reductions in conventional military forces."),
        ("UNITED NATIONS DELEGATES REVIEW SPEECH", "Diplomats are assessing new proposals on arms, regional disputes, and international cooperation."),
        ("MIDEAST DIPLOMACY REMAINS ACTIVE", "Officials continue consultations over prospects for negotiations and regional stability."),
        ("AFGHAN WITHDRAWAL SCHEDULE DISCUSSED", "Attention remains on the timetable for Soviet forces leaving Afghanistan."),
        ("POLISH TALKS DRAW RENEWED ATTENTION", "Government and opposition representatives face continued pressure to resume political discussions."),
        ("BALTIC REFORM GROUPS SEEK GREATER VOICE", "Public organizations in the Baltic republics are pressing cultural and economic reform proposals."),
        ("EAST-WEST RELATIONS SHOW FURTHER THAW", "A series of official exchanges reflects the changing tone between Washington and Moscow."),
        ("CENTRAL AMERICAN PEACE TALKS CONTINUE", "Regional governments are reviewing cease-fire and election commitments."),
        ("SOUTH AFRICAN SANCTIONS DEBATE RENEWED", "Governments and businesses are again weighing economic pressure over apartheid policies."),
        ("PAN AM FLIGHT 103 INVESTIGATION OPENS", "Investigators are gathering evidence after the loss of a passenger aircraft near Lockerbie, Scotland."),
        ("EUROPE PREPARES FOR 1992 COMMON MARKET", "Governments and companies are studying rules planned for a more integrated European market."),
        ("CANADIAN FREE-TRADE DEBATE CONTINUES", "Businesses and provincial leaders are considering the effects of closer trade with the United States."),
        ("CHILE REVIEWS POLITICAL TRANSITION", "Parties are preparing for constitutional steps following the October plebiscite."),
        ("LEBANON CEASE-FIRE EFFORTS FACE STRAIN", "Mediators are attempting to contain renewed fighting and restore political talks."),
        ("PHILIPPINE DEBT TALKS RESUME", "Officials are seeking terms that preserve economic recovery while meeting foreign obligations."),
    ],
    "BUSINESS": [
        ("RJR NABISCO BUYOUT FINANCING EXAMINED", "Bankers and investors continue to assess the record-setting leveraged acquisition."),
        ("WALL STREET CLOSES MIXED IN LIGHT TRADE", "Industrial shares moved narrowly as year-end portfolio adjustments approached."),
        ("DOLLAR TRADING REMAINS UNEVEN", "Currency dealers watched interest-rate signals and trade figures in cautious sessions."),
        ("PERSONAL COMPUTER SALES STAY FIRM", "Dealers report continued business demand for 286 and increasingly capable 386 systems."),
        ("MEMORY-CHIP PRICES DRAW ATTENTION", "Computer makers are monitoring semiconductor supplies and component costs."),
        ("AIRLINES REVIEW WINTER CAPACITY", "Carriers are adjusting schedules and fares for holiday and business travel."),
        ("OIL MARKETS WATCH OPEC PRODUCTION", "Energy traders are evaluating whether members will maintain announced production limits."),
        ("RETAILERS ENTER FINAL HOLIDAY WEEKS", "Merchants are extending store hours and promotions as Christmas approaches."),
        ("JAPANESE AUTOMAKERS EXPAND U.S. OUTPUT", "New manufacturing investment continues to alter the North American automobile market."),
        ("COMMERCIAL PROPERTY LENDING SCRUTINIZED", "Banks are reviewing exposure to rapidly expanding office construction."),
        ("LONG-DISTANCE COMPETITION LOWERS SOME RATES", "Telephone customers are seeing new calling plans and off-peak discounts."),
        ("COMPACT DISC SALES CONTINUE TO CLIMB", "Music retailers report greater consumer interest as player prices decline."),
        ("CATALOG MERCHANTS REPORT HEAVY ORDERS", "Mail-order companies are adding shifts to handle seasonal demand."),
        ("U.S.-CANADA TRADE CHANGES APPROACH", "Companies are preparing paperwork and pricing for the January agreement."),
        ("SMALL FIRMS ADOPT DESKTOP PUBLISHING", "Laser printers and page-layout programs are moving into more offices."),
        ("YEAR-END TAX PLANNING BOOSTS ACTIVITY", "Brokerages and accountants report increased calls ahead of the calendar close."),
    ],
    "TECHNOLOGY": [
        ("386 SYSTEMS MOVE BEYOND ENGINEERING DESKS", "More business buyers are considering 80386 computers as prices ease and software support improves."),
        ("OS/2 SOFTWARE CATALOG GRADUALLY EXPANDS", "Developers continue adapting business applications to the protected-mode operating system."),
        ("VGA ADAPTER CHOICES MULTIPLY", "Compatible display boards are bringing higher resolution and additional colors to non-PS/2 systems."),
        ("2400-BAUD MODEMS REACH MORE HOME USERS", "Falling equipment prices are making faster online sessions practical for additional callers."),
        ("MORRIS NETWORK WORM PROMPTS SECURITY REVIEW", "Computer centers are examining passwords, services, and recovery plans after November's disruption."),
        ("CD-ROM DATABASES ENTER LIBRARIES", "Reference publishers are placing large indexes and collections on optical discs."),
        ("LAPTOP COMPUTERS SHED WEIGHT", "Manufacturers are balancing battery life, displays, storage, and compatibility in portable designs."),
        ("DESKTOP PUBLISHING TOOLS ADD TYPE CONTROL", "New software gives small offices more precise page composition on personal computers."),
        ("EXPANDED MEMORY STANDARDS REMAIN IMPORTANT", "DOS users continue relying on LIM-compatible boards for large spreadsheets and databases."),
        ("SCSI GAINS SUPPORT AMONG PERIPHERAL MAKERS", "Disk and scanner vendors are adopting the flexible interface across several computer families."),
        ("MACINTOSH MULTIFINDER USE GROWS", "Users are learning to divide limited memory among concurrently active applications."),
        ("RISC PROCESSORS ATTRACT WORKSTATION INTEREST", "Computer designers are pursuing simplified instruction sets for technical systems."),
        ("FAX BOARDS LINK PERSONAL COMPUTERS", "Add-in products are beginning to combine document preparation and facsimile transmission."),
        ("LOCAL-AREA NETWORK PRICES DECLINE", "Smaller offices are evaluating shared disks and printers as networking costs fall."),
        ("LASER PRINTER COMPATIBILITY IMPROVES", "More applications and font packages support common page-description methods."),
        ("SHAREWARE DISTRIBUTION EXPANDS ONLINE", "Authors are using bulletin boards and information services to circulate trial software."),
    ],
    "SCIENCE": [
        ("ATLANTIS COMPLETES CLASSIFIED SHUTTLE MISSION", "Space shuttle Atlantis has returned after deploying a Defense Department payload."),
        ("PHOBOS PROBES CONTINUE MARS APPROACH", "Soviet controllers are preparing the two spacecraft for observations of Mars and its moon Phobos."),
        ("HUBBLE TELESCOPE PREPARATIONS ADVANCE", "Engineers continue testing the large orbiting observatory ahead of its planned shuttle launch."),
        ("HIGH-TEMPERATURE SUPERCONDUCTOR WORK CONTINUES", "Laboratories are testing ceramic compounds and searching for practical current-carrying applications."),
        ("VOYAGER 2 NEPTUNE ENCOUNTER PLANNED", "Flight teams are refining observations for the spacecraft's August 1989 passage."),
        ("OZONE LOSS REMAINS RESEARCH PRIORITY", "Atmospheric scientists are gathering evidence on seasonal Antarctic ozone depletion."),
        ("GENOME MAPPING PROPOSALS RECEIVE REVIEW", "Researchers and agencies are debating methods for a coordinated human genetic map."),
        ("CLIMATE MODELS TEST GREENHOUSE FORECASTS", "Scientists are comparing computer projections with long-term temperature records."),
        ("ARCHAEOLOGISTS APPLY NEW DATING METHODS", "Improved laboratory techniques are refining chronologies at several excavation sites."),
        ("RADIO ASTRONOMERS SURVEY DISTANT GALAXIES", "New receiver systems are extending sensitive observations of faint radio sources."),
        ("ANTARCTIC TEAMS BEGIN SUMMER FIELD SEASON", "Research stations are supporting studies of ice, weather, geology, and marine life."),
        ("COMET HALLEY DATA STILL UNDER ANALYSIS", "Astronomers continue comparing spacecraft and ground observations from the 1986 encounter."),
        ("MEDICAL IMAGING COMPUTERS IMPROVE DETAIL", "Hospitals are evaluating faster processing for CT and magnetic-resonance studies."),
        ("DEEP-SEA VENTS YIELD NEW SPECIMENS", "Oceanographers are studying organisms supported by chemical energy rather than sunlight."),
        ("PALEONTOLOGISTS DEBATE EXTINCTION EVIDENCE", "Researchers continue examining impact and volcanic explanations for the end-Cretaceous event."),
        ("SOLAR OBSERVERS TRACK ACTIVE REGIONS", "Stations are monitoring sunspots and radio emissions as the solar cycle strengthens."),
    ],
}


def archive():
    stories = []
    start = date(1988, 12, 1)
    for category, topics in TOPICS.items():
        for index, (title, summary) in enumerate(topics):
            stories.append({
                "id": f"{category[:3]}-{index + 1:02d}", "category": category,
                "title": title, "summary": summary,
                "published": (start + timedelta(days=index % 22)).strftime("%m/%d/88"),
                "source": "CIS PERIOD NEWS WIRE",
            })
    return stories


def edition(app, count=12):
    stories = archive()
    user_id = app.current_user_id or "GUEST"
    state = app.cis_dynamic.load_state(app)
    seen = state.setdefault("period_news_seen", {}).setdefault(user_id, [])
    unseen = [story for story in stories if story["id"] not in seen]
    if len(unseen) < count:
        seen.clear()
        unseen = stories[:]
    selected = app.cis_dynamic.rng(f"period-news-{len(seen) // count}", user_id).sample(unseen, min(count, len(unseen)))
    seen.extend(story["id"] for story in selected)
    state["period_news_seen"][user_id] = seen[-len(stories):]
    app.cis_dynamic.save_state(app, state)
    return selected
