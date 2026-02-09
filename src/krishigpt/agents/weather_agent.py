from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.location import get_lat_lon
from ..tools.weather import get_weather_forecast


def create_weather_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    """
    Weather specialist that handles weather queries in English.
    """
    get_lat_lon_tool = FunctionTool(func=get_lat_lon)
    get_weather_tool = FunctionTool(func=get_weather_forecast)

    return LlmAgent(
        name="WeatherAgent",
        model=model,
        description="Handles weather queries and forecasts for farmers.",
        instruction="""You are a weather specialist for farmers.

Input in session state:
- translation_result: JSON with detected_language and translated_query.

Steps:
1. Read translated_query from translation_result. If missing, use the user's query.
2. Extract the location from the English query.
   - If the location is missing or unclear, ask a short follow-up question in English and stop.
3. Call get_lat_lon with the extracted location. If status is "error", ask for a
   clearer location in English and stop.
4. Call get_weather_forecast with the location data. If status is "error", ask for
   a clearer location in English and stop.
5. Write a concise weather summary in English using:
   location, date, temperature min/max/avg, conditions, humidity, wind_speed.

Return only the English response text.
""",
        tools=[get_lat_lon_tool, get_weather_tool],
        output_key="english_response",
    )
