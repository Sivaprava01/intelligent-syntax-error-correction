"""Pydantic request and response schemas for compiler analysis API."""

from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator


class AnalysisRequest(BaseModel):
    source_code: Optional[str] = Field(
        default=None,
        description="The C source code to be analyzed",
    )
    code: Optional[str] = Field(
        default=None,
        description="Alternative field name for source code",
    )

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


class DiagnosticItem(BaseModel):
    code: str
    category: str
    severity: str
    message: str
    line: int
    column: int
    start_offset: int
    end_offset: int
    excerpt: Optional[str] = None
    recovery_status: Optional[str] = None


class TokenItem(BaseModel):
    type: str
    type_name: str
    value: str
    line: int
    column: int
    start_offset: int
    end_offset: int


class AnalysisResponse(BaseModel):
    success: bool
    is_valid: bool
    error_count: int
    warning_count: int
    diagnostics: list[DiagnosticItem]
    tokens: list[TokenItem]
    ast: Optional[dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    phase: str
