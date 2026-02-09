from __future__ import annotations

import logging
from typing import Any, Dict

from sarvamai import SarvamAI

from krishigpt.config import get_sarvam_api_key

logger = logging.getLogger(__name__)


def translate_text(
    text: str,
    source_language_code: str = "en-IN",
    target_language_code: str = "en-IN",
    speaker_gender: str = "Male",
    mode: str = "classic-colloquial",
) -> Dict[str, Any]:
    """
    Translates text using SarvamAI API.
    """
    api_key = get_sarvam_api_key()
    if not api_key:
        return {
            "status": "error",
            "error_message": "SARVAM_API_KEY is not set",
            "translated_text": "",
        }

    try:
        client = SarvamAI(api_subscription_key=api_key)
        response = client.text.translate(
            input=text,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            speaker_gender=speaker_gender,
            mode=mode,
        )
        return {"status": "success", "translated_text": response.translated_text}
    except Exception as exc:
        logger.exception("Error translating text: %s", exc)
        return {"status": "error", "error_message": str(exc), "translated_text": ""}
