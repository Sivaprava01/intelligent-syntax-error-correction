
# Product Requirements Document (PRD)

## 1. Product Name

Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques

## 2. Product Summary

A web application that helps users detect and repair syntax errors in C programs. It combines a deterministic compiler engine with an AI-assisted correction workflow built using CrewAI and Gemini.

The system identifies syntax errors, presents concise diagnostics, proposes minimal repairs, validates proposed code, and lets users decide which corrections to accept.

## 3. Problem Statement

Beginners learning C often encounter syntax errors that are difficult to locate and understand. Compiler diagnostics may identify an unexpected token without explaining the most likely correction. In addition, the reported location may be after the actual mistake.

A correction tool must do more than generate plausible code. It must identify errors, explain them, preserve the user's source, validate suggestions, and allow the user to inspect each change.

## 4. Product Goals

1. Detect supported C lexical and syntax errors.
2. Provide useful line and column information.
3. Display short, understandable error messages.
4. Generate minimal, context-aware correction proposals.
5. Use CrewAI to orchestrate AI-assisted analysis and correction.
6. Validate every proposed correction with deterministic compiler logic.
7. Require explicit user approval for every applied correction.
8. Show a red/green diff between original and corrected code.
9. Keep compiler-only functionality available when AI is unavailable.
10. Provide a repeatable automated test suite.

## 5. Non-Goals

The first release will not attempt to:
- Replace GCC, Clang, or another production compiler.
- Prove semantic correctness.
- Repair arbitrary runtime bugs.
- Optimize programs.
- Execute submitted programs automatically.
- Support every C standard feature.
- Provide user accounts or cloud project storage.
- Use a database without an approved requirement.
- Guarantee that every AI proposal preserves programmer intent.
- Perform unrestricted file-system operations.

## 6. Target Users

### Primary User
A student learning C programming and Compiler Design.

### Secondary User
An instructor demonstrating lexical analysis, parsing, error recovery, and syntax repair.

## 7. Primary User Journeys

### Journey A: Detect Errors

1. User opens the application.
2. User enters or pastes C code.
3. User selects Detect Errors.
4. Frontend submits source code to the backend.
5. Backend runs lexical analysis and parsing.
6. Backend returns diagnostics.
7. UI displays the errors with line and column information.
8. The source code remains unchanged.

### Journey B: Request Automatic Corrections

1. User enters C code.
2. User selects Auto Correct.
3. Backend analyzes the source with the compiler engine.
4. The correction workflow prepares error context.
5. CrewAI coordinates the AI correction task.
6. The AI proposes one or more candidate edits.
7. The backend checks the proposed edit format and source ranges.
8. The backend applies each candidate to a separate copy.
9. The compiler engine re-parses the resulting code.
10. The backend returns correction proposals with validation status.
11. User reviews each proposal.
12. User accepts or rejects it.
13. Accepted changes appear in the working corrected version.
14. UI updates the diff and remaining diagnostics.

### Journey C: AI Service Unavailable

1. User submits source code.
2. Compiler engine detects errors normally.
3. AI service times out, fails, or returns malformed output.
4. Backend returns the compiler diagnostics and an AI-unavailable status.
5. UI shows a concise message.
6. The application does not fabricate a verified correction.

## 8. Functional Requirements

### FR-01: Code Input
The application must provide a code editor supporting pasted C source code.

Acceptance criteria:
- User can enter multiline code.
- Editor preserves line breaks and indentation.
- Empty submissions are handled gracefully.
- Source size is limited by a documented configuration.

### FR-02: Detect Errors
The application must analyze code without modifying it.

Acceptance criteria:
- Returns a structured list of diagnostics.
- Each diagnostic contains severity, message, line, column, and category when available.
- Valid supported programs return no syntax errors.
- Invalid programs return useful diagnostics.
- The original input remains unchanged.

### FR-03: Diagnostic Categories
Support the following categories where implemented:
- Lexical error.
- Syntax error.
- Unsupported language feature.
- Internal parser limitation.
- AI correction failure.
- Validation failure.

Do not mislabel an unsupported feature as a confirmed syntax error.

### FR-04: Multiple Errors
The parser should attempt to recover and report multiple independent errors.

Acceptance criteria:
- Recovery is bounded.
- The parser avoids infinite loops.
- Duplicate or misleading cascaded errors are reduced where possible.
- A diagnostic may indicate that later errors are uncertain because an earlier error affected parsing.

### FR-05: AI-Assisted Correction
The correction workflow must propose candidate fixes for detected errors.

Acceptance criteria:
- AI receives relevant code and diagnostics, not unnecessary system data.
- AI output follows a structured schema.
- Candidates include a short explanation.
- Candidate edits are minimal when practical.
- The system does not accept a proposal merely because the AI claims it is valid.

### FR-06: Candidate Validation
Each candidate must be checked before it can be labelled syntax-validated.

Acceptance criteria:
- Edit operations are checked for valid ranges.
- Candidate code is created separately from original code.
- Candidate code is re-parsed.
- Failed candidates are rejected or marked unverified.
- Successful parsing is described as syntax validation, not semantic proof.

