from __future__ import annotations

import logging
from typing import Any, Dict

from sarvamai import SarvamAI

from ..config import get_sarvam_api_key

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


def translate_text_if_needed(
    text: str,
    source_language_code: str = "en-IN",
    target_language_code: str = "en-IN",
    speaker_gender: str = "Male",
    mode: str = "classic-colloquial",
) -> Dict[str, Any]:
    """
    Translate only when source and target languages differ.
    """
    if not text:
        return {
            "status": "error",
            "error_message": "text is required",
            "translated_text": "",
        }

    if source_language_code == target_language_code:
        return {"status": "success", "translated_text": text, "skipped": True}

    return translate_text(
        text=text,
        source_language_code=source_language_code,
        target_language_code=target_language_code,
        speaker_gender=speaker_gender,
        mode=mode,
    )
