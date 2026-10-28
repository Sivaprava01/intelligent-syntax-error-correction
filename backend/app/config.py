"""Configuration settings for the syntax error detection and correction backend."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Ensure we reliably find and load .env from backend or root with override=True
_backend_dir = Path(__file__).resolve().parent.parent
_backend_env = _backend_dir / ".env"
_root_env = _backend_dir.parent / ".env"

if _backend_env.exists():
    load_dotenv(dotenv_path=_backend_env, override=True)
elif _root_env.exists():
    load_dotenv(dotenv_path=_root_env, override=True)
else:
    load_dotenv(override=True)

# Map deprecated or unavailable models to gemini-3.5-flash
_DEPRECATED_MODELS = {
    "gemini-1.5-flash": "gemini-3.5-flash",
    "gemini-2.5-flash": "gemini-3.5-flash",
    "gemini-1.5-pro": "gemini-3.5-flash",
    "gemini-2.5-flash-lite": "gemini-3.5-flash",
}
_raw_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
_resolved_model = _DEPRECATED_MODELS.get(_raw_model, _raw_model or "gemini-3.5-flash")


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "Intelligent C Syntax Error Detection and Correction Engine"
    VERSION: str = "2.0.0"
    PHASE: str = "Phase 2 - AI-Assisted Correction & Validation Engine"
    API_PREFIX: str = "/api"
    MAX_SOURCE_SIZE_BYTES: int = 100 * 1024  # 100 KB

    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = _resolved_model
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() in ("true", "1", "yes")


settings = Settings()

