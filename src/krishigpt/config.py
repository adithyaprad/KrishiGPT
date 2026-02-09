from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

_ENV_LOADED = False
_ENV_VALUES: Dict[str, str] = {}


def _load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = _resolve_env_path()
    if env_path:
        _ENV_VALUES.update({k: v for k, v in dotenv_values(env_path).items() if v})
    _ENV_LOADED = True


def _resolve_env_path() -> Optional[Path]:
    project_root = Path(__file__).resolve().parents[2]
    project_env = project_root / ".env"
    if project_env.exists():
        return project_env
    logger.warning("No .env file found at %s; API keys will be missing.", project_env)
    return None


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    _load_env()
    return _ENV_VALUES.get(name, default)


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_APP_NAME = "translator_assistant_app"
DEFAULT_MOSPI_MCP_URL = "https://mcp.mospi.gov.in"


def get_gemini_model() -> str:
    return get_env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL) or DEFAULT_GEMINI_MODEL


def get_openweather_api_key() -> Optional[str]:
    return get_env("OPENWEATHER_API_KEY")


def get_sarvam_api_key() -> Optional[str]:
    return get_env("SARVAM_API_KEY")


def get_google_api_key() -> Optional[str]:
    return get_env("GOOGLE_API_KEY")


def get_mospi_mcp_url() -> str:
    return get_env("MOSPI_MCP_URL", DEFAULT_MOSPI_MCP_URL) or DEFAULT_MOSPI_MCP_URL


def configure_google_api() -> None:
    """
    Configure Gemini credentials from the project .env only.
    """
    api_key = get_google_api_key()
    if not api_key:
        os.environ.pop("GOOGLE_API_KEY", None)
        os.environ.pop("GEMINI_API_KEY", None)
        logger.warning("GOOGLE_API_KEY is not set; Gemini calls may fail.")
        return

    # Ensure any SDKs that rely on process env only see the .env value.
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GEMINI_API_KEY"] = api_key

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
    except Exception as exc:
        logger.debug("Unable to configure google.generativeai: %s", exc)
