"""Fictional December 1988 travel directory helpers."""

from cis_web_files import offer_download

from datetime import datetime

AIRPORTS = {
    "ATL": "Atlanta", "BOS": "Boston", "DFW": "Dallas/Fort Worth", "DEN": "Denver",
    "LAX": "Los Angeles", "LGA": "New York/LaGuardia", "MIA": "Miami", "MSP": "Minneapolis/St. Paul",
    "ORD": "Chicago/O'Hare", "SFO": "San Francisco", "SEA": "Seattle", "STL": "St. Louis",
}

HOTELS = {
    "CHICAGO": [("Palmer House", 89, "LOOP; RESTAURANT"), ("Chicago Hilton", 98, "MICHIGAN AVE; POOL"), ("Hyatt Regency", 112, "DOWNTOWN; BUSINESS SERVICES")],
    "NEW YORK": [("Waldorf-Astoria", 165, "MIDTOWN; DINING"), ("Plaza Hotel", 185, "FIFTH AVE; DINING"), ("Statler Hilton", 119, "MIDTOWN; MEETING ROOMS")],
    "DALLAS": [("Adolphus Hotel", 82, "DOWNTOWN; RESTAURANT"), ("Hyatt Regency", 95, "DOWNTOWN; AIRPORT DESK"), ("Fairmont Dallas", 105, "ARTS DISTRICT; POOL")],
    "LOS ANGELES": [("Biltmore", 92, "DOWNTOWN; DINING"), ("Century Plaza", 135, "CENTURY CITY; POOL"), ("Airport Hilton", 79, "AIRPORT; SHUTTLE")],
    "SAN FRANCISCO": [("St. Francis", 125, "UNION SQUARE; DINING"), ("Hyatt Regency", 139, "EMBARCADERO; BUSINESS SERVICES"), ("Holiday Inn", 78, "FISHERMAN'S WHARF")],
    "BOSTON": [("Copley Plaza", 118, "BACK BAY; DINING"), ("Parker House", 96, "DOWNTOWN; RESTAURANT"), ("Airport Hilton", 76, "AIRPORT; SHUTTLE")],
}

CITY_ALIASES = {"NYC": "NEW YORK", "LGA": "NEW YORK", "ORD": "CHICAGO", "CHI": "CHICAGO", "LAX": "LOS ANGELES", "SFO": "SAN FRANCISCO", "BOS": "BOSTON", "DFW": "DALLAS"}

def validate_travel_date(value):
    if value.strip().upper() in ("", "OPEN"):
        return "OPEN"
    try:
        selected = datetime.strptime(value.strip(), "%m/%d/%y").date()
    except ValueError:
        return None
    return selected.strftime("%m/%d/%y") if selected.year == 1988 and selected.month == 12 else None

def airport_lines():
    return [f"{code}  {city}" for code, city in sorted(AIRPORTS.items())]

def hotels(city):
    city = CITY_ALIASES.get(city.upper(), city.upper())
    rows = HOTELS.get(city, [])
    return city, [f"{index} {name:<24} FROM ${rate}/NIGHT  {notes}" for index, (name, rate, notes) in enumerate(rows, 1)]

def travelgram(city):
    city = CITY_ALIASES.get(city.upper(), city.upper())
    notes = {
        "CHICAGO": ["Airport delays are possible during winter weather.", "Downtown hotels may fill during conventions."],
        "NEW YORK": ["Allow additional time between Manhattan and the airports.", "Holiday-season demand is heavy in Midtown."],
        "LOS ANGELES": ["A rental automobile is useful for many itineraries.", "Confirm airport and downtown hotel locations carefully."],
        "SAN FRANCISCO": ["Pack for cool evenings and changing bay weather.", "Downtown transit serves many visitor districts."],
        "DALLAS": ["Confirm whether a meeting is near downtown or the airport corridor.", "Winter weather can occasionally disrupt connections."],
        "BOSTON": ["Downtown streets can be confusing to first-time drivers.", "Allow for cold December conditions."],
    }
    return [f"TRAVELGRAM -- {city}", *(notes.get(city) or ["No destination bulletin is on file; consult the directory operator."]), "Fictional December 1988 advisory."]

