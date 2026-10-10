"""Automated unit tests for the C subset Lexer."""

import pytest
from backend.app.compiler.lexer import Lexer
from backend.app.compiler.tokens import TokenType
from backend.app.compiler.diagnostics import DiagnosticCode


def test_keywords_and_identifiers():
    source = "int float double char void if else while for return break continue struct typedef const static sizeof switch case default my_var1 _test"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    token_types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert token_types == [
        TokenType.KW_INT,
        TokenType.KW_FLOAT,
        TokenType.KW_DOUBLE,
        TokenType.KW_CHAR,
        TokenType.KW_VOID,
        TokenType.KW_IF,
        TokenType.KW_ELSE,
        TokenType.KW_WHILE,
        TokenType.KW_FOR,
        TokenType.KW_RETURN,
        TokenType.KW_BREAK,
        TokenType.KW_CONTINUE,
        TokenType.KW_STRUCT,
        TokenType.KW_TYPEDEF,
        TokenType.KW_CONST,
        TokenType.KW_STATIC,
        TokenType.KW_SIZEOF,
        TokenType.KW_SWITCH,
        TokenType.KW_CASE,
        TokenType.KW_DEFAULT,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
    ]
    assert tokens[-3].value == "my_var1"
    assert tokens[-2].value == "_test"


def test_integer_and_float_literals():
    source = "42 0x2A 0XFF 3.14 .5 1e-4 2.5e3 100u 200L"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    ints = [t for t in tokens if t.type == TokenType.INT_LITERAL]
    floats = [t for t in tokens if t.type == TokenType.FLOAT_LITERAL]

    assert len(ints) == 5
    assert ints[0].literal_value == 42
    assert ints[1].literal_value == 42
    assert ints[2].literal_value == 255

    assert len(floats) == 4
    assert pytest.approx(floats[0].literal_value) == 3.14
    assert pytest.approx(floats[1].literal_value) == 0.5
    assert pytest.approx(floats[2].literal_value) == 1e-4
    assert pytest.approx(floats[3].literal_value) == 2.5e3


def test_operators_and_delimiters():
    source = "+ - * / % = += -= *= /= %= == != < <= > >= && || ! & | ^ ~ << >> ++ -- ( ) { } [ ] ; , : . ->"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert types == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.ASSIGN,
        TokenType.PLUS_ASSIGN,
        TokenType.MINUS_ASSIGN,
        TokenType.STAR_ASSIGN,
        TokenType.SLASH_ASSIGN,
        TokenType.PERCENT_ASSIGN,
        TokenType.EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.LOGICAL_AND,
        TokenType.LOGICAL_OR,
        TokenType.LOGICAL_NOT,
        TokenType.AMP,
        TokenType.PIPE,
        TokenType.CARET,
        TokenType.TILDE,
        TokenType.LSHIFT,
        TokenType.RSHIFT,
        TokenType.INCREMENT,
        TokenType.DECREMENT,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.LBRACKET,
        TokenType.RBRACKET,
        TokenType.SEMICOLON,
        TokenType.COMMA,
        TokenType.COLON,
        TokenType.DOT,
        TokenType.ARROW,
    ]


def test_token_position_and_offsets():
    source = "int x = 10;\nfloat y = 20.5;"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    # int token: line 1, col 1, offset 0..3
    assert tokens[0].value == "int"
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    assert tokens[0].start_offset == 0
    assert tokens[0].end_offset == 3

    # x token: line 1, col 5, offset 4..5
    assert tokens[1].value == "x"
    assert tokens[1].line == 1
    assert tokens[1].column == 5
    assert tokens[1].start_offset == 4
    assert tokens[1].end_offset == 5

    # float token on line 2
    float_tok = [t for t in tokens if t.type == TokenType.KW_FLOAT][0]
    assert float_tok.line == 2
    assert float_tok.column == 1
    assert source[float_tok.start_offset : float_tok.end_offset] == "float"


def test_comments_handling():
    source = """
    // Single line comment with int x = 100;
    int a = 1; /* Multi line
    comment with symbols += {} () */ int b = 2;
    """
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    # Comments should not produce tokens or false code tokens inside them
    code_token_values = [t.value for t in tokens if t.type != TokenType.EOF]
    assert code_token_values == ["int", "a", "=", "1", ";", "int", "b", "=", "2", ";"]


def test_string_and_char_literals():
    source = 'char *s = "Hello\\nWorld \\"Test\\""; char c = \'\\n\';'
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    str_tok = [t for t in tokens if t.type == TokenType.STRING_LITERAL][0]
    assert str_tok.literal_value == 'Hello\nWorld "Test"'
    char_tok = [t for t in tokens if t.type == TokenType.CHAR_LITERAL][0]
    assert char_tok.literal_value == '\n'


def test_lexical_error_unterminated_string():
    source = 'int x = "unterminated string;\nint y = 2;'
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) >= 1
    assert any(d.code == DiagnosticCode.LEX_UNTERMINATED_STRING.value for d in diagnostics)


def test_lexical_error_unterminated_comment():
    source = "int x = 1; /* unclosed comment starts here"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 1
    assert diagnostics[0].code == DiagnosticCode.LEX_UNTERMINATED_COMMENT.value


def test_lexical_error_invalid_char():
    source = "int x = @ + $;"
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 2
    assert all(d.code == DiagnosticCode.LEX_INVALID_CHAR.value for d in diagnostics)


def test_preprocessor_directives_include_define_pragma():
    source = """#include <stdio.h>
#include "my_header.h"
#define MAX_VAL 100
#pragma once
#ifdef DEBUG
// Comment inside preprocessor block
#endif
int main() {
    return 0;
}
"""
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    token_values = [t.value for t in tokens if t.type != TokenType.EOF]
    assert token_values == ["int", "main", "(", ")", "{", "return", "0", ";", "}"]

    # Check line tracking for 'int' keyword (should be on line 8)
    int_tok = tokens[0]
    assert int_tok.value == "int"
    assert int_tok.line == 8
    assert int_tok.column == 1


def test_preprocessor_line_continuation():
    source = """#define LONG_MACRO(a, b) \\
    ((a) + (b))
int x = 42;
"""
    lexer = Lexer(source)
    tokens, diagnostics = lexer.tokenize()

    assert len(diagnostics) == 0
    token_values = [t.value for t in tokens if t.type != TokenType.EOF]
    assert token_values == ["int", "x", "=", "42", ";"]
    assert tokens[0].line == 3

