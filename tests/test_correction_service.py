"""Unit tests for CorrectionService, Validator, and CandidateRanker."""

import pytest
from backend.app.compiler.engine import CompilerEngine
from backend.app.correction.models import (
    CorrectionCandidate,
    EditOperation,
    EditType,
    ValidationStatus,
)
from backend.app.correction.validator import CandidateValidator
from backend.app.correction.ranking import CandidateRanker
from backend.app.correction.service import CorrectionService
from backend.app.agents.mock_agent import MockCorrectionAgent


def test_candidate_validator_success():
    engine = CompilerEngine()
    validator = CandidateValidator(compiler_engine=engine)

    source = "int main() {\n    int a = 10\n    return a;\n}"
    analysis = engine.analyze(source)
    assert analysis.is_valid is False

    # Target semicolon insert right after '10'
    insert_pos = source.index("10") + 2
    op = EditOperation(
        operation=EditType.INSERT,
        start_offset=insert_pos,
        end_offset=insert_pos,
        replacement=";",
    )
    cand = CorrectionCandidate(
        candidate_id="c1",
        summary="Insert semicolon",
        explanation="Fix missing semicolon",
        edit_operations=[op],
    )

    validated = validator.validate_candidate(source, analysis.diagnostics, cand)
    assert validated.validation_status == ValidationStatus.SYNTAX_VALIDATED
    assert validated.remaining_error_count == 0


def test_candidate_validator_invalid_edit_offsets():
    engine = CompilerEngine()
    validator = CandidateValidator(compiler_engine=engine)

    source = "int main() {\n    return 0;\n}"
    analysis = engine.analyze(source)

    op = EditOperation(
        operation=EditType.REPLACE,
        start_offset=1000,
        end_offset=1005,
        replacement="float",
    )
    cand = CorrectionCandidate(
        candidate_id="c2",
        summary="Invalid edit",
        explanation="Invalid offsets",
        edit_operations=[op],
    )

    validated = validator.validate_candidate(source, analysis.diagnostics, cand)
    assert validated.validation_status == ValidationStatus.REJECTED_INVALID_EDIT
    assert len(validated.warnings) >= 1


def test_candidate_validator_introduces_new_errors():
    engine = CompilerEngine()
    validator = CandidateValidator(compiler_engine=engine)

    source = "int main() {\n    int a = 10\n    return a;\n}"
    analysis = engine.analyze(source)

    # Instead of fixing, it introduces an invalid character and junk
    op = EditOperation(
        operation=EditType.INSERT,
        start_offset=26,
        end_offset=26,
        replacement=" @@@ $$",
    )
    cand = CorrectionCandidate(
        candidate_id="c3",
        summary="Bad fix",
        explanation="Introduces errors",
        edit_operations=[op],
    )

    validated = validator.validate_candidate(source, analysis.diagnostics, cand)
    assert validated.validation_status == ValidationStatus.REJECTED_SYNTAX_INVALID


def test_candidate_ranker_ordering():
    cand_valid = CorrectionCandidate(
        candidate_id="c_val",
        summary="Valid clean fix",
        explanation="",
        edit_operations=[EditOperation(EditType.INSERT, 10, 10, ";")],
        validation_status=ValidationStatus.SYNTAX_VALIDATED,
        remaining_error_count=0,
    )
    cand_rejected = CorrectionCandidate(
        candidate_id="c_rej",
        summary="Rejected fix",
        explanation="",
        edit_operations=[EditOperation(EditType.REPLACE, 0, 5, "invalid syntax")],
        validation_status=ValidationStatus.REJECTED_SYNTAX_INVALID,
        remaining_error_count=2,
    )

    ranked = CandidateRanker.rank_candidates([cand_rejected, cand_valid], original_error_count=1)
    assert ranked[0].candidate_id == "c_val"
    assert ranked[1].candidate_id == "c_rej"
    assert ranked[0].ranking_score > ranked[1].ranking_score


def test_correction_service_end_to_end():
    engine = CompilerEngine()
    agent = MockCorrectionAgent()
    service = CorrectionService(compiler_engine=engine, agent=agent)

    source = "int main() {\n    int a = 10\n    return a;\n}"
    analysis, proposals, version, ai_avail = service.request_corrections(source)

    assert analysis.is_valid is False
    assert len(proposals) >= 1
    best_proposal = proposals[0]
    assert best_proposal.validation_status == ValidationStatus.SYNTAX_VALIDATED

    # Now apply the proposal
    success, new_source, new_diags, new_version, err_msg = service.apply_proposal(
        source_code=source,
        expected_source_version=version,
        proposal=best_proposal,
    )
    assert success is True
    assert err_msg is None
    assert new_version != version
    assert "int a = 10;" in new_source
    assert len(new_diags) == 0


def test_correction_service_stale_proposal_rejected():
    service = CorrectionService()
    source = "int a = 10;"
    proposal = CorrectionCandidate(
        candidate_id="p1",
        summary="fix",
        explanation="",
        edit_operations=[EditOperation(EditType.INSERT, 5, 5, "x")],
    )

    # Supply an incorrect expected version
    success, updated, diags, ver, err = service.apply_proposal(
        source_code=source,
        expected_source_version="stale_version_hash_123",
        proposal=proposal,
    )
    assert success is False
    assert "Stale proposal" in err
    assert updated == source
