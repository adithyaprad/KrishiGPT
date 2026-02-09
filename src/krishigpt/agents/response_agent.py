from __future__ import annotations

import logging
import re
from typing import Any, Dict

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.location import get_lat_lon
from ..tools.sarvam import use_sarvam_llm
from ..tools.weather import get_weather_forecast

logger = logging.getLogger(__name__)


def is_weather_query(query: str) -> Dict[str, Any]:
    """
    Determines if a query is asking about weather.
    """
    query = query.lower()
    weather_keywords = [
        "weather",
        "temperature",
        "forecast",
        "rain",
        "sunny",
        "cloudy",
        "humidity",
        "climate",
        "precipitation",
        "hot",
        "cold",
        "warm",
        "cool",
    ]

    is_weather = any(keyword in query for keyword in weather_keywords)
    location_match = None
    if is_weather:
        patterns = [
            r"(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)",
            r"(?:weather|temperature|forecast|climate)\s+of\s+([A-Za-z\s,]+)",
            r"(?:how's|what's|what is)\s+(?:the|)\s+(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)",
            r"(?:how|what)\s+(?:is|are)\s+(?:the|)\s+(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                location_match = match.group(1).strip()
                break

    return {
        "is_weather_query": is_weather,
        "location": location_match if location_match else "Bangalore,KA,IN",
    }


def execute_getlanlon(location: str) -> Dict[str, Any]:
    """
    Get latitude and longitude for a location using the OpenWeatherMap API.
    """
    return get_lat_lon(location)


def execute_getweatherapi(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get weather data using the OpenWeatherMap API.
    """
    return get_weather_forecast(location_data)


weather_detection_tool = FunctionTool(func=is_weather_query)
getlanlon_tool = FunctionTool(func=execute_getlanlon)
getweatherapi_tool = FunctionTool(func=execute_getweatherapi)
sarvam_llm_tool = FunctionTool(func=use_sarvam_llm)


def create_response_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    """
    Create and return a Response Agent that handles weather queries using the tools
    and non-weather queries using the Sarvam LLM.
    """
    response_agent = LlmAgent(
        name="ResponseAgent",
        model=model,
        instruction="""You are a helpful assistant for farmers that can provide weather information and farming advice.

When you receive a query, follow these steps:

1. First, get the translated query from the session state under the key 'translated_query'.
2. Use the is_weather_query tool to determine if the query is about weather.

If the query IS about weather:
1. Extract the location from the is_weather_query tool's response.
2. Use the execute_getlanlon tool to get the latitude and longitude for the location.
3. Use the execute_getweatherapi tool with the location data to get the weather forecast.
4. Summarize the weather information in a friendly, conversational format.
5. Include all important details like temperature, conditions, humidity, and wind speed.

If the query is NOT about weather:
1. Use the use_sarvam_llm tool with the translated query to get a response from the Sarvam LLM.
2. Check the status of the Sarvam LLM response:
   - If status is "success", use the "response" field from the result
   - If status is "error", provide a fallback response explaining the issue
3. Format the response in a friendly, conversational manner.

Your response will be translated back to the user's original language in the next step.
""",
        description=(
            "Handles user queries and provides weather information or farming advice."
        ),
        tools=[weather_detection_tool, getlanlon_tool, getweatherapi_tool, sarvam_llm_tool],
        output_key="english_response",
    )

    return response_agent
