from __future__ import annotations

import logging
from typing import Any, Dict

from openai import OpenAI

from krishigpt.config import get_sarvam_api_key

logger = logging.getLogger(__name__)


def use_sarvam_llm(query: str) -> Dict[str, Any]:
    """
    Process a non-weather query using the Sarvam LLM API.
    """
    api_key = get_sarvam_api_key()
    if not api_key:
        return {
            "status": "error",
            "message": "SARVAM_API_KEY is not set",
            "response": (
                "I'm sorry, I couldn't process your farming query at the moment. "
                "Please try again later or ask a different question about farming."
            ),
        }

    try:
        client = OpenAI(base_url="https://api.sarvam.ai/v1", api_key=api_key)

        system_message = """
You are a knowledgeable farming assistant that helps farmers with their questions.
Provide accurate, practical, and helpful information about:
- Crop cultivation techniques and best practices
- Pest and disease management
- Soil health and fertilization
- Water management and irrigation
- Sustainable farming practices
- Agricultural tools and equipment
- Seasonal farming advice
- Market trends and crop selection

Keep your responses concise, practical, and tailored to the farmer's specific question.
""".strip()

        response = client.chat.completions.create(
            model="sarvam-m",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        response_content = response.choices[0].message.content
        logger.debug("Sarvam LLM response preview: %s", response_content[:100])

        return {"status": "success", "response": response_content}
    except Exception as exc:
        error_message = str(exc)
        logger.exception("Error using Sarvam LLM: %s", error_message)
        return {
            "status": "error",
            "message": f"Error using Sarvam LLM: {error_message}",
            "response": (
                "I'm sorry, I couldn't process your farming query at the moment. "
                "Please try again later or ask a different question about farming."
            ),
        }
