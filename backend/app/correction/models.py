"""Data models for correction candidates and edit operations."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EditType(str, Enum):
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


class ValidationStatus(str, Enum):
    PROPOSED = "proposed"
    SYNTAX_VALIDATED = "syntax_validated"
    REJECTED_INVALID_EDIT = "rejected_invalid_edit"
    REJECTED_SYNTAX_INVALID = "rejected_syntax_invalid"
    UNVERIFIED = "unverified"
    AI_UNAVAILABLE = "ai_unavailable"


@dataclass
class EditOperation:
    operation: EditType
    start_offset: int
    end_offset: int
    replacement: str = ""
    expected_text: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation.value if hasattr(self.operation, "value") else str(self.operation),
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "replacement": self.replacement,
            "expected_text": self.expected_text,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EditOperation":
        op_str = data.get("operation", "insert").lower()
        if op_str == "insert":
            op = EditType.INSERT
        elif op_str == "delete":
            op = EditType.DELETE
        elif op_str == "replace":
            op = EditType.REPLACE
        else:
            op = EditType.REPLACE

        return cls(
            operation=op,
            start_offset=int(data.get("start_offset", 0)),
            end_offset=int(data.get("end_offset", 0)),
            replacement=str(data.get("replacement", "")),
            expected_text=data.get("expected_text"),
        )


@dataclass
class CorrectionCandidate:
    candidate_id: str
    summary: str
    explanation: str
    edit_operations: list[EditOperation] = field(default_factory=list)
    corrected_source: str = ""
    validation_status: ValidationStatus = ValidationStatus.PROPOSED
    related_diagnostics: list[str] = field(default_factory=list)
    confidence: Optional[float] = None
    ranking_score: Optional[float] = None
    warnings: list[str] = field(default_factory=list)
    remaining_error_count: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "summary": self.summary,
            "explanation": self.explanation,
            "edit_operations": [op.to_dict() for op in self.edit_operations],
            "corrected_source": self.corrected_source,
            "validation_status": self.validation_status.value if hasattr(self.validation_status, "value") else str(self.validation_status),
            "related_diagnostics": self.related_diagnostics,
            "confidence": self.confidence,
            "ranking_score": self.ranking_score,
            "warnings": self.warnings,
            "remaining_error_count": self.remaining_error_count,
        }
