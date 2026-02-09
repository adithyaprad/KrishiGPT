from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.sarvam import use_sarvam_llm


def create_farming_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    """
    Farming specialist that handles agricultural queries in English.
    """
    sarvam_llm_tool = FunctionTool(func=use_sarvam_llm)

    return LlmAgent(
        name="FarmingAgent",
        model=model,
        description="Provides farming advice, crop guidance, and pest management.",
        instruction="""You are a farming specialist for farmers.

Input in session state:
- translation_result: JSON with detected_language and translated_query.

Steps:
1. Read translated_query from translation_result. If missing, use the user's query.
2. Call use_sarvam_llm with the English query.
   - If status is "success", use the "response" field.
   - If status is "error", apologize briefly and ask a follow-up question in English.

Return only the English response text.
""",
        tools=[sarvam_llm_tool],
        output_key="english_response",
    )
