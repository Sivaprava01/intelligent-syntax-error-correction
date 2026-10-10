"""Recursive descent parser with conservative error recovery for the C subset."""

from typing import Optional, Set
from backend.app.compiler.tokens import Token, TokenType, TYPE_KEYWORDS
from backend.app.compiler.ast_nodes import (
    ASTNode,
    Program,
    FunctionDef,
    Param,
    VarDecl,
    Declarator,
    Block,
    IfStmt,
    WhileStmt,
    DoWhileStmt,
    ForStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    ExprStmt,
    BinaryExpr,
    UnaryExpr,
    AssignExpr,
    CallExpr,
    Identifier,
    Literal,
    ArrayAccess,
    MemberAccess,
)
from backend.app.compiler.diagnostics import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticCode,
    DiagnosticSeverity,
    extract_source_excerpt,
)

MAX_DIAGNOSTICS = 50

STATEMENT_STARTERS: Set[TokenType] = {
    TokenType.KW_IF,
    TokenType.KW_WHILE,
    TokenType.KW_FOR,
    TokenType.KW_DO,
    TokenType.KW_RETURN,
    TokenType.KW_BREAK,
    TokenType.KW_CONTINUE,
    TokenType.LBRACE,
    TokenType.KW_INT,
    TokenType.KW_FLOAT,
    TokenType.KW_DOUBLE,
    TokenType.KW_CHAR,
    TokenType.KW_VOID,
    TokenType.KW_STRUCT,
}

ASSIGNMENT_OPERATORS = {
    TokenType.ASSIGN: "=",
    TokenType.PLUS_ASSIGN: "+=",
    TokenType.MINUS_ASSIGN: "-=",
    TokenType.STAR_ASSIGN: "*=",
    TokenType.SLASH_ASSIGN: "/=",
    TokenType.PERCENT_ASSIGN: "%=",
    TokenType.AMP_ASSIGN: "&=",
    TokenType.PIPE_ASSIGN: "|=",
    TokenType.CARET_ASSIGN: "^=",
    TokenType.LSHIFT_ASSIGN: "<<=",
    TokenType.RSHIFT_ASSIGN: ">>=",
}


