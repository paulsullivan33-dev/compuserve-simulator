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
