from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, Optional

import requests

from krishigpt.config import get_openweather_api_key

logger = logging.getLogger(__name__)


def get_lat_lon(
    location: str = "Bangalore,KA,IN",
    api_key: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetch latitude and longitude for a given location using OpenWeatherMap API.
    """
    resolved_api_key = api_key or get_openweather_api_key()
    if not resolved_api_key:
        return {
            "status": "error",
            "message": "OPENWEATHER_API_KEY is not set",
            "latitude": None,
            "longitude": None,
        }

    if not location:
        return {
            "status": "error",
            "message": "Location is required",
            "latitude": None,
            "longitude": None,
        }

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": location,
        "limit": 1,
        "appid": resolved_api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, list):
            location_data = data[0]
            latitude = location_data.get("lat")
            longitude = location_data.get("lon")
            return {
                "status": "success",
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
            }

        logger.warning("No location data found for '%s'", location)
        return {
            "status": "error",
            "message": f"Could not find coordinates for location: {location}",
            "latitude": None,
            "longitude": None,
        }
    except requests.exceptions.RequestException as exc:
        logger.exception("Error fetching location data: %s", exc)
        return {
            "status": "error",
            "message": f"Error retrieving coordinates: {str(exc)}",
            "latitude": None,
            "longitude": None,
        }
    except (json.JSONDecodeError, TypeError) as exc:
        logger.exception("Error parsing location response: %s", exc)
        return {
            "status": "error",
            "message": "Error parsing response from API",
            "latitude": None,
            "longitude": None,
        }


if __name__ == "__main__":
    location_arg = "Bangalore,KA,IN"
    if len(sys.argv) > 1:
        location_arg = sys.argv[1]
    elif not sys.stdin.isatty():
        location_arg = sys.stdin.read().strip()

    result = get_lat_lon(location_arg)
    print(json.dumps(result))
