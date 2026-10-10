"""Correction service coordinating analysis, agent proposal, validation, ranking, and application."""

import hashlib
from typing import Optional
from backend.app.compiler.engine import CompilerEngine, CompilerAnalysisResult
from backend.app.correction.models import CorrectionCandidate, ValidationStatus
from backend.app.correction.validator import CandidateValidator
from backend.app.correction.ranking import CandidateRanker
from backend.app.correction.editor import SourceEditor
from backend.app.agents.base import BaseCorrectionAgent
from backend.app.agents.factory import get_correction_agent
from backend.app.config import settings


class CorrectionService:
    """End-to-end service for syntax error detection, candidate generation, and validation."""

    def __init__(
        self,
        compiler_engine: Optional[CompilerEngine] = None,
        agent: Optional[BaseCorrectionAgent] = None,
        validator: Optional[CandidateValidator] = None,
    ) -> None:
        self.compiler_engine: CompilerEngine = compiler_engine or CompilerEngine()
        self.agent: BaseCorrectionAgent = agent or get_correction_agent()
        self.validator: CandidateValidator = validator or CandidateValidator(self.compiler_engine)

    @staticmethod
    def compute_source_version(source_code: str) -> str:
        return hashlib.sha256(source_code.encode("utf-8")).hexdigest()[:12]

    def request_corrections(
        self,
        source_code: str,
    ) -> tuple[CompilerAnalysisResult, list[CorrectionCandidate], str, bool]:
        """
        Executes the full correction workflow:
        1. Analyzes source with deterministic compiler.
        2. Proposes candidates via agent.
        3. Validates every candidate using compiler re-parsing.
        4. Ranks candidates deterministically.
        Returns: (analysis_result, ranked_proposals, source_version, ai_available)
        """
        source_version = self.compute_source_version(source_code)
        analysis_result = self.compiler_engine.analyze(source_code)

        if analysis_result.is_valid:
            return analysis_result, [], source_version, True

        # Request candidate proposals from agent
        raw_candidates = self.agent.propose_corrections(
            source_code,
            analysis_result.diagnostics,
        )

        ai_available = bool(settings.AI_ENABLED and settings.GEMINI_API_KEY) or isinstance(
            self.agent, BaseCorrectionAgent
        )

        # Validate candidates
        validated_candidates: list[CorrectionCandidate] = []
        for cand in raw_candidates:
            validated = self.validator.validate_candidate(
                original_source=source_code,
                original_diagnostics=analysis_result.diagnostics,
                candidate=cand,
            )
            validated_candidates.append(validated)

        # Rank candidates
        ranked_proposals = CandidateRanker.rank_candidates(
            candidates=validated_candidates,
            original_error_count=analysis_result.error_count,
        )

        return analysis_result, ranked_proposals, source_version, ai_available

    def apply_proposal(
        self,
        source_code: str,
        expected_source_version: str,
        proposal: CorrectionCandidate,
    ) -> tuple[bool, str, list, str, Optional[str]]:
        """
        Applies an approved proposal to the current working source code.
        Returns: (success, updated_source, new_diagnostics, new_source_version, error_message)
        """
        current_version = self.compute_source_version(source_code)

        # Stale proposal check
        if current_version != expected_source_version:
            return (
                False,
                source_code,
                [],
                current_version,
                f"Stale proposal: source version mismatch (expected {expected_source_version}, got {current_version}). Please re-analyze the source.",
            )

        # Apply edit operations
        success, updated_source, errors = SourceEditor.apply_edits(
            source_code, proposal.edit_operations
        )

        if not success:
            return (
                False,
                source_code,
                [],
                current_version,
                f"Failed to apply proposal edits: {'; '.join(errors)}",
            )

        # Re-parse updated source code
        reparse_result = self.compiler_engine.analyze(updated_source)
        new_version = self.compute_source_version(updated_source)

        return (
            True,
            updated_source,
            reparse_result.diagnostics,
            new_version,
            None,
        )