def traveler_profile(app, updates=None):
    result = {}
    def update(state):
        profile = state.setdefault("traveler_profiles", {}).setdefault(app.current_user_id or "GUEST", {"seat": "NO PREFERENCE", "smoking": "NONSMOKING", "car": "COMPACT", "hotel": "BUSINESS", "home_airport": "ORD", "airline": "NONE", "frequent_traveler": "NONE"})
        profile.setdefault("home_airport", "ORD"); profile.setdefault("airline", "NONE"); profile.setdefault("frequent_traveler", "NONE")
        if updates: profile.update(updates)
        result.update(profile)
    if updates and hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state)
        if updates: app.cis_dynamic.save_state(app, state)
    return dict(result)

def trip_folder(app):
    state = app.cis_dynamic.load_state(app)
    reservations = [item for item in state.get("reservations", []) if item.get("user_id") == app.current_user_id]
    profile = traveler_profile(app)
    lines = ["TRAVELER PREFERENCES", f"HOME {profile['home_airport']}  SEAT {profile['seat']}  {profile['smoking']}", f"CAR {profile['car']}  HOTEL {profile['hotel']}", f"AIRLINE {profile['airline']}  TRAVELER NO. {profile['frequent_traveler']}", "", "ITINERARY ITEMS"]
    for item in reservations:
        if item.get("type") == "HOTEL":
            lines.append(f"{item['confirmation']} HOTEL {item.get('destination')} {item.get('nights', 1)} NIGHT(S) [{item['status']}]")
        else:
            lines.append(f"{item['confirmation']} AIR {item.get('origin')}-{item.get('destination')} {item.get('travel_date', 'OPEN')} [{item['status']}]")
        lines.append("  " + item.get("flight", "")[:72])
    return lines if reservations else [*lines, "No itinerary items recorded."]

def ground_transport(city):
    city = CITY_ALIASES.get(city.upper(), city.upper())
    return [f"GROUND TRANSPORTATION -- {city}", "", "RENTAL CAR (fictional daily rates)", "COMPACT $29  INTERMEDIATE $35  FULL SIZE $43", "Mileage allowance and taxes vary; confirm at the counter.", "", "RAIL INFORMATION", "AMTRAK reservations and schedules: consult station or travel agent.", "Coach and sleeping-car accommodations are subject to availability.", "", "Local taxi, airport bus, and hotel shuttle information is illustrative."]

def export_itinerary(app):
    destination = app.BASE_DIR / "downloads" / f"TRIP_{(app.current_user_id or 'GUEST').replace(',', '_')}.TXT"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text("COMPUSERVE TRAVEL SERVICES\nDECEMBER 1988 FICTIONAL ITINERARY\n\n" + "\n".join(trip_folder(app)) + "\n\nVERIFY ALL SERVICES WITH THE CARRIER OR PROPERTY.\n", encoding="ascii", errors="replace")
    app.cis_dynamic.record_activity(app, app.current_user_id, "TRAVEL", f"Prepared itinerary packet {destination.name}.")
    offer_download(destination)
    return destination

def combined_plan(origin, destination, city, nights, travel_date, schedule_fn):
    outbound = schedule_fn(origin, destination, travel_date, "COACH")[:3]
    return_date = "OPEN RETURN"
    inbound = schedule_fn(destination, origin, return_date, "COACH")[:3]
    hotel_city, lodging = hotels(city)
    return [f"COMBINED TRIP PLAN  {origin}-{destination}  {travel_date}", "", "OUTBOUND OPTIONS", *outbound, "", "RETURN OPTIONS", *inbound, "", f"LODGING -- {hotel_city} / {nights} NIGHT(S)", *lodging, "", "Select and reserve air and lodging separately; all prices are fictional."]

