from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, Optional

import requests

from ..config import get_mandi_api_key

logger = logging.getLogger(__name__)


def get_mandi_prices(
    state: str,
    district: str,
    commodity: str,
    api_key: Optional[str] = None,
    timeout: int = 10,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Fetch mandi prices for a commodity using data.gov.in API.
    """
    resolved_api_key = get_mandi_api_key()
    if api_key and api_key != resolved_api_key:
        logger.warning("Ignoring provided MANDI API key; using .env value.")
    if not resolved_api_key:
        return {
            "status": "error",
            "message": "MANDI_API_KEY is not set",
            "records": None,
        }

    state = (state or "").strip()
    district = (district or "").strip()
    commodity = (commodity or "").strip()

    if not state or not commodity:
        return {
            "status": "error",
            "message": "state and commodity are required",
            "records": None,
        }

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": resolved_api_key,
        "format": "json",
        "filters[state.keyword]": state,
        "filters[commodity]": commodity,
        "limit": str(limit),
    }
    if district:
        params["filters[district]"] = district

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        records = data.get("records", [])
        if not records:
            return {
                "status": "error",
                "message": "No mandi price records found for the given filters",
                "records": [],
            }

        return {
            "status": "success",
            "message": "Successfully retrieved mandi price data",
            "count": data.get("count", len(records)),
            "total": data.get("total"),
            "records": records,
        }
    except requests.exceptions.RequestException as exc:
        logger.exception("Error fetching mandi data: %s", exc)
        return {
            "status": "error",
            "message": f"Error fetching mandi data: {exc}",
            "records": None,
        }
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        logger.exception("Error processing mandi data: %s", exc)
        return {
            "status": "error",
            "message": f"Error processing mandi data: {exc}",
            "records": None,
        }


if __name__ == "__main__":
    state_arg = ""
    district_arg = ""
    commodity_arg = ""
    if len(sys.argv) >= 4:
        state_arg = sys.argv[1]
        district_arg = sys.argv[2]
        commodity_arg = sys.argv[3]
    elif not sys.stdin.isatty():
        try:
            input_data = json.loads(sys.stdin.read().strip())
            state_arg = input_data.get("state", "")
            district_arg = input_data.get("district", "")
            commodity_arg = input_data.get("commodity", "")
        except json.JSONDecodeError as exc:
            print(f"Error parsing input JSON: {exc}", file=sys.stderr)

    result = get_mandi_prices(state_arg, district_arg, commodity_arg)
    print(json.dumps(result))
