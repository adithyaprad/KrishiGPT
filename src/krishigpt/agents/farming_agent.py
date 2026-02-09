from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

from ..config import get_mospi_mcp_url
from ..tools.sarvam import use_sarvam_llm


def _build_mospi_toolset() -> McpToolset:
    mospi_url = get_mospi_mcp_url()
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=mospi_url),
        tool_name_prefix="mospi",
    )


def create_farming_agent(model: str = "gemini-2.5-flash") -> LlmAgent:
    """
    Farming specialist that handles agricultural queries in English, including
    official government statistics via MCP when available.
    """
    sarvam_llm_tool = FunctionTool(func=use_sarvam_llm)
    mospi_toolset = _build_mospi_toolset()

    return LlmAgent(
        name="FarmingAgent",
        model=model,
        description=(
            "Provides farming advice, crop guidance, and official government "
            "statistics via MoSPI MCP tools."
        ),
        instruction="""You are a farming specialist for farmers.

Input in session state:
- translation_result: JSON with detected_language and translated_query.

Steps:
1. Read translated_query from translation_result. If missing, use the user's query.
2. Decide the data source with a strict rule:
   - ALWAYS use MoSPI MCP tools if the query involves official statistics, indices,
     surveys, time-series values, rates, percentages, prices, growth, or any
     government dataset (examples: CPI, WPI, IIP, PLFS, NAS, ASI, environmental stats).
   - Use MoSPI MCP tools if the user asks for "latest", "trend", "value", "rate",
     "index", "price", "survey", "report", "official data", or any dataset name.
   - Only use Sarvam (use_sarvam_llm) for general advice, recommendations, farming
     practices, pest control, crop guidance, or explanations that do NOT require
     official statistics.
3. If a query could be answered by official data, prefer MoSPI MCP tools even if it
   also asks for advice. After MCP data is retrieved, you may add a short factual
   explanation, but do NOT invent data.
4. If required details for MCP are missing (time period, geography, dataset),
   ask a short clarification question in English and stop.
5. If MCP tools return no data or an error, fall back to use_sarvam_llm.
6. If the query is clearly non-statistical advice, call use_sarvam_llm directly.
   - If status is "success", use the "response" field.
   - If status is "error", apologize briefly and ask a follow-up question in English.

Return only the English response text.
""",
        tools=[mospi_toolset, sarvam_llm_tool],
        output_key="english_response",
    )
