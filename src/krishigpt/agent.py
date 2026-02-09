from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from .agents.response_agent import create_response_agent
from .config import DEFAULT_APP_NAME, configure_google_api, get_gemini_model
from .tools.translation import translate_text

logger = logging.getLogger(__name__)

APP_NAME = DEFAULT_APP_NAME
DEFAULT_USER_ID = "user_01"
DEFAULT_SESSION_ID = "translation_session_01"

LANGUAGE_NAMES = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "od-IN": "Odia",
    "pa-IN": "Punjabi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
}

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
    Build the multilingual farmer assistant pipeline.
    """
    configure_google_api()
    gemini_model = model or get_gemini_model()
    translation_tool = FunctionTool(func=translate_text)

    language_detection_agent = LlmAgent(
        name="LanguageDetectionAgent",
        model=gemini_model,
        instruction="""You are a Language Detection Agent.
Your task is to identify which language the user's query is written in.

Only consider the following language options:
en-IN: English
hi-IN: Hindi
bn-IN: Bengali
gu-IN: Gujarati
kn-IN: Kannada
ml-IN: Malayalam
mr-IN: Marathi
od-IN: Odia
pa-IN: Punjabi
ta-IN: Tamil
te-IN: Telugu

Return ONLY the language code (e.g., "hi-IN", "en-IN", etc.) without any additional text or explanation.
If you're unsure, default to "en-IN".
""",
        description="Detects the language of the user's query.",
        output_key="detected_language",
    )

    translation_agent = LlmAgent(
        name="TranslationAgent",
        model=gemini_model,
        instruction="""You are a Translation Agent.
Your task is to translate the user's query to English using the translation tool.
Use the language code provided in the session state under the key 'detected_language' as the source_language_code parameter when calling the translation tool.
Access the detected language code from the session state and pass it explicitly to the translation tool.

For example, if the detected language is "hi-IN", you should call the translation tool with:
translate_text(
    text=user_query,
    source_language_code="hi-IN",
    speaker_gender="Male",
    mode="classic-colloquial"
)

If the query is already in English (detected_language is 'en-IN'), still use the translation tool for consistency.
Output only the translated text without additional explanations.
""",
        description="Translates user queries to English using the translation tool.",
        tools=[translation_tool],
        output_key="translated_query",
    )

    response_agent = create_response_agent(model=gemini_model)

    final_response_agent = LlmAgent(
        name="FinalResponseAgent",
        model=gemini_model,
        instruction="""You are a Translation Agent for responses.
Your task is to translate the English response back to the user's original language.

1. Get the English response from the session state under the key 'english_response'.
2. Get the user's original language code from the session state under the key 'detected_language'.
3. Use the translation tool to translate the response to the user's original language.

For example, if the detected language is "hi-IN", you should call the translation tool with:
translate_text(
    text=english_response,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    speaker_gender="Male",
    mode="classic-colloquial"
)

If the original language was English (detected_language is 'en-IN'), just return the English response as is.
Output only the translated response without additional explanations.
""",
        description="Translates the English response back to the user's original language.",
        tools=[translation_tool],
        output_key="final_response",
    )

    return SequentialAgent(
        name="MultilingualFarmerAssistantPipeline",
        sub_agents=[
            language_detection_agent,
            translation_agent,
            response_agent,
            final_response_agent,
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
    formatted_response = []

    language_code = responses.get("detected_language")
    if language_code:
        language_name = LANGUAGE_NAMES.get(language_code, language_code)
        formatted_response.append(
            f"Detected Language: {language_name} ({language_code})"
        )

    english_response = responses.get("english_response")
    if english_response:
        formatted_response.append(f"\nEnglish Response:\n{english_response}")

    final_response = responses.get("final_response")
    if final_response and language_code and language_code != "en-IN":
        language_name = LANGUAGE_NAMES.get(language_code, language_code)
        formatted_response.append(
            f"\n{language_name} Response:\n{final_response}"
        )

    return "\n".join(formatted_response)


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
