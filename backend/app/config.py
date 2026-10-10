"""Configuration settings for the syntax error detection and correction backend."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "Intelligent C Syntax Error Detection and Correction Engine"
    VERSION: str = "2.0.0"
    PHASE: str = "Phase 2 - AI-Assisted Correction & Validation Engine"
    API_PREFIX: str = "/api"
    MAX_SOURCE_SIZE_BYTES: int = 100 * 1024  # 100 KB

    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() in ("true", "1", "yes")


settings = Settings()
