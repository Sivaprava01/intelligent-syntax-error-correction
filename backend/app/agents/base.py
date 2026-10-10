"""Base interface for syntax error correction agents."""

from abc import ABC, abstractmethod
from typing import Optional
from backend.app.compiler.diagnostics import Diagnostic
from backend.app.correction.models import CorrectionCandidate


class BaseCorrectionAgent(ABC):
    """Abstract interface for AI and heuristic correction agents."""

    @abstractmethod
    def propose_corrections(
        self,
        source_code: str,
        diagnostics: list[Diagnostic],
    ) -> list[CorrectionCandidate]:
        """
        Generates candidate corrections given the source code and compiler diagnostics.
        """
        pass
