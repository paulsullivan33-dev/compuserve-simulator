"""Deterministic December 1988 weather operations for fictional travel."""

import hashlib
from datetime import datetime


STORMS = (
    {"id": "GL-1216", "start": 16, "end": 18, "name": "GREAT LAKES SNOW", "airports": {"ORD", "DTW", "STL"}, "summary": "Heavy snow, deicing delays, and reduced runway acceptance rates."},
    {"id": "NE-1222", "start": 22, "end": 24, "name": "NORTHEAST COASTAL STORM", "airports": {"LGA", "BOS", "DCA"}, "summary": "Snow and coastal winds are disrupting holiday operations."},
    {"id": "TX-1227", "start": 27, "end": 28, "name": "CENTRAL ICE ADVISORY", "airports": {"DFW", "STL", "ORD"}, "summary": "Freezing rain is limiting departures and surface transportation."},
)


def _travel_day(value):
    try:
        return datetime.strptime(value, "%m/%d/%y").day
    except (TypeError, ValueError):
        return None


def storm_for(reservation):
    day = _travel_day(reservation.get("travel_date"))
    if day is None or reservation.get("type", "AIR") != "AIR":
        return None
    route = {reservation.get("origin"), reservation.get("destination")}
    return next((storm for storm in STORMS if storm["start"] <= day <= storm["end"] and route & storm["airports"]), None)


def severity(confirmation, storm):
    value = int(hashlib.sha256(f"{confirmation}:{storm['id']}".encode()).hexdigest()[:8], 16) % 10
    return "CANCELLED" if value < 2 else "MAJOR DELAY" if value < 6 else "WEATHER WATCH"


def bulletin_lines(day=None):
    active_day = day or datetime.now().day
    lines = ["DECEMBER 1988 TRAVEL WEATHER OPERATIONS", ""]
    for storm in STORMS:
        marker = "ACTIVE" if storm["start"] <= active_day <= storm["end"] else "PAST" if active_day > storm["end"] else "FORECAST"
        airports = "/".join(sorted(storm["airports"]))
        lines.extend([f'{storm["id"]} [{marker}] DEC {storm["start"]}-{storm["end"]}  {storm["name"]}', f"  {airports}: {storm['summary']}"])
    lines.extend(["", "All weather, schedules, accommodations, and alternatives are fictional."])
    return lines


def evaluate_reservations(app):
    """Flag newly affected trips once and return their confirmation numbers."""
    created = []

    def update(state):
        disruptions = state.setdefault("travel_disruptions", {})
        for reservation in state.get("reservations", []):
            if reservation.get("user_id") != app.current_user_id or reservation.get("status") == "CANCELLED":
                continue
            storm = storm_for(reservation)
            confirmation = reservation.get("confirmation")
            if not storm or not confirmation or confirmation in disruptions:
                continue
            level = severity(confirmation, storm)
            disruptions[confirmation] = {
                "confirmation": confirmation, "storm": storm["id"], "name": storm["name"],
                "severity": level, "status": "ACTION REQUIRED", "choice": None,
                "route": f'{reservation.get("origin")}-{reservation.get("destination")}',
                "travel_date": reservation.get("travel_date"),
            }
            reservation["pre_disruption_status"] = reservation.get("status", "CONFIRMED")
            reservation["status"] = f"{level} - ACTION REQUIRED"
            created.append(confirmation)

    if hasattr(app, "update_json_atomic"):
        app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)

    for confirmation in created:
        state = app.cis_dynamic.load_state(app)
        disruption = state["travel_disruptions"][confirmation]
        app.cis_dynamic.schedule_event(app, "mail", {
            "to": app.current_user_id, "from": "TRAVEL WEATHER DESK",
            "subject": f"ACTION REQUIRED {confirmation} {disruption['severity']}",
            "body": f"{disruption['name']} affects {disruption['route']} on {disruption['travel_date']}. "
                    "Enter GO TRAVEL and choose Weather Operations for alternate flight, rail, "
                    "accommodation, standby, or cancellation choices.",
        }, app.cis_dynamic.simulation_datetime())
        app.cis_dynamic.record_activity(app, app.current_user_id, "TRAVEL", f"Weather action required for {confirmation}.")
    if created:
        app.cis_dynamic.process_events(app)
    return created


