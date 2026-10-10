"""FastAPI route handlers for compiler analysis and AI correction endpoints."""

from fastapi import APIRouter, HTTPException, status
from backend.app.config import settings
from backend.app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    DiagnosticItem,
    TokenItem,
    HealthResponse,
)
from backend.app.schemas.correction import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionProposalSchema,
    EditOperationSchema,
    ApplyProposalRequest,
    ApplyProposalResponse,
)
from backend.app.compiler.engine import CompilerEngine
from backend.app.correction.service import CorrectionService
from backend.app.correction.models import CorrectionCandidate, EditOperation, EditType, ValidationStatus

router = APIRouter()
compiler_engine = CompilerEngine()
correction_service = CorrectionService(compiler_engine=compiler_engine)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Returns the service health and status."""
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        phase=settings.PHASE,
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_source_code(request: AnalysisRequest) -> AnalysisResponse:
    """Analyzes C source code using deterministic lexical and syntactic parsing."""
    code = request.source_code if request.source_code is not None else ""

    code_bytes = code.encode("utf-8")
    if len(code_bytes) > settings.MAX_SOURCE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Source code exceeds maximum allowed size of {settings.MAX_SOURCE_SIZE_BYTES} bytes ({settings.MAX_SOURCE_SIZE_BYTES // 1024} KB).",
        )

    result = compiler_engine.analyze(code)

    diagnostic_items = [
        DiagnosticItem(
            code=d.code,
            category=d.category.value if hasattr(d.category, "value") else str(d.category),
            severity=d.severity.value if hasattr(d.severity, "value") else str(d.severity),
            message=d.message,
            line=d.line,
            column=d.column,
            start_offset=d.start_offset,
            end_offset=d.end_offset,
            excerpt=d.excerpt,
            recovery_status=d.recovery_status,
        )
        for d in result.diagnostics
    ]

    token_items = [
        TokenItem(
            type=t.type.value,
            type_name=t.type.name,
            value=t.value,
            line=t.line,
            column=t.column,
            start_offset=t.start_offset,
            end_offset=t.end_offset,
        )
        for t in result.tokens
    ]

    ast_dict = result.ast.to_dict() if result.ast else None

    return AnalysisResponse(
        success=True,
        is_valid=result.is_valid,
        error_count=result.error_count,
        warning_count=result.warning_count,
        diagnostics=diagnostic_items,
        tokens=token_items,
        ast=ast_dict,
    )


@router.post("/corrections", response_model=CorrectionResponse)
@router.post("/v1/correct", response_model=CorrectionResponse)
async def request_corrections(request: CorrectionRequest) -> CorrectionResponse:
    """
    Analyzes C source code, generates candidate corrections,
    validates them via deterministic re-parsing, and returns ranked proposals.
    """
    code = request.source_code if request.source_code is not None else ""

    code_bytes = code.encode("utf-8")
    if len(code_bytes) > settings.MAX_SOURCE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Source code exceeds maximum allowed size of {settings.MAX_SOURCE_SIZE_BYTES} bytes ({settings.MAX_SOURCE_SIZE_BYTES // 1024} KB).",
        )

    analysis_res, proposals, source_version, ai_avail = correction_service.request_corrections(code)

    diag_items = [
        DiagnosticItem(
            code=d.code,
            category=d.category.value if hasattr(d.category, "value") else str(d.category),
            severity=d.severity.value if hasattr(d.severity, "value") else str(d.severity),
            message=d.message,
            line=d.line,
            column=d.column,
            start_offset=d.start_offset,
            end_offset=d.end_offset,
            excerpt=d.excerpt,
            recovery_status=d.recovery_status,
        )
        for d in analysis_res.diagnostics
    ]

    proposal_schemas = [
        CorrectionProposalSchema(
            candidate_id=p.candidate_id,
            summary=p.summary,
            explanation=p.explanation,
            edit_operations=[
                EditOperationSchema(
                    operation=op.operation.value if hasattr(op.operation, "value") else str(op.operation),
                    start_offset=op.start_offset,
                    end_offset=op.end_offset,
                    replacement=op.replacement,
                    expected_text=op.expected_text,
                )
                for op in p.edit_operations
            ],
            corrected_source=p.corrected_source,
            validation_status=p.validation_status.value if hasattr(p.validation_status, "value") else str(p.validation_status),
            related_diagnostics=p.related_diagnostics,
            confidence=p.confidence,
            ranking_score=p.ranking_score,
            warnings=p.warnings,
            remaining_error_count=p.remaining_error_count,
        )
        for p in proposals
    ]

    return CorrectionResponse(
        success=True,
        source_version=source_version,
        is_valid=analysis_res.is_valid,
        error_count=analysis_res.error_count,
        diagnostics=diag_items,
        proposals=proposal_schemas,
        ai_available=ai_avail,
    )


@router.post("/corrections/apply", response_model=ApplyProposalResponse)
@router.post("/v1/apply", response_model=ApplyProposalResponse)
async def apply_proposal(request: ApplyProposalRequest) -> ApplyProposalResponse:
    """
    Applies an approved correction proposal to the current working source code.
    Verifies source version integrity to prevent stale edit application.
    """
    p_schema = request.proposal
    edit_ops = [
        EditOperation(
            operation=EditType(op.operation) if op.operation in ("insert", "delete", "replace") else EditType.REPLACE,
            start_offset=op.start_offset,
            end_offset=op.end_offset,
            replacement=op.replacement,
            expected_text=op.expected_text,
        )
        for op in p_schema.edit_operations
    ]

    candidate = CorrectionCandidate(
        candidate_id=p_schema.candidate_id,
        summary=p_schema.summary,
        explanation=p_schema.explanation,
        edit_operations=edit_ops,
        corrected_source=p_schema.corrected_source,
        validation_status=ValidationStatus(p_schema.validation_status) if p_schema.validation_status in ValidationStatus._value2member_map_ else ValidationStatus.PROPOSED,
        related_diagnostics=p_schema.related_diagnostics,
    )

    success, updated_source, new_diagnostics, new_ver, err_msg = correction_service.apply_proposal(
        source_code=request.source_code,
        expected_source_version=request.expected_source_version,
        proposal=candidate,
    )

    if not success:
        return ApplyProposalResponse(
            success=False,
            updated_source=request.source_code,
            new_source_version=request.expected_source_version,
            is_valid=False,
            error_count=len(new_diagnostics),
            diagnostics=[],
            error_message=err_msg,
        )

    diag_items = [
        DiagnosticItem(
            code=d.code,
            category=d.category.value if hasattr(d.category, "value") else str(d.category),
            severity=d.severity.value if hasattr(d.severity, "value") else str(d.severity),
            message=d.message,
            line=d.line,
            column=d.column,
            start_offset=d.start_offset,
            end_offset=d.end_offset,
            excerpt=d.excerpt,
            recovery_status=d.recovery_status,
        )
        for d in new_diagnostics
    ]

    error_count = sum(1 for d in new_diagnostics if d.severity == "error")

    return ApplyProposalResponse(
        success=True,
        updated_source=updated_source,
        new_source_version=new_ver,
        is_valid=error_count == 0,
        error_count=error_count,
        diagnostics=diag_items,
        error_message=None,
    )
