from __future__ import annotations

import logging
import os
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_ENV_LOADED = False


def _load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    load_dotenv()
    _ENV_LOADED = True


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    _load_env()
    return os.getenv(name, default)


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-exp"
DEFAULT_APP_NAME = "translator_assistant_app"


def get_gemini_model() -> str:
    return get_env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL) or DEFAULT_GEMINI_MODEL


def get_openweather_api_key() -> Optional[str]:
    return get_env("OPENWEATHER_API_KEY")


def get_sarvam_api_key() -> Optional[str]:
    return get_env("SARVAM_API_KEY")
