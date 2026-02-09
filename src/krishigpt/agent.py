from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents.farming_agent import create_farming_agent
from .agents.government_agent import create_government_data_agent
from .agents.translation_agent import (
    create_input_translation_agent,
    create_output_translation_agent,
)
from .agents.weather_agent import create_weather_agent
from .config import DEFAULT_APP_NAME, configure_google_api, get_gemini_model

logger = logging.getLogger(__name__)

APP_NAME = DEFAULT_APP_NAME
DEFAULT_USER_ID = "user_01"
DEFAULT_SESSION_ID = "translation_session_01"

_runner: Optional[Runner] = None
_session_service: Optional[InMemorySessionService] = None
_root_agent: Optional[SequentialAgent] = None


def _extract_event_text(event: Any) -> Optional[str]:
    try:
        if hasattr(event, "content") and hasattr(event.content, "parts"):
            parts = event.content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text
        if hasattr(event, "content") and isinstance(event.content, str):
            return event.content
    except Exception:
        return None
    return None


def build_pipeline(model: Optional[str] = None) -> SequentialAgent:
    """
    Build the multilingual farmer assistant pipeline using on-demand subagents.
    """
    configure_google_api()
    gemini_model = model or get_gemini_model()
    input_translation_agent = create_input_translation_agent(model=gemini_model)
    weather_agent = create_weather_agent(model=gemini_model)
    farming_agent = create_farming_agent(model=gemini_model)
    government_agent = create_government_data_agent(model=gemini_model)
    output_translation_agent = create_output_translation_agent(model=gemini_model)

    coordinator_agent = LlmAgent(
        name="FarmerAssistantCoordinator",
        model=gemini_model,
        description="Routes farmer queries to specialist agents on demand.",
        instruction="""You are the coordinator for a farmer assistant.

Use the English query from translation_result.translated_query in session state.
If translation_result is missing, use the user's original query.

Decide which specialist should handle the user query:
- WeatherAgent: weather, temperature, rain, forecast, humidity, wind, climate.
- FarmingAgent: crops, pests, soil, irrigation, fertilizer, equipment, practices.
- GovernmentDataAgent: government statistics, official surveys, CPI/WPI/IIP,
  PLFS, NAS, ASI, environmental statistics, or MoSPI datasets.

If the query is weather-related, call:
transfer_to_agent(agent_name="WeatherAgent")

If the query is farming-related, call:
transfer_to_agent(agent_name="FarmingAgent")

If the query is government-data related, call:
transfer_to_agent(agent_name="GovernmentDataAgent")

If the intent is unclear, ask a short clarification question in English and do not call any tools.

Do not answer weather or farming queries directly; always delegate to a specialist.
""",
        sub_agents=[weather_agent, farming_agent, government_agent],
        output_key="coordinator_message",
    )

    return SequentialAgent(
        name="FarmerAssistantPipeline",
        sub_agents=[
            input_translation_agent,
            coordinator_agent,
            output_translation_agent,
        ],
    )


def _get_runner(model: Optional[str] = None) -> Tuple[Runner, InMemorySessionService]:
    global _runner, _session_service, _root_agent
    if _runner is None or _session_service is None or _root_agent is None:
        _root_agent = build_pipeline(model)
        _session_service = InMemorySessionService()
        _runner = Runner(
            agent=_root_agent,
            app_name=APP_NAME,
            session_service=_session_service,
        )
    return _runner, _session_service


def _ensure_session(
    session_service: InMemorySessionService, user_id: str, session_id: str
) -> None:
    try:
        session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
    except Exception as exc:
        logger.debug("Session may already exist: %s", exc)


def call_agent(
    query: str,
    user_id: str = DEFAULT_USER_ID,
    session_id: str = DEFAULT_SESSION_ID,
    debug: bool = False,
) -> str:
    """
    Process a user query through the agent pipeline.
    """
    runner, session_service = _get_runner()
    _ensure_session(session_service, user_id, session_id)

    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(user_id=user_id, session_id=session_id, new_message=content)

    responses: Dict[str, str] = {}
    for event in events:
        if getattr(event, "output_key", None):
            output_value = _extract_event_text(event)
            if output_value is not None:
                responses[event.output_key] = output_value
                if debug:
                    logger.info(
                        "Agent '%s' output (%s): %s",
                        event.agent_name,
                        event.output_key,
                        output_value,
                    )

        if hasattr(event, "is_final_response") and event.is_final_response():
            final_text = _extract_event_text(event)
            if debug and final_text:
                logger.info("Final response: %s", final_text)

    return _format_response(responses)


def _format_response(responses: Dict[str, str]) -> str:
    final_response = responses.get("final_response")
    if final_response:
        return final_response

    english_response = responses.get("english_response")
    if english_response:
        return english_response

    coordinator_message = responses.get("coordinator_message")
    if coordinator_message:
        return coordinator_message

    translated_query = responses.get("translated_query")
    if translated_query:
        return translated_query

    return "I'm sorry, I couldn't process that request. Please try again."


def test_pipeline() -> None:
    """
    Test the agent pipeline with a sample query.
    """
    test_query = "What's the weather like in Mumbai today?"
    response = call_agent(test_query, debug=True)
    print("\nFinal formatted response:")
    print(response)


root_agent = build_pipeline()

if __name__ == "__main__":
    test_pipeline()
