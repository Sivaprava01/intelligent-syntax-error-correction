"""Pydantic request and response schemas for AI correction engine."""

from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator
from backend.app.schemas.analysis import DiagnosticItem


class EditOperationSchema(BaseModel):
    operation: str = Field(description="'insert', 'delete', or 'replace'")
    start_offset: int
    end_offset: int
    replacement: str = ""
    expected_text: Optional[str] = None


class CorrectionProposalSchema(BaseModel):
    candidate_id: str
    summary: str
    explanation: str
    edit_operations: list[EditOperationSchema]
    corrected_source: str
    validation_status: str
    related_diagnostics: list[str] = []
    confidence: Optional[float] = None
    ranking_score: Optional[float] = None
    warnings: list[str] = []
    remaining_error_count: Optional[int] = None


class CorrectionRequest(BaseModel):
    source_code: Optional[str] = Field(
        default=None,
        description="The C source code to be corrected",
    )
    code: Optional[str] = Field(
        default=None,
        description="Alternative field name for source code",
    )
    source_version: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_code_field(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "source_code" not in values and "code" in values:
                values["source_code"] = values["code"]
            elif "source_code" in values and values["source_code"] is None and "code" in values:
                values["source_code"] = values["code"]
            elif "source_code" not in values:
                values["source_code"] = ""
        return values


class CorrectionResponse(BaseModel):
    success: bool
    source_version: str
    is_valid: bool
    error_count: int
    diagnostics: list[DiagnosticItem]
    proposals: list[CorrectionProposalSchema]
    ai_available: bool


class ApplyProposalRequest(BaseModel):
    source_code: str
    expected_source_version: str
    proposal: CorrectionProposalSchema


class ApplyProposalResponse(BaseModel):
    success: bool
    updated_source: str
    new_source_version: str
    is_valid: bool
    error_count: int
    diagnostics: list[DiagnosticItem]
    error_message: Optional[str] = None
