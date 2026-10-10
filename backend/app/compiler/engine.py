"""Compiler engine facade combining lexer and parser for deterministic analysis."""

from dataclasses import dataclass
from typing import Any, Optional
from backend.app.compiler.lexer import Lexer
from backend.app.compiler.parser import Parser
from backend.app.compiler.tokens import Token
from backend.app.compiler.ast_nodes import Program
from backend.app.compiler.diagnostics import Diagnostic, DiagnosticSeverity


@dataclass
class CompilerAnalysisResult:
    is_valid: bool
    diagnostics: list[Diagnostic]
    tokens: list[Token]
    ast: Optional[Program]
    error_count: int
    warning_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "tokens": [t.to_dict() for t in self.tokens],
            "ast": self.ast.to_dict() if self.ast else None,
        }


class CompilerEngine:
    """Deterministic C compiler engine for syntax analysis and diagnostic generation."""

    def __init__(self) -> None:
        pass

    def analyze(self, source_code: str) -> CompilerAnalysisResult:
        # Step 1: Lexical analysis
        lexer = Lexer(source_code)
        tokens, lex_diagnostics = lexer.tokenize()

        # Step 2: Syntax analysis
        parser = Parser(tokens, source=source_code)
        ast, parse_diagnostics = parser.parse()

        # Combine diagnostics and sort by (line, column, start_offset)
        all_diagnostics = lex_diagnostics + parse_diagnostics
        all_diagnostics.sort(key=lambda d: (d.line, d.column, d.start_offset))

        error_count = sum(1 for d in all_diagnostics if d.severity == DiagnosticSeverity.ERROR)
        warning_count = sum(1 for d in all_diagnostics if d.severity == DiagnosticSeverity.WARNING)
        is_valid = error_count == 0

        return CompilerAnalysisResult(
            is_valid=is_valid,
            diagnostics=all_diagnostics,
            tokens=tokens,
            ast=ast,
            error_count=error_count,
            warning_count=warning_count,
        )
