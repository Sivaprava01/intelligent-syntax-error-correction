
# PHASE 1 — Deterministic Compiler Foundation

## 1. Objective

Implement a Python-based C syntax analysis engine that works independently of CrewAI and Gemini.

By the end of this phase, the backend must accept C source code, tokenize it, parse the supported grammar, report syntax diagnostics, recover from selected errors, and expose an API for syntax checking.

All essential compiler tests must run offline.

## 2. Prerequisites to Study

Study the following concepts before implementing the related modules.

### 2.1 Compiler Pipeline
Understand:
- Source code and tokens.
- Lexical analysis.
- Syntax analysis.
- Abstract syntax trees.
- Syntax errors versus semantic errors.
- Error recovery.
- Source positions and diagnostics.

Deliverable: a short explanation in project documentation describing how source code moves through the compiler engine.

### 2.2 Lexical Analysis
Study:
- Token types.
- Keywords and identifiers.
- Integer and floating-point literals.
- Character and string literals.
- Operators and punctuators.
- Comments.
- Whitespace.
- Longest-match tokenization.
- Line and column tracking.
- Unterminated strings and comments.

### 2.3 Parsing
Study:
- Context-free grammars.
- Terminals and non-terminals.
- Production rules.
- Recursive-descent parsing.
- Operator precedence and associativity.
- Statement parsing.
- Expression parsing.
- Lookahead.
- Syntax error reporting.
- Synchronization-based recovery.

Use a documented grammar subset. Do not attempt to reproduce the entire C standard grammar in one step.

### 2.4 Python Engineering
Study:
- Python type hints.
- Dataclasses or equivalent typed models.
- Exceptions.
- Modules and imports.
- Pytest fixtures and parameterized tests.
- FastAPI request and response models.
- Separation of business logic from HTTP handlers.

## 3. Initial Setup

Create the backend environment.

Windows PowerShell:

    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install fastapi "uvicorn[standard]" pytest pytest-cov httpx pydantic

Create a requirements.txt containing the dependencies actually used by the backend.

Record exact tested dependency versions before the phase is considered complete.

Suggested commands:

    python --version
    python -m pip freeze

Do not add CrewAI or a Gemini SDK in this phase unless an existing dependency requires it. Phase 1 must not depend on an LLM.

## 4. Initial Directory Structure

    backend/
      app/
        __init__.py
        main.py
        api/
          __init__.py
          routes.py
        schemas/
          __init__.py
          analysis.py
        compiler/
          __init__.py
          tokens.py
          lexer.py
          grammar.py
          ast_nodes.py
          diagnostics.py
          parser.py
          recovery.py
          validator.py
      tests/
        compiler/
        api/
        fixtures/
      requirements.txt
      pytest.ini

Create files incrementally. Do not fill every file with placeholder code simply to match the tree.

## 5. Step 1 — Define Shared Models

Before implementing the lexer, define a token representation.

Each token should contain:
- Token type.
- Original lexeme.
- Start line and column.
- End line and column where practical.
- Optional source offsets for reliable edit operations later.

Define diagnostic models with:
- Stable error code.
- Category.
- Severity.
- Short human-readable message.
- Line.
- Column.
- Optional end position.
- Optional offending token.
- Optional internal details for debugging.

Do not expose Python exception traces as user-facing diagnostics.

### Tests to write first

- Token and diagnostic objects preserve their values.
- Source positions use a consistent convention.
- Invalid line or column values are rejected where applicable.
- Serialization produces the expected structured response.

## 6. Step 2 — Implement the Lexer

The lexer converts source text into a sequence of tokens.

### Initial token categories

- Keywords: int, char, float, double, void, if, else, for, while, do, switch, case, default, break, continue, return, struct, enum, and supported additional keywords.
- Identifiers.
- Integer constants.
- Floating-point constants.
- Character constants.
- String literals.
- Operators.
- Punctuators.
- End-of-file.
- Lexical diagnostics.

### Lexical rules

