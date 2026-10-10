"""Diagnostic reporting structures and codes for compiler analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DiagnosticCategory(str, Enum):
    LEXICAL = "lexical"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"


class DiagnosticCode(str, Enum):
    # Lexical Errors (E100 - E199)
    LEX_UNTERMINATED_STRING = "E101"
    LEX_UNTERMINATED_CHAR = "E102"
    LEX_UNTERMINATED_COMMENT = "E103"
    LEX_INVALID_CHAR = "E104"
    LEX_INVALID_NUMBER = "E105"

    # Syntax Errors (E200 - E299)
    PARSE_EXPECTED_TOKEN = "E201"
    PARSE_UNEXPECTED_TOKEN = "E202"
    PARSE_MISSING_SEMICOLON = "E203"
    PARSE_MISSING_BRACE = "E204"
    PARSE_MISSING_PAREN = "E205"
    PARSE_INVALID_EXPRESSION = "E206"
    PARSE_INVALID_DECLARATION = "E207"
    PARSE_UNCLOSED_BLOCK = "E208"
    PARSE_MISSING_TYPE = "E209"
    PARSE_MISSING_IDENTIFIER = "E210"
    PARSE_INVALID_STATEMENT = "E211"


@dataclass
class Diagnostic:
    code: str
    category: DiagnosticCategory
    severity: DiagnosticSeverity
    message: str
    line: int
    column: int
    start_offset: int
    end_offset: int
    excerpt: Optional[str] = None
    recovery_status: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "excerpt": self.excerpt,
            "recovery_status": self.recovery_status,
        }


def extract_source_excerpt(source: str, line_num: int) -> Optional[str]:
    """Extract a line excerpt from source code by 1-indexed line number."""
    lines = source.splitlines()
    if 1 <= line_num <= len(lines):
        return lines[line_num - 1]
    return None
