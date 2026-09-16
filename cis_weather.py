"""Modern weather data rendered for the period terminal."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cis_storage import read_reference_cache, write_reference_cache


GEOCODE_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {0: "CLEAR", 1: "MAINLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST", 45: "FOG", 48: "RIME FOG", 51: "LIGHT DRIZZLE", 53: "DRIZZLE", 55: "HEAVY DRIZZLE", 61: "LIGHT RAIN", 63: "RAIN", 65: "HEAVY RAIN", 71: "LIGHT SNOW", 73: "SNOW", 75: "HEAVY SNOW", 80: "RAIN SHOWERS", 81: "RAIN SHOWERS", 82: "HEAVY SHOWERS", 85: "SNOW SHOWERS", 86: "HEAVY SNOW SHOWERS", 95: "THUNDERSTORM", 96: "THUNDERSTORM WITH HAIL", 99: "SEVERE THUNDERSTORM WITH HAIL"}


class LiveWeatherError(RuntimeError):
    pass


def _get_json(url, opener, timeout):
    request = Request(url, headers={"User-Agent": "ClassicCompuServe/1.0 (live weather)"})
    with opener(request, timeout=timeout) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise LiveWeatherError(str(payload.get("reason") or "Weather provider rejected the request."))
    return payload


def live_weather(city, base_dir, timeout=5, opener=urlopen):
    query = city.strip() or "Chicago"
    cache_key = query.casefold()
    cached = read_reference_cache(base_dir, "weather", cache_key, max_age_hours=.5)
    if cached is not None:
        return {**cached, "cached": True}
    try:
        location = read_reference_cache(base_dir, "weather-location", cache_key, max_age_hours=24 * 30)
        if location is None:
            geo = _get_json(f"{GEOCODE_API}?{urlencode({'name': query, 'count': 1, 'language': 'en', 'format': 'json'})}", opener, timeout)
            if not geo.get("results"):
                raise LiveWeatherError("Location not found.")
            found = geo["results"][0]
            location = {key: found.get(key) for key in ("name", "admin1", "country", "latitude", "longitude", "timezone")}
            write_reference_cache(base_dir, "weather-location", cache_key, location)
        parameters = {"latitude": location["latitude"], "longitude": location["longitude"], "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m", "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max", "temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "precipitation_unit": "inch", "timezone": "auto", "forecast_days": 3}
        forecast = _get_json(f"{FORECAST_API}?{urlencode(parameters)}", opener, timeout)
        result = {"location": location, "current": forecast.get("current", {}), "daily": forecast.get("daily", {}), "cached": False}
        write_reference_cache(base_dir, "weather", cache_key, result)
        return result
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError, LiveWeatherError) as exc:
        stale = read_reference_cache(base_dir, "weather", cache_key, allow_expired=True)
        if stale is not None:
            return {**stale, "cached": True, "stale": True}
        raise LiveWeatherError(f"Live weather unavailable: {exc}") from exc


def weather_lines(report):
    location, current, daily = report["location"], report["current"], report["daily"]
    place = ", ".join(part for part in (location.get("name"), location.get("admin1"), location.get("country")) if part)
    code = int(current.get("weather_code", -1))
    lines = [place.upper(), "LIVE WEATHER WIRE -- MODERN CONDITIONS", "", f'OBSERVATION {current.get("time", "")}', f'CONDITIONS  {WEATHER_CODES.get(code, f"CODE {code}")}', f'TEMPERATURE {current.get("temperature_2m", "?")} F', f'FEELS LIKE  {current.get("apparent_temperature", "?")} F', f'HUMIDITY    {current.get("relative_humidity_2m", "?")} PERCENT', f'WIND        {current.get("wind_direction_10m", "?")} DEG AT {current.get("wind_speed_10m", "?")} MPH', f'GUSTS       {current.get("wind_gusts_10m", "?")} MPH', "", "THREE-DAY OUTLOOK"]
    dates = daily.get("time", [])
    for index, date in enumerate(dates):
        lines.append(f'{date}  {WEATHER_CODES.get(int(daily.get("weather_code", [-1])[index]), "UNKNOWN"):<18} HIGH {daily.get("temperature_2m_max", ["?"])[index]}  LOW {daily.get("temperature_2m_min", ["?"])[index]}  PRECIP {daily.get("precipitation_probability_max", ["?"])[index]}%')
    if report.get("cached"):
        lines.extend(["", "CACHED COPY" + (" -- PROVIDER CURRENTLY UNAVAILABLE." if report.get("stale") else ".")])
    lines.extend(["", "DATA: OPEN-METEO. OUTSIDE THE 1988 SIMULATION."])
    return lines


# ===========================================================================
# CONTENT PACK 3: Weather Wire & Ski Reports (December 1988 period content)
# ===========================================================================
# The block below is period-flavored simulation content. Forecasts, base
# depths, and lift counts are plausible and generic -- they are NOT real
# historical records and are not presented as such. Keep them timeless:
# nothing here should reference anything after 1988.
from datetime import date as _date
from typing import Dict as _Dict
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple


def _wx_day(day: _Optional[_date] = None) -> _date:
    """Resolve the simulation day, defaulting to the session-aware one."""
    if day is not None:
        return day
    try:
        from cis_dynamic import simulation_day
        return simulation_day()
    except Exception:
        return _date(1988, 12, 15)


# ---------------------------------------------------------------------------
# U.S. city forecasts: 12 cities, 3 deterministic daily variants each.
# Format per variant: (condition, high, low).
# Plausible December winter norms -- generic, not historical records.
# ---------------------------------------------------------------------------
_CITY_FORECASTS: _Dict[str, _List[_Tuple[str, int, int]]] = {
    "NEW YORK":      [("Sunny and cold, gusty winds", 34, 22),
                      ("Partly cloudy, flurries late", 32, 24),
                      ("Overcast, cold rain possible", 38, 30)],
    "CHICAGO":       [("Lake-effect snow showers", 28, 15),
                      ("Sunny but bitter, wind chill below zero", 22, 6),
                      ("Cloudy, snow overnight", 26, 18)],
    "BOSTON":        [("Snow developing by evening", 31, 20),
                      ("Clear and frigid", 28, 14),
                      ("Morning flurries, afternoon sun", 33, 21)],
    "WASHINGTON":    [("Partly cloudy, mild for December", 46, 30),
                      ("Light rain ending by noon", 44, 34),
                      ("Sunny and crisp", 42, 26)],
    "ATLANTA":       [("Sunny, unseasonably mild", 58, 38),
                      ("Scattered clouds, breezy", 52, 36),
                      ("Morning fog, afternoon sun", 55, 40)],
    "MIAMI":         [("Sunny and warm, ocean breeze", 76, 62),
                      ("Partly cloudy, brief shower", 74, 64),
                      ("Mostly sunny, pleasant", 77, 60)],
    "DALLAS":        [("Windy, falling temperatures", 52, 32),
                      ("Sunny and cool", 55, 34),
                      ("Overcast, drizzle", 48, 38)],
    "DENVER":        [("Snow, 2-4 inches possible", 30, 12),
                      ("Sunny, fresh powder overnight", 34, 16),
                      ("Blustery, blowing snow", 26, 8)],
    "MINNEAPOLIS":   [("Bitter cold, blowing snow", 8, -8),
                      ("Sunny, frigid", 12, -4),
                      ("Light snow, wind chills -20", 10, -2)],
    "SEATTLE":       [("Steady rain, breezy", 46, 38),
                      ("Drizzle, low clouds", 44, 36),
                      ("Rain ending, partial clearing", 48, 40)],
    "SAN FRANCISCO": [("Morning fog, afternoon sun", 58, 46),
                      ("Light rain", 56, 48),
                      ("Partly cloudy, cool", 60, 44)],
    "LOS ANGELES":   [("Sunny and mild, Santa Ana winds", 70, 50),
                      ("Mostly sunny, marine layer AM", 68, 52),
                      ("Clear and warm for December", 72, 48)],
}

_CITY_ORDER = ("NEW YORK", "CHICAGO", "BOSTON", "WASHINGTON", "ATLANTA",
               "MIAMI", "DALLAS", "DENVER", "MINNEAPOLIS", "SEATTLE",
               "SAN FRANCISCO", "LOS ANGELES")


# ---------------------------------------------------------------------------
# Ski reports: major resorts with plausible early-season numbers.
# Format per variant: (base depth in inches, open lifts, open trails,
# condition note). Counts are generic early-season estimates.
# ---------------------------------------------------------------------------
_SKI_REPORTS: _Dict[str, _List[_Tuple[int, int, int, str]]] = {
    "VAIL, CO":        [(30, 12, 45, "Packed powder; new terrain opening"),
                        (24, 10, 38, "Machine-groomed; excellent cover up top"),
                        (36, 14, 52, "Fresh snowfall overnight")],
    "ASPEN, CO":       [(28, 8, 34, "Good packed powder"),
                        (22, 7, 29, "Groomed; cold temps preserving snow"),
                        (32, 9, 40, "Overnight snow, back bowls filling in")],
    "KILLINGTON, VT":  [(20, 9, 30, "Man-made base; firm early-season"),
                        (24, 11, 36, "New natural snow; woods still thin"),
                        (18, 8, 27, "Cold snap; hardpack mornings")],
    "STOWE, VT":       [(22, 6, 24, "Groomed cruisers in good shape"),
                        (26, 7, 28, "Powder on the upper mountain"),
                        (19, 5, 21, "Firm; more terrain expected by weekend")],
    "MAMMOTH, CA":     [(34, 13, 60, "Deep Sierra base; spring-like afternoons"),
                        (30, 12, 55, "Excellent coverage, all lifts turning"),
                        (38, 15, 68, "Storm totals; powder day conditions")],
    "SQUAW VALLEY, CA": [(28, 8, 42, "Good coverage on the upper mountain"),
                         (24, 7, 36, "Groomed; KT-22 line early"),
                         (33, 9, 48, "Fresh snow; lake views with powder")],
    "PARK CITY, UT":   [(26, 10, 50, "Utah's light powder; great cruising"),
                        (22, 9, 44, "Cold and clear; perfect grooming"),
                        (30, 11, 55, "Overnight flurries freshen trails")],
}


# ---------------------------------------------------------------------------
# Weather wire notes: short national weather-news blurbs, rotated by day.
# ---------------------------------------------------------------------------
_WIRE_NOTES: _List[str] = [
    "A strong Pacific storm is pushing heavy rain into the Northwest, with "
    "mountain snow expected above 4,000 feet through the weekend.",
    "Arctic air spilling out of Canada has the Upper Midwest in a deep freeze "
    "-- wind chills of 20 to 40 below zero across the Dakotas and Minnesota.",
    "A nor'easter is taking shape off the Mid-Atlantic coast. Snow and "
    "sleet are possible for New England by tomorrow night.",
    "Lake-effect snow bands are hammering the lee of Lakes Erie and Ontario; "
    "travel advisories are up for the I-90 corridor.",
    "High pressure over the Southeast is keeping the region dry and mild -- "
    "a welcome stretch for holiday travelers.",
    "The Sierra is cashing in: resorts from Tahoe to Mammoth are reporting "
    "their best early-season base in years.",
    "A fast-moving clipper will drop light snow from the Rockies to the "
    "Great Lakes tonight, then clear out by morning.",
    "Santa Ana winds are gusting through Southern California canyons; fire "
    "weather watches are posted inland.",
]


def city_forecast_lines(day: _Optional[_date] = None) -> _List[str]:
    """Plausible December forecasts for 12 major U.S. cities."""
    day = _wx_day(day)
    stamp = day.strftime("%A, %B %d, %Y").upper()
    lines = [
        "NATIONAL WEATHER WIRE -- U.S. CITY FORECASTS",
        f"Forecast for {stamp}",
        "",
    ]
    for city in _CITY_ORDER:
        variants = _CITY_FORECASTS[city]
        condition, high, low = variants[day.toordinal() % len(variants)]
        lines.append(f"{city:<14} {condition}")
        lines.append(f"{'':<14} High {high} / Low {low}")
    lines.append("")
    lines.append("All temperatures Fahrenheit. These are typical")
    lines.append("December conditions -- illustrative, not archive data.")
    return lines


def ski_report_lines(day: _Optional[_date] = None) -> _List[str]:
    """Early-season ski reports for major U.S. resorts."""
    day = _wx_day(day)
    stamp = day.strftime("%A, %B %d, %Y").upper()
    lines = [
        "SKI COUNTRY -- EARLY-SEASON RESORT REPORTS",
        f"Conditions for {stamp}",
        "",
    ]
    for resort in _SKI_REPORTS:
        variants = _SKI_REPORTS[resort]
        base, lifts, trails, note = variants[day.toordinal() % len(variants)]
        lines.append(resort)
        lines.append(f"  Base depth: {base} in.  Lifts open: {lifts}  Trails: {trails}")
        lines.append(f"  {note}.")
    lines.append("")
    lines.append("Base depths and counts are typical early-season figures;")
    lines.append("call ahead -- mountain weather changes fast.")
    return lines


def wire_note_lines(day: _Optional[_date] = None) -> _List[str]:
    """A few short national weather-news blurbs."""
    day = _wx_day(day)
    lines = [
        "WEATHER WIRE NOTES",
        "",
    ]
    start = day.toordinal() % len(_WIRE_NOTES)
    for offset in range(3):
        lines.append("* " + _WIRE_NOTES[(start + offset) % len(_WIRE_NOTES)])
        lines.append("")
    lines.append("Wire notes are illustrative -- not actual 1988 advisories.")
    return lines


def weather_menu_lines(day: _Optional[_date] = None) -> _List[_Tuple[str, _List[str]]]:
    """All sections as (title, lines) pairs for the menu wire-up."""
    return [
        ("U.S. City Forecasts", city_forecast_lines(day)),
        ("Ski Reports", ski_report_lines(day)),
        ("Weather Wire Notes", wire_note_lines(day)),
        ("1988 Weather Retrospective", retrospective_lines(day)),
    ]


# ===========================================================================
# CONTENT PACK 6: 1988 Weather Retrospective (period feature content)
# ===========================================================================
# A December 1988 look back at Hurricane Gilbert and the summer drought
# and heat wave. Written from a December 1988 perspective ("three months
# ago"); nothing here references anything after 1988.
#
# Fact-marking convention (mirrors cis_sports.py's VERIFIED-flag pattern):
#   VERIFIED = checked against published 1988 records (NHC Gilbert review,
#              NPS/NASA Yellowstone fire figures, NOAA/Illinois State
#              Climatologist drought assessments).
#   (est.)    = rounded or approximate figures, labeled in the output.
# Dramatized color is feature-writing only; all factual claims below are
# either verified or explicitly marked (est.).

_RETRO_EST = " (est.)"


def gilbert_retrospective_lines() -> _List[str]:
    """Hurricane Gilbert retrospective: the season's record storm (VERIFIED).

    Verified facts: formed Sep 8, 1988; Jamaica landfall Sep 12 (~125 mph);
    reached Cat 5 Sep 13; peak 185 mph / 888 mb; Yucatan landfall Sep 14
    as Cat 5 (~160 mph); final landfall near La Pesca, Tamaulipas, Sep 16;
    dissipated Sep 19; 888 mb = lowest Atlantic pressure then on record.
    """
    return [
        "STORM OF THE SEASON: HURRICANE GILBERT",
        "",
        "Three months ago, the Atlantic produced the most intense",
        "hurricane ever recorded: Hurricane Gilbert.",
        "",
        "SEPT  8 -- Tropical depression forms east of the Lesser Antilles.",
        "SEPT 11 -- Gilbert becomes a hurricane, tracking due west.",
        "SEPT 12 -- Landfall in Jamaica, sustained winds near 125 mph.",
        "SEPT 13 -- Central pressure falls to 888 mb -- the lowest ever",
        "             measured in an Atlantic hurricane. Peak sustained",
        "             winds reach 185 mph; Gilbert is a Category 5 storm.",
        "SEPT 14 -- Landfall on the Yucatan Peninsula near Cozumel as a",
        "             Category 5 hurricane, winds near 160 mph.",
        "SEPT 16 -- Final landfall near La Pesca, Tamaulipas, in northeast",
        "             Mexico, as a Category 3 hurricane.",
        "SEPT 19 -- Gilbert dissipates over Texas.",
        "",
        "At 888 millibars, Gilbert stands as the most intense Atlantic",
        f"hurricane on record. It claimed roughly 300 lives{_RETRO_EST},",
        f"and damage estimates run into the billions{_RETRO_EST}.",
    ]


def drought_retrospective_lines() -> _List[str]:
    """Summer 1988 drought, heat wave, and Yellowstone fires (VERIFIED).

    Verified facts: drought rated among the nation's worst of the past
    100 years; record-low river flows stopped lower-Mississippi barge
    traffic in June-July 1988; James Hansen testified to the Senate on
    Jun 23, 1988; Yellowstone fires burned ~800,000 acres (~36% of the
    park); 25,000+ firefighters cycled through; September snow ended them.
    """
    return [
        "THE LONG HOT SUMMER: DROUGHT OF 1988",
        "",
        "The drought of 1988 ranks among the worst in the nation in the",
        "past 100 years.",
        "",
        "Through June and July, record-low river flows stopped barge",
        "traffic on the lower Mississippi; shoals and grounded tows",
        "snarled the waterways that carry the heartland's grain. Towns",
        "across the Midwest rationed water. Crops withered across the",
        "Plains and the Corn Belt, and losses are estimated in the tens",
        f"of billions of dollars{_RETRO_EST}.",
        "",
        "The heat built with it. On June 23, NASA climatologist James",
        'Hansen told a Senate committee that the "greenhouse effect" had',
        "been detected -- and the greenhouse debate hit the front page.",
        "",
        "In Yellowstone, the worst drought in the park's recorded history",
        "left the forests tinder-dry. Lightning set fires that grew into",
        "the largest firefighting effort the nation had yet seen: more",
        "than 25,000 firefighters cycled through the park. By September,",
        "about 800,000 acres -- more than a third of the park -- had",
        "burned. Snow on September 11 finally stopped the flames' advance.",
    ]


def retrospective_lines(day: _Optional[_date] = None) -> _List[str]:
    """Full December 1988 weather retrospective: Gilbert + summer drought."""
    lines = [
        "WEATHER WIRE SPECIAL -- 1988 WEATHER RETROSPECTIVE",
        "A DECEMBER 1988 LOOK BACK AT THE YEAR'S EXTREMES",
        "",
        "Meteorological facts below are verified against 1988 published",
        f"records; rounded figures are marked{_RETRO_EST}.",
        "",
    ]
    lines.extend(gilbert_retrospective_lines())
    lines.append("")
    lines.extend(drought_retrospective_lines())
    lines.append("")
    lines.append("Feature content: verified facts plus marked estimates.")
    return lines


def weather_service(app) -> _List[_Tuple[str, _List[str]]]:
    """Coordinator entry point: return Weather & Ski sections for this session.

    ``app`` is accepted for a uniform service signature; the day is resolved
    session-aware via cis_dynamic.simulation_day().
    """
    return weather_menu_lines()


if __name__ == "__main__":
    for title, lines in weather_menu_lines():
        print("=" * 60)
        print(title)
        print("=" * 60)
        print("\n".join(lines))