1. Recognize whitespace and track line and column.
2. Skip comments without removing text inside strings.
3. Support single-line and multi-line comments.
4. Use longest-match rules for operators such as ==, !=, <=, >=, ++, --, &&, ||, +=, and ->.
5. Distinguish keywords from identifiers.
6. Preserve original lexemes.
7. Report unterminated strings and comments.
8. Handle escaped quotes in strings and character constants.
9. Avoid confusing comment markers with text inside literals.
10. Ensure the lexer always advances or terminates.

Do not silently accept malformed literals as valid tokens.

### Lexer test cases

Valid examples:
- int main() { return 0; }
- int total = 10 + 20;
- printf("Hello // world");
- // comment followed by code
- /* multi-line comment */ int x;
- x <= 10 && y != 0

Invalid examples:
- Unterminated string.
- Unterminated block comment.
- Malformed character constant.
- Unsupported or malformed literal form.

Tests must check token type, lexeme, and source positions, not only whether tokenization succeeds.

## 7. Step 3 — Document the Supported Grammar

Before coding the parser, write down the initial grammar and identify unsupported features.

Begin with:
- Translation unit.
- Function definition.
- Declaration.
- Type specifier.
- Declarator.
- Compound statement.
- Expression statement.
- if/else.
- while and for.
- return.
- break and continue.
- Function calls.
- Assignment and arithmetic expressions.
- Comparison and logical expressions.

Add features incrementally.

C declarators and expressions can be complex. Do not claim complete C compatibility based on a small grammar.

Create a grammar coverage checklist and update it when a new production is implemented.

## 8. Step 4 — Implement the Parser

Start with a recursive-descent parser for statements and declarations.

For expressions, implement a precedence-aware parser, such as precedence climbing or Pratt parsing.

The parser must:
- Consume lexer tokens.
- Report unexpected tokens.
- Identify missing expected tokens.
- Preserve token positions.
- Avoid infinite loops.
- Distinguish end-of-file errors.
- Produce a structured representation where useful.
- Avoid changing the original source.

Do not attempt to parse C with regular expressions alone.

### Parser tests

Valid programs:
1. Empty function body.
2. Function returning an integer.
3. Multiple variable declarations.
4. Arithmetic expressions.
5. Nested parentheses.
6. Function calls.
7. if/else statements.
8. while loops.
9. for loops.
10. return statements.
11. Nested compound statements.
12. Arrays and pointers when supported.

Invalid programs:
1. Missing semicolon.
2. Missing closing parenthesis.
3. Missing closing brace.
4. Unexpected operator.
5. Invalid expression.
6. Malformed function declaration.
7. Missing expression after assignment.
8. Incomplete return statement where the grammar requires an expression.
9. Missing operand.
10. Unexpected end of file.

Each test must specify its expected result.

## 9. Step 5 — Error Recovery

The parser should attempt to report multiple independent errors in one run.

Implement bounded recovery using synchronization points such as:
- Semicolon.
- Closing brace.
- A suitable statement boundary.
- End-of-file.

Recovery must be context-aware. A closing brace should not always be discarded simply because an error occurred.

Requirements:
- Ensure each recovery step consumes input or terminates.
- Set a maximum number of diagnostics per request.
- Prevent infinite loops.
- Avoid repeated identical diagnostics at the same position.
- Record when a diagnostic may be a cascade caused by an earlier error.
- Do not claim that every error can be recovered from accurately.

Tests:
- Two independent missing semicolons.
- Missing brace followed by another statement.
- Malformed expression followed by a valid statement.
- Truncated source.
- Multiple unexpected tokens.
- Pathological input that could otherwise loop indefinitely.

## 10. Step 6 — Build the Compiler Service

Create a service that:
1. Receives source text.
2. Runs the lexer.
3. Collects lexical diagnostics.
4. Runs the parser when appropriate.
5. Combines diagnostics.
6. Returns a structured result.
7. Preserves the source unchanged.

