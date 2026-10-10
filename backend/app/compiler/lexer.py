"""Lexer for the supported C language subset."""

from typing import Optional
from backend.app.compiler.tokens import Token, TokenType, KEYWORDS
from backend.app.compiler.diagnostics import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticCode,
    DiagnosticSeverity,
    extract_source_excerpt,
)


class Lexer:
    """Deterministic lexical analyzer for C subset source code."""

    def __init__(self, source: str) -> None:
        self.source: str = source
        self.length: int = len(source)
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return "\0"

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _add_diagnostic(
        self,
        code: DiagnosticCode,
        message: str,
        line: int,
        column: int,
        start_offset: int,
        end_offset: int,
        severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    ) -> None:
        excerpt = extract_source_excerpt(self.source, line)
        self.diagnostics.append(
            Diagnostic(
                code=code.value,
                category=DiagnosticCategory.LEXICAL,
                severity=severity,
                message=message,
                line=line,
                column=column,
                start_offset=start_offset,
                end_offset=end_offset,
                excerpt=excerpt,
            )
        )

    def tokenize(self) -> tuple[list[Token], list[Diagnostic]]:
        """Tokenizes the entire source string and returns (tokens, diagnostics)."""
        while self.pos < self.length:
            ch = self._peek()

            # Whitespace
            if ch in " \t\r\n\f\v":
                self._advance()
                continue

            # Preprocessor directives (#include, #define, #ifdef, #pragma, etc.)
            if ch == "#":
                self._skip_preprocessor_directive()
                continue

            # Comments or Slash operator
            if ch == "/":
                next_ch = self._peek(1)
                if next_ch == "/":
                    self._skip_single_line_comment()
                    continue
                elif next_ch == "*":
                    self._skip_multi_line_comment()
                    continue
                elif next_ch == "=":
                    start_pos = self.pos
                    line = self.line
                    col = self.column
                    self._advance()
                    self._advance()
                    self.tokens.append(Token(TokenType.SLASH_ASSIGN, "/=", line, col, start_pos, self.pos))
                    continue
                else:
                    start_pos = self.pos
                    line = self.line
                    col = self.column
                    self._advance()
                    self.tokens.append(Token(TokenType.SLASH, "/", line, col, start_pos, self.pos))
                    continue

            # String literal
            if ch == '"':
                self._tokenize_string()
                continue

            # Character literal
            if ch == "'":
                self._tokenize_char()
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == "_":
                self._tokenize_identifier_or_keyword()
                continue

            # Numbers (integers or floating point)
            if ch.isdigit():
                self._tokenize_number()
                continue
            elif ch == "." and self._peek(1).isdigit():
                self._tokenize_number()
                continue

            # Operators and Delimiters
            self._tokenize_operator_or_delimiter()

        # Append EOF token
        self.tokens.append(
            Token(
                type=TokenType.EOF,
                value="",
                line=self.line,
                column=self.column,
                start_offset=self.pos,
                end_offset=self.pos,
            )
        )

        return self.tokens, self.diagnostics

    def _skip_preprocessor_directive(self) -> None:
        """
        Scans a C preprocessor directive from '#' to the end of the logical line.
        Handles line continuations with backslash (\) and inline comments safely.
        """
        self._advance()  # Advance past '#'

        while self.pos < self.length:
            ch = self._peek()

            # Line continuation with backslash \
            if ch == "\\":
                next_ch = self._peek(1)
                if next_ch == "\n":
                    self._advance()  # \
                    self._advance()  # \n
                    continue
                elif next_ch == "\r" and self._peek(2) == "\n":
                    self._advance()  # \
                    self._advance()  # \r
                    self._advance()  # \n
                    continue

            # End of directive at newline
            if ch == "\n":
                break

            # Comments inside directive
            if ch == "/":
                next_ch = self._peek(1)
                if next_ch == "/":
                    self._skip_single_line_comment()
                    break
                elif next_ch == "*":
                    self._skip_multi_line_comment()
                    continue

            # Strings / headers in quotes inside directive (e.g. #include "myheader.h")
            if ch == '"':
                self._advance()
                while self.pos < self.length:
                    s_ch = self._peek()
                    if s_ch == '"':
                        self._advance()
                        break
                    elif s_ch == "\\":
                        self._advance()
                        if self.pos < self.length:
                            self._advance()
                    elif s_ch == "\n":
                        break
                    else:
                        self._advance()
                continue

            self._advance()

    def _skip_single_line_comment(self) -> None:
        # Advance past '//'
        self._advance()
        self._advance()
        while self.pos < self.length and self._peek() != "\n":
            self._advance()

    def _skip_multi_line_comment(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos
        # Advance past '/*'
        self._advance()
        self._advance()

        while self.pos < self.length:
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance()
                self._advance()
                return
            self._advance()

        # Unterminated comment
        self._add_diagnostic(
            DiagnosticCode.LEX_UNTERMINATED_COMMENT,
            "Unterminated multi-line comment '/*'",
            start_line,
            start_col,
            start_pos,
            self.pos,
        )

    def _tokenize_string(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos
        self._advance()  # Skip opening quote

        chars: list[str] = []
        is_terminated = False

        while self.pos < self.length:
            ch = self._peek()
            if ch == '"':
                self._advance()  # Skip closing quote
                is_terminated = True
                break
            elif ch == "\n":
                break  # Newline inside string without escape is an error in C
            elif ch == "\\":
                self._advance()
                escape_ch = self._peek()
                if escape_ch == "\0":
                    break
                escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "0": "\0"}
                chars.append(escape_map.get(escape_ch, escape_ch))
                self._advance()
            else:
                chars.append(ch)
                self._advance()

        raw_value = self.source[start_pos : self.pos]
        if not is_terminated:
            self._add_diagnostic(
                DiagnosticCode.LEX_UNTERMINATED_STRING,
                "Unterminated string literal",
                start_line,
                start_col,
                start_pos,
                self.pos,
            )
            self.tokens.append(
                Token(
                    type=TokenType.STRING_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value="".join(chars),
                )
            )
        else:
            self.tokens.append(
                Token(
                    type=TokenType.STRING_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value="".join(chars),
                )
            )

    def _tokenize_char(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos
        self._advance()  # Skip opening single quote

        char_val: Optional[str] = None
        if self.pos < self.length:
            ch = self._peek()
            if ch == "\\":
                self._advance()
                escape_ch = self._peek()
                escape_map = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "'": "'", '"': '"', "0": "\0"}
                char_val = escape_map.get(escape_ch, escape_ch)
                self._advance()
            elif ch != "'" and ch != "\n":
                char_val = ch
                self._advance()

        if self._peek() == "'":
            self._advance()  # Skip closing quote
            raw_value = self.source[start_pos : self.pos]
            self.tokens.append(
                Token(
                    type=TokenType.CHAR_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value=char_val,
                )
            )
        else:
            raw_value = self.source[start_pos : self.pos]
            self._add_diagnostic(
                DiagnosticCode.LEX_UNTERMINATED_CHAR,
                "Unterminated character literal",
                start_line,
                start_col,
                start_pos,
                self.pos,
            )
            self.tokens.append(
                Token(
                    type=TokenType.CHAR_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value=char_val,
                )
            )

    def _tokenize_identifier_or_keyword(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        while self.pos < self.length and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()

        ident_text = self.source[start_pos : self.pos]
        token_type = KEYWORDS.get(ident_text, TokenType.IDENTIFIER)

        self.tokens.append(
            Token(
                type=token_type,
                value=ident_text,
                line=start_line,
                column=start_col,
                start_offset=start_pos,
                end_offset=self.pos,
            )
        )

    def _tokenize_number(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos

        is_float = False

        # Hexadecimal literal: 0x... or 0X...
        if self._peek() == "0" and self._peek(1) in ("x", "X"):
            self._advance()
            self._advance()
            while self.pos < self.length and (self._peek().isdigit() or self._peek() in "abcdefABCDEF"):
                self._advance()
            raw_value = self.source[start_pos : self.pos]
            try:
                lit_val = int(raw_value, 16)
            except ValueError:
                lit_val = 0
                self._add_diagnostic(
                    DiagnosticCode.LEX_INVALID_NUMBER,
                    f"Invalid hexadecimal literal '{raw_value}'",
                    start_line,
                    start_col,
                    start_pos,
                    self.pos,
                )
            self.tokens.append(
                Token(
                    type=TokenType.INT_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value=lit_val,
                )
            )
            return

        # Digits before decimal
        while self.pos < self.length and self._peek().isdigit():
            self._advance()

        # Fractional part
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()  # '.'
            while self.pos < self.length and self._peek().isdigit():
                self._advance()
        elif self._peek() == "." and not self._peek(1).isdigit() and start_pos != self.pos:
            # e.g. 10. (valid float in C)
            is_float = True
            self._advance()

        # Scientific notation e or E
        if self._peek() in ("e", "E"):
            is_float = True
            self._advance()
            if self._peek() in ("+", "-"):
                self._advance()
            while self.pos < self.length and self._peek().isdigit():
                self._advance()

        # Suffixes: f, F, l, L, u, U
        while self.pos < self.length and self._peek() in ("f", "F", "l", "L", "u", "U"):
            self._advance()

        raw_value = self.source[start_pos : self.pos]
        if is_float:
            clean_str = raw_value.rstrip("fFlL")
            try:
                lit_val = float(clean_str)
            except ValueError:
                lit_val = 0.0
            self.tokens.append(
                Token(
                    type=TokenType.FLOAT_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value=lit_val,
                )
            )
        else:
            clean_str = raw_value.rstrip("uUlL")
            try:
                lit_val = int(clean_str, 8 if clean_str.startswith("0") and len(clean_str) > 1 else 10)
            except ValueError:
                lit_val = int(clean_str) if clean_str.isdigit() else 0
            self.tokens.append(
                Token(
                    type=TokenType.INT_LITERAL,
                    value=raw_value,
                    line=start_line,
                    column=start_col,
                    start_offset=start_pos,
                    end_offset=self.pos,
                    literal_value=lit_val,
                )
            )

    def _tokenize_operator_or_delimiter(self) -> None:
        start_line = self.line
        start_col = self.column
        start_pos = self.pos
        ch = self._advance()

        # Multi-character operator checks
        if ch == "+":
            if self._match("+"):
                self.tokens.append(Token(TokenType.INCREMENT, "++", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, "+=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.PLUS, "+", start_line, start_col, start_pos, self.pos))
        elif ch == "-":
            if self._match("-"):
                self.tokens.append(Token(TokenType.DECREMENT, "--", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, "-=", start_line, start_col, start_pos, self.pos))
            elif self._match(">"):
                self.tokens.append(Token(TokenType.ARROW, "->", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.MINUS, "-", start_line, start_col, start_pos, self.pos))
        elif ch == "*":
            if self._match("="):
                self.tokens.append(Token(TokenType.STAR_ASSIGN, "*=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.STAR, "*", start_line, start_col, start_pos, self.pos))
        elif ch == "%":
            if self._match("="):
                self.tokens.append(Token(TokenType.PERCENT_ASSIGN, "%=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.PERCENT, "%", start_line, start_col, start_pos, self.pos))
        elif ch == "=":
            if self._match("="):
                self.tokens.append(Token(TokenType.EQUAL, "==", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col, start_pos, self.pos))
        elif ch == "!":
            if self._match("="):
                self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.LOGICAL_NOT, "!", start_line, start_col, start_pos, self.pos))
        elif ch == "<":
            if self._match("<"):
                if self._match("="):
                    self.tokens.append(Token(TokenType.LSHIFT_ASSIGN, "<<=", start_line, start_col, start_pos, self.pos))
                else:
                    self.tokens.append(Token(TokenType.LSHIFT, "<<", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.LESS, "<", start_line, start_col, start_pos, self.pos))
        elif ch == ">":
            if self._match(">"):
                if self._match("="):
                    self.tokens.append(Token(TokenType.RSHIFT_ASSIGN, ">>=", start_line, start_col, start_pos, self.pos))
                else:
                    self.tokens.append(Token(TokenType.RSHIFT, ">>", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.GREATER, ">", start_line, start_col, start_pos, self.pos))
        elif ch == "&":
            if self._match("&"):
                self.tokens.append(Token(TokenType.LOGICAL_AND, "&&", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.AMP_ASSIGN, "&=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.AMP, "&", start_line, start_col, start_pos, self.pos))
        elif ch == "|":
            if self._match("|"):
                self.tokens.append(Token(TokenType.LOGICAL_OR, "||", start_line, start_col, start_pos, self.pos))
            elif self._match("="):
                self.tokens.append(Token(TokenType.PIPE_ASSIGN, "|=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.PIPE, "|", start_line, start_col, start_pos, self.pos))
        elif ch == "^":
            if self._match("="):
                self.tokens.append(Token(TokenType.CARET_ASSIGN, "^=", start_line, start_col, start_pos, self.pos))
            else:
                self.tokens.append(Token(TokenType.CARET, "^", start_line, start_col, start_pos, self.pos))
        elif ch == "~":
            self.tokens.append(Token(TokenType.TILDE, "~", start_line, start_col, start_pos, self.pos))
        elif ch == "(":
            self.tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col, start_pos, self.pos))
        elif ch == ")":
            self.tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col, start_pos, self.pos))
        elif ch == "{":
            self.tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col, start_pos, self.pos))
        elif ch == "}":
            self.tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col, start_pos, self.pos))
        elif ch == "[":
            self.tokens.append(Token(TokenType.LBRACKET, "[", start_line, start_col, start_pos, self.pos))
        elif ch == "]":
            self.tokens.append(Token(TokenType.RBRACKET, "]", start_line, start_col, start_pos, self.pos))
        elif ch == ";":
            self.tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col, start_pos, self.pos))
        elif ch == ",":
            self.tokens.append(Token(TokenType.COMMA, ",", start_line, start_col, start_pos, self.pos))
        elif ch == ":":
            self.tokens.append(Token(TokenType.COLON, ":", start_line, start_col, start_pos, self.pos))
        elif ch == ".":
            self.tokens.append(Token(TokenType.DOT, ".", start_line, start_col, start_pos, self.pos))
        else:
            self._add_diagnostic(
                DiagnosticCode.LEX_INVALID_CHAR,
                f"Unexpected character: {ch!r}",
                start_line,
                start_col,
                start_pos,
                self.pos,
            )
            self.tokens.append(Token(TokenType.ERROR, ch, start_line, start_col, start_pos, self.pos))
