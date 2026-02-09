from __future__ import annotations

from typing import Dict, Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

from ..config import get_mospi_mcp_auth_token, get_mospi_mcp_url


def _build_mospi_headers() -> Optional[Dict[str, str]]:
    token = get_mospi_mcp_auth_token()
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


def _build_mospi_toolset() -> McpToolset:
    mospi_url = get_mospi_mcp_url()
    headers = _build_mospi_headers()
    connection_kwargs: Dict[str, object] = {"url": mospi_url}
    if headers:
        connection_kwargs["headers"] = headers
    return McpToolset(
        connection_params=SseConnectionParams(**connection_kwargs),
    )


def create_government_data_agent(model: str = "gemini-2.5-flash-lite") -> LlmAgent:
    """
    Government data specialist that uses the MoSPI MCP server for official stats.
    """
    mospi_toolset = _build_mospi_toolset()

    return LlmAgent(
        name="GovernmentDataAgent",
        model=model,
        description="Fetches official MoSPI government statistics via MCP tools.",
        instruction="""You are a government statistics specialist for farmers.

Input in session state:
- translation_result: JSON with detected_language and translated_query.

Steps:
1. Read translated_query from translation_result. If missing, use the user's query.
2. Identify the official dataset or indicator needed (e.g., CPI, WPI, IIP, PLFS, NAS,
   ASI, environmental statistics) and the time period and geography.
3. Use the available MCP tools to fetch the data from MoSPI.
   - If required details are missing or ambiguous, ask a short clarification
     question in English and stop.
   - If a tool returns an error or no data, explain briefly and ask for a refined query.
4. Summarize the results in English, citing the dataset name, time period, geography,
   and any units reported by the tool.

Do not answer from memory; always use MCP tools for data retrieval.
Return only the English response text.
""",
        tools=[mospi_toolset],
        output_key="english_response",
    )