def member_lines(app):
    state = app.cis_dynamic.load_state(app)
    items = [item for item in state.get("travel_disruptions", {}).values() if any(
        reservation.get("confirmation") == item["confirmation"] and reservation.get("user_id") == app.current_user_id
        for reservation in state.get("reservations", [])
    )]
    lines = bulletin_lines(app.cis_dynamic.simulation_day().day)
    lines.extend(["", "MY AFFECTED ITINERARIES"])
    for item in items:
        lines.append(f'{item["confirmation"]} {item["route"]} {item["travel_date"]} [{item["status"]}]')
        lines.append(f'  {item["name"]} / {item["severity"]}' + (f' / {item["choice"]}' if item.get("choice") else ""))
    if not items:
        lines.append("No member itineraries are affected.")
    return lines


def resolve(app, confirmation, choice):
    confirmation = confirmation.upper()
    choice = choice.upper()
    state = app.cis_dynamic.load_state(app)
    disruption = state.get("travel_disruptions", {}).get(confirmation)
    reservation = next((item for item in state.get("reservations", []) if item.get("confirmation") == confirmation and item.get("user_id") == app.current_user_id), None)
    if not disruption or not reservation:
        return "Affected itinerary not found."
    if disruption.get("status") == "RESOLVED":
        return f"Weather choice already recorded: {disruption.get('choice')}."
    if choice == "FLIGHT":
        options = [line for line in app.cis_dynamic.flight_schedule(reservation["origin"], reservation["destination"], reservation.get("travel_date", "OPEN")) if "CANCELLED" not in line]
        if not options:
            return "No alternate flight is currently available."
        reservation["flight"] = options[0]
        reservation["status"] = "REBOOKED - WEATHER"
        result = "Alternate flight confirmed from controlled availability."
    elif choice == "RAIL":
        reservation["flight"] = f'AMTRAK PROTECTIVE ROUTING {reservation["origin"]}-{reservation["destination"]} - CALL STATION'
        reservation["status"] = "REBOOKED - RAIL"
        result = "Protective rail routing added; station confirmation is required."
    elif choice == "HOTEL":
        reservation["status"] = "WEATHER HOTEL REQUESTED"
        disruption["hotel"] = "AIRPORT HOTEL WAITLIST - ONE NIGHT"
        result = "Airport hotel waitlist requested; availability is not guaranteed."
    elif choice == "STANDBY":
        reservation["status"] = "WEATHER STANDBY"
        result = "Original itinerary retained on weather standby."
    elif choice == "CANCEL":
        reservation["status"] = "CANCELLED - WEATHER"
        result = "Itinerary cancelled under the fictional weather waiver."
    else:
        return "Choose FLIGHT, RAIL, HOTEL, STANDBY, or CANCEL."
    disruption.update({"status": "RESOLVED", "choice": choice, "resolved": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")})
    reservation["weather_resolution"] = choice
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": "TRAVEL WEATHER DESK", "subject": f"WEATHER CHOICE {confirmation} - {choice}", "body": result})
    app.cis_dynamic.record_activity(app, app.current_user_id, "TRAVEL", f"Weather choice {choice} recorded for {confirmation}.")
    return result


def service(app):
    evaluate_reservations(app)
    app.text_page("travel", "TRAVEL WEATHER OPERATIONS", member_lines(app))
    confirmation = input("Affected confirmation, or RETURN ! ").strip().upper()
    if not confirmation:
        return
    choice = input("FLIGHT, RAIL, HOTEL, STANDBY, or CANCEL ! ").strip().upper()
    app.ansi_scroll(resolve(app, confirmation, choice), 0.01)
