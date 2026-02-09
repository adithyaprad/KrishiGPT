from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.market import get_mandi_prices


def create_market_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """
    Market specialist that handles mandi price queries in English.
    """
    mandi_tool = FunctionTool(func=get_mandi_prices)

    return LlmAgent(
        name="MarketAgent",
        model=model,
        description="Provides mandi market prices for commodities.",
        instruction="""You are a market price specialist for farmers.

Input in session state:
- translation_result: JSON with detected_language and translated_query.

Steps:
1. Read translated_query from translation_result. If missing, use the user's query.
2. Extract state and commodity from the English query. District is optional.
   - If state or commodity is missing or unclear, ask a short follow-up question in English and stop.
   - Do NOT ask for district if state and commodity are present; proceed without it.
3. Call get_mandi_prices with state, district (if available), commodity.
4. If status is "error", apologize briefly and ask for corrected details.
5. If status is "success", summarize the records concisely:
   - Mention arrival_date (if present), market, variety, grade.
   - Include min_price, max_price, modal_price.
   - If multiple records exist, list each on its own line.
6. If district was not provided, add a short note that results are statewide and
   the user can specify a district for more precise prices.

Return only the English response text.
""",
        tools=[mandi_tool],
        output_key="english_response",
    )
