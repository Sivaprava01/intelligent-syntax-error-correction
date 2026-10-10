"""Automated unit tests for the C subset Parser and CompilerEngine."""

import pytest
from backend.app.compiler.engine import CompilerEngine
from backend.app.compiler.ast_nodes import (
    Program,
    FunctionDef,
    VarDecl,
    IfStmt,
    WhileStmt,
    ForStmt,
    DoWhileStmt,
    ReturnStmt,
    BinaryExpr,
    CallExpr,
)
from backend.app.compiler.diagnostics import DiagnosticCode


@pytest.fixture
def engine() -> CompilerEngine:
    return CompilerEngine()


def test_valid_variable_declarations(engine: CompilerEngine):
    source = """
    int a;
    float b = 3.14;
    char c = 'z', d;
    int *ptr = 0;
    """
    result = engine.analyze(source)
    assert result.is_valid is True
    assert len(result.diagnostics) == 0
    assert result.ast is not None
    assert len(result.ast.declarations) == 4
    assert isinstance(result.ast.declarations[0], VarDecl)
    assert result.ast.declarations[0].type_name == "int"
    assert result.ast.declarations[0].declarators[0].name == "a"
    assert result.ast.declarations[1].declarators[0].init is not None


def test_valid_function_definitions_and_calls(engine: CompilerEngine):
    source = """
    int add(int x, int y) {
        return x + y;
    }

    void main() {
        int result = add(10, 20);
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is True
    assert len(result.diagnostics) == 0
    assert len(result.ast.declarations) == 2

    func1 = result.ast.declarations[0]
    assert isinstance(func1, FunctionDef)
    assert func1.name == "add"
    assert func1.return_type == "int"
    assert len(func1.params) == 2
    assert func1.body is not None

    func2 = result.ast.declarations[1]
    assert isinstance(func2, FunctionDef)
    assert func2.name == "main"


def test_control_structures_if_else_while_for_do(engine: CompilerEngine):
    source = """
    int test_loops(int n) {
        if (n > 0) {
            n = n - 1;
        } else {
            n = 0;
        }

        while (n < 10) {
            n = n + 1;
            if (n == 5) {
                break;
            }
        }

        for (int i = 0; i < 5; i++) {
            if (i == 2) {
                continue;
            }
        }

        do {
            n = n - 1;
        } while (n > 0);

        return n;
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is True
    assert len(result.diagnostics) == 0
    func = result.ast.declarations[0]
    assert isinstance(func, FunctionDef)
    stmts = func.body.statements
    assert isinstance(stmts[0], IfStmt)
    assert isinstance(stmts[1], WhileStmt)
    assert isinstance(stmts[2], ForStmt)
    assert isinstance(stmts[3], DoWhileStmt)
    assert isinstance(stmts[4], ReturnStmt)


def test_operator_precedence(engine: CompilerEngine):
    source = """
    int compute() {
        int x = 1 + 2 * 3 == 7 && 4 < 5;
        return x;
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is True
    assert len(result.diagnostics) == 0


def test_syntax_error_missing_semicolon(engine: CompilerEngine):
    source = """
    int main() {
        int a = 10
        int b = 20;
        return a + b;
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is False
    assert result.error_count >= 1
    codes = [d.code for d in result.diagnostics]
    assert DiagnosticCode.PARSE_MISSING_SEMICOLON.value in codes
    # Check that location is reported around line 3
    diag = [d for d in result.diagnostics if d.code == DiagnosticCode.PARSE_MISSING_SEMICOLON.value][0]
    assert diag.line in (2, 3)


def test_syntax_error_missing_closing_brace(engine: CompilerEngine):
    source = """
    int test() {
        int a = 1;
    """
    result = engine.analyze(source)
    assert result.is_valid is False
    codes = [d.code for d in result.diagnostics]
    assert DiagnosticCode.PARSE_UNCLOSED_BLOCK.value in codes or DiagnosticCode.PARSE_MISSING_BRACE.value in codes


def test_syntax_error_missing_parenthesis(engine: CompilerEngine):
    source = """
    int test() {
        if (x > 0 {
            return 1;
        }
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is False
    codes = [d.code for d in result.diagnostics]
    assert DiagnosticCode.PARSE_MISSING_PAREN.value in codes


def test_multiple_error_recovery(engine: CompilerEngine):
    source = """
    int func1() {
        int a = 10
        int b = 20
        return a + b;
    }

    int func2() {
        if (x > 0 {
            int y = 5;
        }
        return 0;
    }
    """
    result = engine.analyze(source)
    assert result.is_valid is False
    assert result.error_count >= 2
    # Ensure error recovery enabled parsing both functions and detecting errors in both
    lines = [d.line for d in result.diagnostics]
    assert any(line <= 5 for line in lines)  # Error in func1
    assert any(line >= 8 for line in lines)  # Error in func2


def test_empty_program(engine: CompilerEngine):
    source = ""
    result = engine.analyze(source)
    assert result.is_valid is True
    assert result.error_count == 0
    assert len(result.diagnostics) == 0
    assert result.ast is not None
    assert len(result.ast.declarations) == 0


def test_comments_only_program(engine: CompilerEngine):
    source = """
    // This is a test comment
    /* Another multi-line
       comment */
    """
    result = engine.analyze(source)
    assert result.is_valid is True
    assert result.error_count == 0
    assert len(result.ast.declarations) == 0


def test_preprocessor_directives_valid_program(engine: CompilerEngine):
    source = """#include <stdio.h>
#include "myheader.h"
#define PI 3.14159
#ifdef DEBUG
#define FLAG 1
#endif

int main() {
    int x = 42;
    return x;
}
"""
    result = engine.analyze(source)
    assert result.is_valid is True
    assert result.error_count == 0
    assert len(result.diagnostics) == 0
    assert len(result.ast.declarations) == 1
    assert isinstance(result.ast.declarations[0], FunctionDef)
    assert result.ast.declarations[0].name == "main"


def test_preprocessor_with_syntax_error_exact_user_case(engine: CompilerEngine):
    source = """#include <stdio.h>

int main() {
    int a = 10
    int b = 20;
    int sum = a + b;
    printf("Sum is: %d\\n", sum);
    return 0;
}
"""
    result = engine.analyze(source)
    assert result.is_valid is False
    assert result.error_count == 1
    diag = result.diagnostics[0]
    assert diag.code == DiagnosticCode.PARSE_MISSING_SEMICOLON.value
    assert diag.line == 4
    codes = [d.code for d in result.diagnostics]
    assert DiagnosticCode.LEX_INVALID_CHAR.value not in codes
    assert DiagnosticCode.PARSE_INVALID_DECLARATION.value not in codes

