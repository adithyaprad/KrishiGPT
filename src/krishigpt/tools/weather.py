from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, Optional

import requests

from ..config import get_openweather_api_key

logger = logging.getLogger(__name__)


def get_weather_forecast(
    location_data: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetch weather forecast data for a location using data from get_lat_lon.
    """
    resolved_api_key = get_openweather_api_key()
    if api_key and api_key != resolved_api_key:
        logger.warning("Ignoring provided OpenWeather API key; using .env value.")
    if not resolved_api_key:
        return {
            "status": "error",
            "message": "OPENWEATHER_API_KEY is not set",
            "weather_data": None,
        }

    if not location_data or not isinstance(location_data, dict):
        return {
            "status": "error",
            "message": "Invalid or missing location data",
            "weather_data": None,
        }

    lat = location_data.get("latitude")
    lon = location_data.get("longitude")
    location = location_data.get("location", "Unknown location")

    if lat is None or lon is None:
        return {
            "status": "error",
            "message": f"Missing coordinates for location: {location}",
            "weather_data": None,
        }

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": resolved_api_key}

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        weather_list = data.get("list", [])
        if not weather_list:
            return {
                "status": "error",
                "message": "No weather data found",
                "weather_data": None,
            }

        first_date = weather_list[0]["dt_txt"].split(" ")[0]
        first_day_data = [
            entry for entry in weather_list if entry["dt_txt"].startswith(first_date)
        ]

        temps = [entry["main"]["temp"] - 273.15 for entry in first_day_data]
        min_temp = round(min(temps), 1)
        max_temp = round(max(temps), 1)
        avg_temp = round(sum(temps) / len(temps), 1)

        weather_conditions = []
        for entry in first_day_data:
            for condition in entry["weather"]:
                if condition["main"] not in weather_conditions:
                    weather_conditions.append(condition["main"])

        humidity_avg = sum(entry["main"]["humidity"] for entry in first_day_data) / len(
            first_day_data
        )
        wind_speeds = [
            entry.get("wind", {}).get("speed", 0) for entry in first_day_data
        ]
        wind_speed_avg = (
            sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0
        )

        city_name = data.get("city", {}).get("name", location)

        text_summary = (
            f"Weather forecast for {city_name} on {first_date}:\n"
            f"Temperature: {min_temp}°C to {max_temp}°C (avg: {avg_temp}°C)\n"
            f"Conditions: {', '.join(weather_conditions)}\n"
            f"Humidity: {round(humidity_avg, 1)}%\n"
            f"Wind Speed: {round(wind_speed_avg, 1)} m/s\n"
        )

        return {
            "status": "success",
            "message": "Successfully retrieved weather data",
            "location": city_name,
            "date": first_date,
            "temperature": {
                "min": min_temp,
                "max": max_temp,
                "average": avg_temp,
                "unit": "°C",
            },
            "weather_conditions": weather_conditions,
            "humidity": round(humidity_avg, 1),
            "wind_speed": round(wind_speed_avg, 1),
            "text_summary": text_summary,
        }
    except requests.exceptions.RequestException as exc:
        logger.exception("Error fetching weather data: %s", exc)
        return {
            "status": "error",
            "message": f"Error fetching weather data: {exc}",
            "weather_data": None,
        }
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        logger.exception("Error processing weather data: %s", exc)
        return {
            "status": "error",
            "message": f"Error processing weather data: {exc}",
            "weather_data": None,
        }


if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = sys.stdin.read().strip()
            location_data = json.loads(input_data)
        else:
            location_data = {
                "status": "success",
                "location": "Bangalore,KA,IN",
                "latitude": 12.9716,
                "longitude": 77.5946,
            }

        weather_data = get_weather_forecast(location_data)
        print(json.dumps(weather_data))
    except json.JSONDecodeError as exc:
        print(f"Error parsing input JSON: {exc}", file=sys.stderr)
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Error parsing input JSON: {exc}",
                    "weather_data": None,
                }
            )
        )
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Unexpected error: {exc}",
                    "weather_data": None,
                }
            )
        )
