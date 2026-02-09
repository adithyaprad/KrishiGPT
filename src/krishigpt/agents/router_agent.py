from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent


def create_router_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    """
    Classify intent and extract location into a structured JSON decision.
    """
    return LlmAgent(
        name="RoutingAgent",
        model=model,
        instruction="""You are a routing agent for a farmer assistant.
Your job is to read the translated English query and output a strict JSON object
that decides the user's intent and any location information needed for weather.

Input:
- The translated query is available in session state under the key 'translated_query'.

Output (JSON only, no extra text):
{
  "intent": "weather" | "farming" | "general",
  "location": "<string or empty>",
  "needs_clarification": true | false,
  "clarification_question": "<string or empty>"
}

Rules:
- Use intent "weather" if the user asks about weather, temperature, rain, forecast, humidity, wind, or climate.
- Use intent "farming" if the user asks about crops, pests, soil, irrigation, fertilizer, equipment, or farming practices.
- Use intent "general" for greetings or unrelated questions.
- If intent is "weather" and location is missing or ambiguous, set needs_clarification=true and ask a short question like "Which city or village are you asking about?".
- Keep location as a plain place name if present (e.g., "Mumbai, MH, IN").
- If unsure, set intent to "farming" (not "general") and needs_clarification=false.
""",
        description="Routes queries to weather or farming workflows.",
        output_key="routing_decision",
    )
