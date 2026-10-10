"""Candidate verification and re-parsing validator."""

from typing import Optional
from backend.app.compiler.engine import CompilerEngine, CompilerAnalysisResult
from backend.app.compiler.diagnostics import Diagnostic
from backend.app.correction.models import CorrectionCandidate, ValidationStatus
from backend.app.correction.editor import SourceEditor


class CandidateValidator:
    """Validates correction candidates by applying edits and re-parsing with CompilerEngine."""

    def __init__(self, compiler_engine: Optional[CompilerEngine] = None) -> None:
        self.compiler_engine: CompilerEngine = compiler_engine or CompilerEngine()

    def validate_candidate(
        self,
        original_source: str,
        original_diagnostics: list[Diagnostic],
        candidate: CorrectionCandidate,
    ) -> CorrectionCandidate:
        """
        Validates a single candidate:
        1. Applies edits to a copy of original source.
        2. Re-parses the candidate code using CompilerEngine.
        3. Compares diagnostics before and after.
        4. Updates candidate.validation_status and candidate.warnings.
        """
        # Step 1: Apply edits
        success, corrected_code, errors = SourceEditor.apply_edits(
            original_source, candidate.edit_operations
        )

        if not success:
            candidate.corrected_source = original_source
            candidate.validation_status = ValidationStatus.REJECTED_INVALID_EDIT
            candidate.warnings.extend(errors)
            candidate.remaining_error_count = len(original_diagnostics)
            return candidate

        candidate.corrected_source = corrected_code

        # Step 2: Re-parse candidate code with compiler engine
        candidate_result: CompilerAnalysisResult = self.compiler_engine.analyze(corrected_code)
        candidate.remaining_error_count = candidate_result.error_count

        original_error_count = sum(1 for d in original_diagnostics if d.severity == "error")

        # Step 3: Compare diagnostic sets
        orig_codes = {d.code for d in original_diagnostics}
        new_codes = {d.code for d in candidate_result.diagnostics}

        # Check if new error codes appeared that weren't in the original code
        introduced_codes = new_codes - orig_codes

        if candidate_result.is_valid:
            # Clean fix - zero remaining errors
            candidate.validation_status = ValidationStatus.SYNTAX_VALIDATED
        elif candidate_result.error_count < original_error_count and not introduced_codes:
            # Partial progress - resolved some errors without creating new ones
            candidate.validation_status = ValidationStatus.SYNTAX_VALIDATED
        elif introduced_codes:
            # Introduced new syntax errors
            candidate.validation_status = ValidationStatus.REJECTED_SYNTAX_INVALID
            candidate.warnings.append(
                f"Candidate introduced new syntax error(s): {', '.join(introduced_codes)}"
            )
        elif candidate_result.error_count >= original_error_count:
            # Did not reduce errors
            candidate.validation_status = ValidationStatus.REJECTED_SYNTAX_INVALID
            candidate.warnings.append("Candidate did not resolve any syntax errors.")
        else:
            candidate.validation_status = ValidationStatus.UNVERIFIED

        return candidate
