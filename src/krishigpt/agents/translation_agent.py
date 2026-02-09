from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.translation import translate_text_if_needed


def create_input_translation_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Detect language and translate the user query to English.
    """
    translation_tool = FunctionTool(func=translate_text_if_needed)

    return LlmAgent(
        name="InputTranslationAgent",
        model=model,
        description="Detects the user language and translates the query to English.",
        instruction="""You translate user queries to English.

Supported languages:
en-IN, hi-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN.

Steps:
1. Detect the user's language code from the list above.
2. If the detected language is "en-IN", do NOT call any tool. Output the JSON
   with translated_query equal to the original user query.
3. Otherwise call translate_text_if_needed with:
   - text = user's query
   - source_language_code = detected language
   - target_language_code = "en-IN"
4. The tool returns JSON with status and translated_text.
   - If status is "success", use translated_text.
   - If status is "error", use the original query.

Output ONLY this JSON (no extra text):
{
  "detected_language": "<language code>",
  "translated_query": "<english text>"
}
""",
        tools=[translation_tool],
        output_key="translation_result",
    )


def create_output_translation_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Translate the English response back to the user's language.
    """
    translation_tool = FunctionTool(func=translate_text_if_needed)

    return LlmAgent(
        name="OutputTranslationAgent",
        model=model,
        description="Translates the English response back to the user's language.",
        instruction="""You translate the assistant's English response back to the user's language.

Inputs in session state:
- english_response: the response from a specialist agent (English).
- coordinator_message: clarification text from the coordinator (English), if any.
- translation_result: JSON with detected_language from InputTranslationAgent.

Steps:
1. Use english_response if present; otherwise use coordinator_message.
2. If no response text exists, return a short apology in English.
3. Read detected_language from translation_result. If missing, assume "en-IN".
4. If detected_language is "en-IN", return the English text as-is and do NOT call any tool.
5. Otherwise call translate_text_if_needed with:
   - text = English response
   - source_language_code = "en-IN"
   - target_language_code = detected_language
6. If translation fails, return the English text.

Return only the final response text.
""",
        tools=[translation_tool],
        output_key="final_response",
    )