### FR-07: Individual Approval
The user must approve every correction before it changes the working corrected version.

Acceptance criteria:
- Accept applies the selected proposal.
- Reject discards the selected proposal.
- Rejected changes do not modify the code.
- The original source is preserved.
- The user can see which proposals have been accepted or rejected.
- Conflicting edits are detected rather than silently overwriting one another.

### FR-08: Code Diff
Display original and corrected code side-by-side.

Acceptance criteria:
- Removed lines are highlighted in red.
- Added lines are highlighted in green.
- Unchanged lines remain readable.
- The diff updates after accepted corrections.
- The diff reflects actual text changes, not AI-generated descriptions.
- Users can inspect the final corrected version.

### FR-09: API Reliability
The backend must handle malformed requests and dependency failures.

Acceptance criteria:
- Invalid request data receives an appropriate HTTP error.
- Internal exceptions do not expose secrets or stack traces to ordinary users.
- AI failure does not erase diagnostics already produced.
- Requests have configurable timeouts and input-size limits.

### FR-10: Testing
The project must include automated tests.

Acceptance criteria:
- Compiler unit tests run without network access.
- AI behavior is tested with mocked responses.
- API tests use FastAPI TestClient.
- Frontend tests cover primary interactions.
- Live Gemini tests are optional.
- Test commands are documented.

## 9. User Interface Requirements

### Main Workspace
- Application title.
- C code editor.
- Detect Errors button.
- Auto Correct button.
- Clear or reset control, with confirmation when unsaved content would be lost.
- Error and correction status area.

### Diagnostics Panel
- Error category.
- Short message.
- Line and column.
- Severity.
- Optional details when useful.

### Correction Review Panel
For each proposal:
- Proposed change.
- Brief explanation.
- Validation status.
- Accept button.
- Reject button.

### Comparison Panel
- Original source.
- Current corrected source.
- Red/green diff.
- Clear indication that changes were accepted by the user.

### Loading and Error States
Show clear states for:
- Analysis in progress.
- No syntax errors found.
- Syntax errors found.
- No safe correction candidate found.
- AI service unavailable.
- Request timed out.
- Invalid input.
- Internal failure.

## 10. Correction Safety Rules

1. Never mutate the original source.
2. Never silently accept an AI correction.
3. Never label an unvalidated candidate as verified.
4. Never execute user code as part of correction validation.
5. Never trust source offsets without checking them.
6. Reject malformed AI output.
7. Reject or flag candidates that modify unrelated code unexpectedly.
8. Re-parse after each accepted change or validate the combined result.
9. Detect conflicts between proposed edits.
10. Tell the user when the parser cannot validate a candidate.

## 11. C Language Scope

The project should implement a clearly documented, practical subset of C with an incremental path toward broader C11-compatible syntax.

Initial grammar coverage should prioritize:
- Identifiers and literals.
- Variable declarations.
- Primitive types and pointers.
- Expressions and operators.
- Function declarations and definitions.
- Function calls and arguments.
- Compound statements.
- if/else.
- switch/case/default.
- while and do-while.
- for loops.
- return, break, and continue.
- Arrays.
- Structs and enums, as supported by the parser design.
- Comments and string literals.
- Basic preprocessing directives, handled conservatively.

Advanced declarators, complex initializers, compiler extensions, and full preprocessing must be documented according to actual support.

A program accepted by the custom parser is not necessarily accepted by every C compiler.

## 12. Non-Functional Requirements

### Reliability
- Deterministic compiler results for identical inputs and configuration.
- Bounded parsing and correction operations.
- Graceful failure when AI is unavailable.

### Performance
- Compiler-only analysis should avoid unnecessary network requests.
- AI requests should have explicit timeouts.
- UI should show progress for longer requests.

### Maintainability
- Separate lexer, parser, correction, agent, API, and frontend code.
- Use type hints and Pydantic models.
- Keep prompts versioned and testable.
- Keep modules small and focused.

### Security
- API keys remain server-side.
- Source code is not sent to the AI unless the user requests AI-assisted correction.
- User code is never executed by default.
- Avoid logging source code unnecessarily.

## 13. Success Metrics

Evaluate using a curated corpus of valid and invalid C examples.

Record:
- Valid-code acceptance rate on supported examples.
- Error detection rate on labelled invalid examples.
- Diagnostic location accuracy.
- False-positive rate.
- Candidate syntax-validation rate.
- User correction acceptance rate.
- Regression-test pass rate.
- Compiler-only and AI-assisted response times.

Do not claim a percentage without defining and testing the corresponding dataset.

## 14. Definition of Done

The product is ready for demonstration when:
- Detection and correction are separate user actions.
- The compiler engine works without AI.
- AI suggestions are independently validated.
- Every correction requires user approval.
- Original code is preserved.
- Diff and diagnostics are functional.
- Automated tests pass.
- Setup instructions are reproducible.
- Known limitations are documented.
