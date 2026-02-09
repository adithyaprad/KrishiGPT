from __future__ import annotations

import logging
from typing import Any, Dict

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.location import get_lat_lon
from ..tools.sarvam import use_sarvam_llm
from ..tools.weather import get_weather_forecast

logger = logging.getLogger(__name__)


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

Inputs in session state:
- translated_query: the user's query in English.
- routing_decision: a JSON string with keys intent, location, needs_clarification, clarification_question.

Workflow:
1. Parse routing_decision.
2. If needs_clarification is true, ask the clarification_question and stop.
3. If intent is "weather":
   - If location is empty, ask for the location.
   - Otherwise call execute_getlanlon with the location, then execute_getweatherapi.
   - If either tool returns status "error", apologize and ask for a clearer location.
   - Summarize weather using the tool fields. Include location, date, temperature range,
     conditions, humidity, and wind speed.
4. If intent is "farming" or "general":
   - Call use_sarvam_llm with translated_query.
   - If status is "success", use the response text.
   - If status is "error", apologize briefly and ask a follow-up question for details.

Output:
- Plain English response only (no JSON).
- Keep it concise, practical, and farmer-friendly.
""",
        description=(
            "Handles user queries and provides weather information or farming advice."
        ),
        tools=[getlanlon_tool, getweatherapi_tool, sarvam_llm_tool],
        output_key="english_response",
    )

    return response_agent