class Parser:
    """Deterministic recursive descent parser for C subset with panic-mode recovery."""

    def __init__(self, tokens: list[Token], source: str = "") -> None:
        self.tokens: list[Token] = tokens
        self.source: str = source
        self.pos: int = 0
        self.diagnostics: list[Diagnostic] = []
        self._panic_mode: bool = False

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF token

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _previous(self) -> Token:
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        return self.tokens[0]

    def _add_diagnostic(
        self,
        code: DiagnosticCode,
        message: str,
        token: Optional[Token] = None,
        severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
        recovery_status: Optional[str] = None,
    ) -> None:
        if len(self.diagnostics) >= MAX_DIAGNOSTICS:
            return

        tok = token or self._peek()
        line = tok.line
        col = tok.column
        start_off = tok.start_offset
        end_off = tok.end_offset
        excerpt = extract_source_excerpt(self.source, line) if self.source else None

        self.diagnostics.append(
            Diagnostic(
                code=code.value,
                category=DiagnosticCategory.SYNTAX,
                severity=severity,
                message=message,
                line=line,
                column=col,
                start_offset=start_off,
                end_offset=end_off,
                excerpt=excerpt,
                recovery_status=recovery_status,
            )
        )

    def _consume(self, token_type: TokenType, error_message: str, code: DiagnosticCode = DiagnosticCode.PARSE_EXPECTED_TOKEN) -> Token:
        if self._check(token_type):
            return self._advance()
        
        cur = self._peek()
        self._add_diagnostic(code, error_message, cur)
        self._panic_mode = True
        return cur

    def _synchronize_statement(self) -> None:
        """Conservative recovery: skip tokens until a safe statement boundary."""
        self._panic_mode = False
        while not self._check(TokenType.EOF):
            # If we just passed a semicolon or right brace, we may start a new statement
            if self._previous().type in (TokenType.SEMICOLON, TokenType.RBRACE):
                return

            if self._peek().type in STATEMENT_STARTERS:
                return

            if self._peek().type == TokenType.SEMICOLON:
                self._advance()
                return

            self._advance()

    def _synchronize_top_level(self) -> None:
        """Synchronize to next top-level item (e.g. type keyword or EOF)."""
        self._panic_mode = False
        while not self._check(TokenType.EOF):
            if self._previous().type in (TokenType.SEMICOLON, TokenType.RBRACE):
                if self._peek().type in TYPE_KEYWORDS:
                    return

            if self._peek().type in TYPE_KEYWORDS:
                return

            self._advance()

    # --- Grammar parsing entry points ---

    def parse(self) -> tuple[Program, list[Diagnostic]]:
        """Parses the token stream into a Program AST node."""
        declarations: list[ASTNode] = []
        start_tok = self._peek()

        while not self._check(TokenType.EOF):
            try:
                decl = self._parse_external_declaration()
                if decl:
                    declarations.append(decl)
            except Exception as e:
                self._add_diagnostic(
                    DiagnosticCode.PARSE_UNEXPECTED_TOKEN,
                    f"Syntax error in top-level declaration: {e}",
                    self._peek(),
                    recovery_status="Recovered at next top-level declaration",
                )
                self._synchronize_top_level()

        eof_tok = self._peek()
        program = Program(
            declarations=declarations,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=eof_tok.end_offset,
        )
        return program, self.diagnostics

    def _is_type_specifier(self) -> bool:
        return self._peek().type in TYPE_KEYWORDS

    def _parse_type_specifier(self) -> str:
        tok = self._advance()
        type_name = tok.value
        if tok.type == TokenType.KW_STRUCT:
            if self._check(TokenType.IDENTIFIER):
                ident = self._advance()
                type_name = f"struct {ident.value}"
        # Parse pointer stars if any
        while self._match(TokenType.STAR):
            type_name += "*"
        return type_name

    def _parse_external_declaration(self) -> Optional[ASTNode]:
        """Parses a top-level function definition or global variable declaration."""
        if not self._is_type_specifier():
            cur = self._peek()
            self._add_diagnostic(
                DiagnosticCode.PARSE_INVALID_DECLARATION,
                f"Expected type specifier at top level, found {cur.value!r}",
                cur,
                recovery_status="Skipped to next declaration",
            )
            self._advance()
            self._synchronize_top_level()
            return None

        start_tok = self._peek()
        type_name = self._parse_type_specifier()

        if not self._check(TokenType.IDENTIFIER):
            cur = self._peek()
            self._add_diagnostic(
                DiagnosticCode.PARSE_MISSING_IDENTIFIER,
                f"Expected identifier after type '{type_name}', found {cur.value!r}",
                cur,
            )
            self._synchronize_top_level()
            return None

        name_tok = self._advance()
        name = name_tok.value

        # Check if this is a function definition / declaration
        if self._check(TokenType.LPAREN):
            return self._parse_function_tail(type_name, name, start_tok)

        # Otherwise it's a global variable declaration
        return self._parse_var_decl_tail(type_name, name, start_tok)

    def _parse_function_tail(self, return_type: str, name: str, start_tok: Token) -> Optional[FunctionDef]:
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_parameter_list()
        self._consume(TokenType.RPAREN, "Expected ')' after parameter list", DiagnosticCode.PARSE_MISSING_PAREN)

        # Function body or prototype
        if self._check(TokenType.LBRACE):
            body = self._parse_block()
            end_tok = self._previous()
            return FunctionDef(
                return_type=return_type,
                name=name,
                params=params,
                body=body,
                line=start_tok.line,
                column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=end_tok.end_offset,
            )
        elif self._match(TokenType.SEMICOLON):
            # Function prototype
            end_tok = self._previous()
            return FunctionDef(
                return_type=return_type,
                name=name,
                params=params,
                body=None,
                line=start_tok.line,
                column=start_tok.column,
                start_offset=start_tok.start_offset,
                end_offset=end_tok.end_offset,
            )
        else:
            cur = self._peek()
            self._add_diagnostic(
                DiagnosticCode.PARSE_EXPECTED_TOKEN,
                f"Expected '{{' or ';' after function header, found {cur.value!r}",
                cur,
            )
            self._synchronize_top_level()
            return None

    def _parse_parameter_list(self) -> list[Param]:
        params: list[Param] = []
        if self._check(TokenType.RPAREN):
            return params

        # Handle 'void' single parameter
        if self._check(TokenType.KW_VOID) and self._peek(1).type == TokenType.RPAREN:
            self._advance()
            return params

        while True:
            param = self._parse_parameter()
            if param:
                params.append(param)
            if not self._match(TokenType.COMMA):
                break

        return params

    def _parse_parameter(self) -> Optional[Param]:
        if not self._is_type_specifier():
            cur = self._peek()
            self._add_diagnostic(
                DiagnosticCode.PARSE_MISSING_TYPE,
                f"Expected parameter type, found {cur.value!r}",
                cur,
            )
            return None

        start_tok = self._peek()
        type_name = self._parse_type_specifier()
        param_name = ""
        if self._check(TokenType.IDENTIFIER):
            param_name = self._advance().value

        end_tok = self._previous()
        return Param(
            type_name=type_name,
            name=param_name,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_var_decl_tail(self, type_name: str, first_name: str, start_tok: Token) -> Optional[VarDecl]:
        declarators: list[Declarator] = []

        # Parse optional initializer for the first declarator
        first_init: Optional[ASTNode] = None
        if self._match(TokenType.ASSIGN):
            first_init = self._parse_expression()
        declarators.append(Declarator(name=first_name, init=first_init, line=start_tok.line, column=start_tok.column))

        # Parse additional declarators separated by comma
        while self._match(TokenType.COMMA):
            name_tok = self._consume(TokenType.IDENTIFIER, "Expected identifier after ',' in variable declaration")
            decl_name = name_tok.value
            decl_init: Optional[ASTNode] = None
            if self._match(TokenType.ASSIGN):
                decl_init = self._parse_expression()
            declarators.append(Declarator(name=decl_name, init=decl_init, line=name_tok.line, column=name_tok.column))

        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(
                DiagnosticCode.PARSE_MISSING_SEMICOLON,
                "Expected ';' after variable declaration",
                self._previous(),
                recovery_status="Recovered after declaration",
            )
            self._synchronize_statement()
        else:
            self._advance()

        end_tok = self._previous()
        return VarDecl(
            type_name=type_name,
            declarators=declarators,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    # --- Statement parsing ---

    def _parse_statement(self) -> Optional[ASTNode]:
        if self._check(TokenType.LBRACE):
            return self._parse_block()
        if self._check(TokenType.KW_IF):
            return self._parse_if_stmt()
        if self._check(TokenType.KW_WHILE):
            return self._parse_while_stmt()
        if self._check(TokenType.KW_DO):
            return self._parse_do_while_stmt()
        if self._check(TokenType.KW_FOR):
            return self._parse_for_stmt()
        if self._check(TokenType.KW_RETURN):
            return self._parse_return_stmt()
        if self._check(TokenType.KW_BREAK):
            return self._parse_break_stmt()
        if self._check(TokenType.KW_CONTINUE):
            return self._parse_continue_stmt()
        if self._is_type_specifier():
            start_tok = self._peek()
            type_name = self._parse_type_specifier()
            name_tok = self._consume(TokenType.IDENTIFIER, "Expected identifier after type in local variable declaration")
            return self._parse_var_decl_tail(type_name, name_tok.value, start_tok)
        if self._match(TokenType.SEMICOLON):
            # Empty statement
            tok = self._previous()
            return ExprStmt(expr=None, line=tok.line, column=tok.column, start_offset=tok.start_offset, end_offset=tok.end_offset)

        # Expression statement
        return self._parse_expr_stmt()

    def _parse_block(self) -> Block:
        start_tok = self._consume(TokenType.LBRACE, "Expected '{' to start block", DiagnosticCode.PARSE_MISSING_BRACE)
        statements: list[ASTNode] = []

        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            try:
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            except Exception as e:
                self._add_diagnostic(
                    DiagnosticCode.PARSE_INVALID_STATEMENT,
                    f"Syntax error in statement: {e}",
                    self._peek(),
                    recovery_status="Synchronized to next statement",
                )
                self._synchronize_statement()

        if self._check(TokenType.RBRACE):
            end_tok = self._advance()
        else:
            self._add_diagnostic(
                DiagnosticCode.PARSE_UNCLOSED_BLOCK,
                "Expected '}' to close block",
                self._peek(),
                recovery_status="Unclosed block at EOF",
            )
            end_tok = self._peek()

        return Block(
            statements=statements,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_if_stmt(self) -> IfStmt:
        start_tok = self._advance()  # 'if'
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'", DiagnosticCode.PARSE_MISSING_PAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition", DiagnosticCode.PARSE_MISSING_PAREN)

        then_branch = self._parse_statement()
        else_branch: Optional[ASTNode] = None

        if self._match(TokenType.KW_ELSE):
            else_branch = self._parse_statement()

        end_tok = self._previous()
        return IfStmt(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_while_stmt(self) -> WhileStmt:
        start_tok = self._advance()  # 'while'
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'", DiagnosticCode.PARSE_MISSING_PAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while condition", DiagnosticCode.PARSE_MISSING_PAREN)

        body = self._parse_statement()
        end_tok = self._previous()

        return WhileStmt(
            condition=condition,
            body=body,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_do_while_stmt(self) -> DoWhileStmt:
        start_tok = self._advance()  # 'do'
        body = self._parse_statement()
        self._consume(TokenType.KW_WHILE, "Expected 'while' after 'do' body")
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'", DiagnosticCode.PARSE_MISSING_PAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition", DiagnosticCode.PARSE_MISSING_PAREN)
        
        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(DiagnosticCode.PARSE_MISSING_SEMICOLON, "Expected ';' after do-while statement", self._previous())
        else:
            self._advance()

        end_tok = self._previous()
        return DoWhileStmt(
            body=body,
            condition=condition,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_for_stmt(self) -> ForStmt:
        start_tok = self._advance()  # 'for'
        self._consume(TokenType.LPAREN, "Expected '(' after 'for'", DiagnosticCode.PARSE_MISSING_PAREN)

        # Init clause: could be VarDecl or Expression or empty
        init: Optional[ASTNode] = None
        if self._is_type_specifier():
            init_start = self._peek()
            type_name = self._parse_type_specifier()
            name_tok = self._consume(TokenType.IDENTIFIER, "Expected identifier in for-loop variable declaration")
            init = self._parse_var_decl_tail(type_name, name_tok.value, init_start)
        elif not self._check(TokenType.SEMICOLON):
            init = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after for-loop init", DiagnosticCode.PARSE_MISSING_SEMICOLON)
        else:
            self._advance()  # consume ';'

        # Condition clause
        condition: Optional[ASTNode] = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after for-loop condition", DiagnosticCode.PARSE_MISSING_SEMICOLON)

        # Update clause
        update: Optional[ASTNode] = None
        if not self._check(TokenType.RPAREN):
            update = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after for-loop clauses", DiagnosticCode.PARSE_MISSING_PAREN)

        body = self._parse_statement()
        end_tok = self._previous()

        return ForStmt(
            init=init,
            condition=condition,
            update=update,
            body=body,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_return_stmt(self) -> ReturnStmt:
        start_tok = self._advance()  # 'return'
        value: Optional[ASTNode] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()

        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(
                DiagnosticCode.PARSE_MISSING_SEMICOLON,
                "Expected ';' after return statement",
                self._previous(),
                recovery_status="Recovered after return",
            )
            self._synchronize_statement()
        else:
            self._advance()

        end_tok = self._previous()
        return ReturnStmt(
            value=value,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_break_stmt(self) -> BreakStmt:
        start_tok = self._advance()  # 'break'
        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(DiagnosticCode.PARSE_MISSING_SEMICOLON, "Expected ';' after 'break'", self._previous())
            self._synchronize_statement()
        else:
            self._advance()
        end_tok = self._previous()
        return BreakStmt(
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_continue_stmt(self) -> ContinueStmt:
        start_tok = self._advance()  # 'continue'
        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(DiagnosticCode.PARSE_MISSING_SEMICOLON, "Expected ';' after 'continue'", self._previous())
            self._synchronize_statement()
        else:
            self._advance()
        end_tok = self._previous()
        return ContinueStmt(
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    def _parse_expr_stmt(self) -> ExprStmt:
        start_tok = self._peek()
        expr = self._parse_expression()

        if not self._check(TokenType.SEMICOLON):
            self._add_diagnostic(
                DiagnosticCode.PARSE_MISSING_SEMICOLON,
                "Expected ';' after expression",
                self._previous(),
                recovery_status="Recovered at statement boundary",
            )
            self._synchronize_statement()
        else:
            self._advance()

        end_tok = self._previous()
        return ExprStmt(
            expr=expr,
            line=start_tok.line,
            column=start_tok.column,
            start_offset=start_tok.start_offset,
            end_offset=end_tok.end_offset,
        )

    # --- Expression parsing with precedence climbing ---

    def _parse_expression(self) -> ASTNode:
        return self._parse_assignment_expr()

    def _parse_assignment_expr(self) -> ASTNode:
        expr = self._parse_logical_or()

        # Check if following token is an assignment operator
        if self._peek().type in ASSIGNMENT_OPERATORS:
            op_tok = self._advance()
            op_str = ASSIGNMENT_OPERATORS[op_tok.type]
            value = self._parse_assignment_expr()
            return AssignExpr(
                target=expr,
                op=op_str,
                value=value,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=value.end_offset if value else op_tok.end_offset,
            )

        return expr

    def _parse_logical_or(self) -> ASTNode:
        expr = self._parse_logical_and()
        while self._match(TokenType.LOGICAL_OR):
            op_tok = self._previous()
            right = self._parse_logical_and()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_logical_and(self) -> ASTNode:
        expr = self._parse_bitwise_or()
        while self._match(TokenType.LOGICAL_AND):
            op_tok = self._previous()
            right = self._parse_bitwise_or()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_bitwise_or(self) -> ASTNode:
        expr = self._parse_bitwise_xor()
        while self._match(TokenType.PIPE):
            op_tok = self._previous()
            right = self._parse_bitwise_xor()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_bitwise_xor(self) -> ASTNode:
        expr = self._parse_bitwise_and()
        while self._match(TokenType.CARET):
            op_tok = self._previous()
            right = self._parse_bitwise_and()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_bitwise_and(self) -> ASTNode:
        expr = self._parse_equality()
        while self._match(TokenType.AMP):
            op_tok = self._previous()
            right = self._parse_equality()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_equality(self) -> ASTNode:
        expr = self._parse_relational()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op_tok = self._previous()
            right = self._parse_relational()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_relational(self) -> ASTNode:
        expr = self._parse_shift()
        while self._match(TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL):
            op_tok = self._previous()
            right = self._parse_shift()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_shift(self) -> ASTNode:
        expr = self._parse_additive()
        while self._match(TokenType.LSHIFT, TokenType.RSHIFT):
            op_tok = self._previous()
            right = self._parse_additive()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_additive(self) -> ASTNode:
        expr = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._previous()
            right = self._parse_multiplicative()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_multiplicative(self) -> ASTNode:
        expr = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._previous()
            right = self._parse_unary()
            expr = BinaryExpr(
                left=expr,
                op=op_tok.value,
                right=right,
                line=expr.line,
                column=expr.column,
                start_offset=expr.start_offset,
                end_offset=right.end_offset if right else op_tok.end_offset,
            )
        return expr

    def _parse_unary(self) -> ASTNode:
        if self._match(
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.LOGICAL_NOT,
            TokenType.TILDE,
            TokenType.INCREMENT,
            TokenType.DECREMENT,
            TokenType.STAR,
            TokenType.AMP,
            TokenType.KW_SIZEOF,
        ):
            op_tok = self._previous()
            operand = self._parse_unary()
            return UnaryExpr(
                op=op_tok.value,
                operand=operand,
                prefix=True,
                line=op_tok.line,
                column=op_tok.column,
                start_offset=op_tok.start_offset,
                end_offset=operand.end_offset if operand else op_tok.end_offset,
            )

        return self._parse_postfix()

    def _parse_postfix(self) -> ASTNode:
        expr = self._parse_primary()

        while True:
            if self._match(TokenType.INCREMENT, TokenType.DECREMENT):
                op_tok = self._previous()
                expr = UnaryExpr(
                    op=op_tok.value,
                    operand=expr,
                    prefix=False,
                    line=expr.line,
                    column=expr.column,
                    start_offset=expr.start_offset,
                    end_offset=op_tok.end_offset,
                )
            elif self._match(TokenType.LPAREN):
                # Function call
                args = self._parse_argument_list()
                rparen = self._consume(TokenType.RPAREN, "Expected ')' after argument list", DiagnosticCode.PARSE_MISSING_PAREN)
                expr = CallExpr(
                    callee=expr,
                    args=args,
                    line=expr.line,
                    column=expr.column,
                    start_offset=expr.start_offset,
                    end_offset=rparen.end_offset,
                )
            elif self._match(TokenType.LBRACKET):
                # Array index
                index_expr = self._parse_expression()
                rbrack = self._consume(TokenType.RBRACKET, "Expected ']' after array index", DiagnosticCode.PARSE_EXPECTED_TOKEN)
                expr = ArrayAccess(
                    array=expr,
                    index=index_expr,
                    line=expr.line,
                    column=expr.column,
                    start_offset=expr.start_offset,
                    end_offset=rbrack.end_offset,
                )
            elif self._match(TokenType.DOT):
                member_tok = self._consume(TokenType.IDENTIFIER, "Expected member name after '.'")
                expr = MemberAccess(
                    object=expr,
                    member=member_tok.value,
                    is_arrow=False,
                    line=expr.line,
                    column=expr.column,
                    start_offset=expr.start_offset,
                    end_offset=member_tok.end_offset,
                )
            elif self._match(TokenType.ARROW):
                member_tok = self._consume(TokenType.IDENTIFIER, "Expected member name after '->'")
                expr = MemberAccess(
                    object=expr,
                    member=member_tok.value,
                    is_arrow=True,
                    line=expr.line,
                    column=expr.column,
                    start_offset=expr.start_offset,
                    end_offset=member_tok.end_offset,
                )
            else:
                break

        return expr

    def _parse_argument_list(self) -> list[ASTNode]:
        args: list[ASTNode] = []
        if self._check(TokenType.RPAREN):
            return args

        while True:
            arg = self._parse_assignment_expr()
            args.append(arg)
            if not self._match(TokenType.COMMA):
                break
        return args

    def _parse_primary(self) -> ASTNode:
        # Parenthesized expression
        if self._match(TokenType.LPAREN):
            start_tok = self._previous()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression", DiagnosticCode.PARSE_MISSING_PAREN)
            return expr

        # Identifier
        if self._match(TokenType.IDENTIFIER):
            tok = self._previous()
            return Identifier(
                name=tok.value,
                line=tok.line,
                column=tok.column,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
            )

        # Literals
        if self._match(TokenType.INT_LITERAL):
            tok = self._previous()
            return Literal(
                value=tok.literal_value,
                raw=tok.value,
                literal_type="int",
                line=tok.line,
                column=tok.column,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
            )

        if self._match(TokenType.FLOAT_LITERAL):
            tok = self._previous()
            return Literal(
                value=tok.literal_value,
                raw=tok.value,
                literal_type="float",
                line=tok.line,
                column=tok.column,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
            )

        if self._match(TokenType.STRING_LITERAL):
            tok = self._previous()
            return Literal(
                value=tok.literal_value,
                raw=tok.value,
                literal_type="string",
                line=tok.line,
                column=tok.column,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
            )

        if self._match(TokenType.CHAR_LITERAL):
            tok = self._previous()
            return Literal(
                value=tok.literal_value,
                raw=tok.value,
                literal_type="char",
                line=tok.line,
                column=tok.column,
                start_offset=tok.start_offset,
                end_offset=tok.end_offset,
            )

        # If unexpected token
        cur = self._peek()
        self._add_diagnostic(
            DiagnosticCode.PARSE_INVALID_EXPRESSION,
            f"Expected expression, found {cur.value!r}",
            cur,
        )
        self._advance()
        return Identifier(
            name="<error>",
            line=cur.line,
            column=cur.column,
            start_offset=cur.start_offset,
            end_offset=cur.end_offset,
        )
