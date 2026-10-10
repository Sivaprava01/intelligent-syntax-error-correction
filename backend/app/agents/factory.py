"""Correction Agent Factory."""

from typing import Optional
from backend.app.config import settings
from backend.app.agents.base import BaseCorrectionAgent
from backend.app.agents.mock_agent import MockCorrectionAgent
from backend.app.agents.crew_agent import CrewAICorrectionAgent
from backend.app.agents.gemini_agent import GeminiCorrectionAgent


def get_correction_agent(agent_type: Optional[str] = None) -> BaseCorrectionAgent:
    """
    Returns the configured correction agent.
    If agent_type is explicitly 'mock', returns MockCorrectionAgent.
    If agent_type is 'gemini', returns GeminiCorrectionAgent.
    If agent_type is 'crewai' or None and AI is enabled, returns CrewAICorrectionAgent.
    Defaults to MockCorrectionAgent when AI is disabled or key is missing.
    """
    if agent_type == "mock":
        return MockCorrectionAgent()

    if agent_type == "gemini":
        if settings.AI_ENABLED and settings.GEMINI_API_KEY:
            return GeminiCorrectionAgent()
        return MockCorrectionAgent()

    if settings.AI_ENABLED and settings.GEMINI_API_KEY:
        return CrewAICorrectionAgent()

    return MockCorrectionAgent()