Keep this service independent of FastAPI.

Suggested result fields:
- success.
- supported_language_profile.
- diagnostics.
- token_count, if useful.
- analysis metadata.

Do not expose the entire token stream unless a debugging or educational feature needs it.

## 11. Step 7 — Implement the API

Create a minimal FastAPI endpoint.

Suggested endpoint:

    POST /api/v1/analyze

Example request:

    {
      "source_code": "int main() { return 0; }"
    }

Example response for a valid program:

    {
      "status": "valid",
      "diagnostics": [],
      "summary": "No syntax errors found in the supported C subset."
    }

Example response for an invalid program:

    {
      "status": "invalid",
      "diagnostics": [
        {
          "code": "C_SYNTAX_MISSING_SEMICOLON",
          "category": "syntax",
          "severity": "error",
          "message": "Expected ';' after the expression.",
          "line": 2,
          "column": 18
        }
      ]
    }

These are illustrative contracts. Define actual Pydantic models and keep the response consistent.

Use appropriate HTTP status codes for request errors and server failures. A validly submitted program containing syntax errors should ordinarily return a successful analysis response with diagnostics, not an HTTP 500.

## 12. Step 8 — Configure Pytest

Create pytest.ini:

    [pytest]
    testpaths = tests
    python_files = test_*.py
    python_functions = test_*
    addopts = -ra

Write tests before or alongside each module.

### Run all tests

    python -m pytest

### Run compiler tests

    python -m pytest tests/compiler -v

### Run API tests

    python -m pytest tests/api -v

### Run with coverage

    python -m pytest --cov=app --cov-report=term-missing

### Run one test

    python -m pytest tests/compiler/test_lexer.py -v

If pytest cannot import app, fix the package layout or working directory. Do not work around the problem by disabling tests.

## 13. Required Test Categories

### Lexer
- Keywords and identifiers.
- Operators and punctuators.
- Numeric literals.
- Strings and escapes.
- Comments.
- Line and column tracking.
- Malformed input.

### Parser
- Every implemented grammar production.
- Operator precedence.
- Nested statements.
- Missing tokens.
- Unexpected tokens.
- End-of-file handling.
- Error recovery.

### Compiler Service
- Valid input.
- Invalid input.
- Combined lexical and syntax diagnostics.
- Original source preservation.
- Input limits.

### API
- Valid request.
- Invalid request schema.
- Empty source.
- Oversized source.
- Valid C subset program.
- Invalid C subset program.
- Stable response format.

## 14. Optional External Compiler Validation

Do not make an external compiler mandatory for Phase 1.

After the custom parser is stable, an optional test adapter may invoke an installed GCC or Clang compiler in syntax-checking mode.

Important:
- Detect whether the compiler is installed.
- Skip optional tests when unavailable.
- Use subprocess argument arrays rather than shell command construction.
- Never execute the submitted program.
- Apply timeouts and safe process handling.
- Keep compiler output separate from custom-parser diagnostics.
- Do not treat the external compiler as the implementation of the custom parser.

## 15. Phase 1 Acceptance Criteria

Phase 1 is complete only when:

- Lexer and parser modules exist and are independently testable.
- The supported grammar is documented.
- Known valid programs pass.
- Known invalid programs produce expected diagnostics.
- Error positions are tested.
- Recovery is bounded.
- API responses follow a stable schema.
- All offline pytest tests pass.
- No AI dependency is required.
- README documents how to create the environment, run the API, and run tests.

## 16. Antigravity Execution Instructions

Implement this phase in small, reviewable steps.

For every step:
1. Inspect the current repository.
2. Explain the concept being implemented.
3. List the files that will be created or modified.
4. Implement only that step.
5. Add or update pytest tests.
6. Run the relevant tests.
7. Report actual results.
8. Update the grammar coverage checklist.
9. Wait for unresolved design decisions rather than inventing major requirements.

Do not proceed to Phase 2 until all Phase 1 acceptance criteria pass.
