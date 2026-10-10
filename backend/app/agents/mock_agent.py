"""Deterministic Mock and Heuristic Correction Agent for offline testing and baseline repair."""

import uuid
from typing import Optional
from backend.app.compiler.diagnostics import Diagnostic, DiagnosticCode
from backend.app.correction.models import (
    CorrectionCandidate,
    EditOperation,
    EditType,
    ValidationStatus,
)
from backend.app.agents.base import BaseCorrectionAgent


class MockCorrectionAgent(BaseCorrectionAgent):
    """
    Deterministic rule-based agent for offline testing and baseline syntax repair.
    Produces structured candidates from compiler diagnostics.
    """

    def __init__(self, custom_candidates: Optional[list[CorrectionCandidate]] = None) -> None:
        self.custom_candidates = custom_candidates

    def propose_corrections(
        self,
        source_code: str,
        diagnostics: list[Diagnostic],
    ) -> list[CorrectionCandidate]:
        if self.custom_candidates is not None:
            return self.custom_candidates

        candidates: list[CorrectionCandidate] = []
        source_len = len(source_code)

        for i, diag in enumerate(diagnostics):
            cand_id = f"cand_mock_{i + 1}_{uuid.uuid4().hex[:6]}"

            # Case 1: Missing Semicolon (E203)
            if diag.code == DiagnosticCode.PARSE_MISSING_SEMICOLON.value:
                insert_pos = min(diag.end_offset, source_len)
                # If there's a trailing newline or spaces right before, position properly
                op = EditOperation(
                    operation=EditType.INSERT,
                    start_offset=insert_pos,
                    end_offset=insert_pos,
                    replacement=";",
                    expected_text="",
                )
                candidates.append(
                    CorrectionCandidate(
                        candidate_id=cand_id,
                        summary="Insert missing semicolon ';'",
                        explanation=f"Statement or declaration at line {diag.line} was missing a terminating semicolon.",
                        edit_operations=[op],
                        validation_status=ValidationStatus.PROPOSED,
                        related_diagnostics=[diag.code],
                        confidence=0.98,
                    )
                )

            # Case 2: Missing Closing Brace or Unclosed Block (E204, E208)
            elif diag.code in (
                DiagnosticCode.PARSE_MISSING_BRACE.value,
                DiagnosticCode.PARSE_UNCLOSED_BLOCK.value,
            ):
                insert_pos = source_len
                # Add newline + closing brace at EOF or line end
                op = EditOperation(
                    operation=EditType.INSERT,
                    start_offset=insert_pos,
                    end_offset=insert_pos,
                    replacement="\n}\n",
                    expected_text="",
                )
                candidates.append(
                    CorrectionCandidate(
                        candidate_id=cand_id,
                        summary="Insert missing closing brace '}'",
                        explanation=f"Block opened at line {diag.line} was not closed.",
                        edit_operations=[op],
                        validation_status=ValidationStatus.PROPOSED,
                        related_diagnostics=[diag.code],
                        confidence=0.90,
                    )
                )

            # Case 3: Missing Parenthesis (E205)
            elif diag.code == DiagnosticCode.PARSE_MISSING_PAREN.value:
                insert_pos = min(diag.end_offset, source_len)
                op = EditOperation(
                    operation=EditType.INSERT,
                    start_offset=insert_pos,
                    end_offset=insert_pos,
                    replacement=")",
                    expected_text="",
                )
                candidates.append(
                    CorrectionCandidate(
                        candidate_id=cand_id,
                        summary="Insert missing closing parenthesis ')'",
                        explanation=f"Expression at line {diag.line} was missing a closing parenthesis.",
                        edit_operations=[op],
                        validation_status=ValidationStatus.PROPOSED,
                        related_diagnostics=[diag.code],
                        confidence=0.92,
                    )
                )

            # Case 4: Unterminated String Literal (E101)
            elif diag.code == DiagnosticCode.LEX_UNTERMINATED_STRING.value:
                insert_pos = min(diag.end_offset, source_len)
                op = EditOperation(
                    operation=EditType.INSERT,
                    start_offset=insert_pos,
                    end_offset=insert_pos,
                    replacement='"',
                    expected_text="",
                )
                candidates.append(
                    CorrectionCandidate(
                        candidate_id=cand_id,
                        summary='Insert missing closing quote \'"\'',
                        explanation=f"String literal at line {diag.line} was not closed before newline or EOF.",
                        edit_operations=[op],
                        validation_status=ValidationStatus.PROPOSED,
                        related_diagnostics=[diag.code],
                        confidence=0.95,
                    )
                )

        return candidates
