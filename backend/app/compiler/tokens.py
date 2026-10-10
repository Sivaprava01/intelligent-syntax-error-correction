"""Compiler tokens definition for the C subset."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class TokenType(Enum):
    # Keywords
    KW_INT = "int"
    KW_FLOAT = "float"
    KW_DOUBLE = "double"
    KW_CHAR = "char"
    KW_VOID = "void"
    KW_IF = "if"
    KW_ELSE = "else"
    KW_WHILE = "while"
    KW_FOR = "for"
    KW_DO = "do"
    KW_RETURN = "return"
    KW_BREAK = "break"
    KW_CONTINUE = "continue"
    KW_STRUCT = "struct"
    KW_TYPEDEF = "typedef"
    KW_CONST = "const"
    KW_STATIC = "static"
    KW_SIZEOF = "sizeof"
    KW_SWITCH = "switch"
    KW_CASE = "case"
    KW_DEFAULT = "default"

    # Identifiers and Literals
    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    CHAR_LITERAL = "CHAR_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"

    # Arithmetic Operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"

    # Assignment Operators
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    STAR_ASSIGN = "*="
    SLASH_ASSIGN = "/="
    PERCENT_ASSIGN = "%="
    AMP_ASSIGN = "&="
    PIPE_ASSIGN = "|="
    CARET_ASSIGN = "^="
    LSHIFT_ASSIGN = "<<="
    RSHIFT_ASSIGN = ">>="

    # Increment / Decrement
    INCREMENT = "++"
    DECREMENT = "--"

    # Relational Operators
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="

    # Logical Operators
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    LOGICAL_NOT = "!"

    # Bitwise Operators
    AMP = "&"
    PIPE = "|"
    CARET = "^"
    TILDE = "~"
    LSHIFT = "<<"
    RSHIFT = ">>"

    # Punctuation & Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    SEMICOLON = ";"
    COMMA = ","
    COLON = ":"
    DOT = "."
    ARROW = "->"

    # Special
    EOF = "EOF"
    ERROR = "ERROR"


KEYWORDS: dict[str, TokenType] = {
    "int": TokenType.KW_INT,
    "float": TokenType.KW_FLOAT,
    "double": TokenType.KW_DOUBLE,
    "char": TokenType.KW_CHAR,
    "void": TokenType.KW_VOID,
    "if": TokenType.KW_IF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE,
    "for": TokenType.KW_FOR,
    "do": TokenType.KW_DO,
    "return": TokenType.KW_RETURN,
    "break": TokenType.KW_BREAK,
    "continue": TokenType.KW_CONTINUE,
    "struct": TokenType.KW_STRUCT,
    "typedef": TokenType.KW_TYPEDEF,
    "const": TokenType.KW_CONST,
    "static": TokenType.KW_STATIC,
    "sizeof": TokenType.KW_SIZEOF,
    "switch": TokenType.KW_SWITCH,
    "case": TokenType.KW_CASE,
    "default": TokenType.KW_DEFAULT,
}

TYPE_KEYWORDS: set[TokenType] = {
    TokenType.KW_INT,
    TokenType.KW_FLOAT,
    TokenType.KW_DOUBLE,
    TokenType.KW_CHAR,
    TokenType.KW_VOID,
    TokenType.KW_STRUCT,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    start_offset: int
    end_offset: int
    literal_value: Optional[Any] = None

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "type_name": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
        }
