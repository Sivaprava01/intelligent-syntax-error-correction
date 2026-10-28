
# Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques

## 1. Project Overview

### 1.1 Objective

Build a web-based application that detects syntax errors in C source code and helps users correct them using compiler design techniques and an AI-assisted correction workflow.

The application will allow users to:
- Enter or paste C source code.
- Detect syntax errors without modifying the source.
- View concise diagnostics with line and column information.
- Request proposed automatic corrections.
- Review, accept, or reject each proposed correction.
- Compare original and corrected code using a red/green diff.
- Validate proposed fixes before presenting them as verified corrections.

### 1.2 Core Principle

The system combines deterministic compiler techniques with AI-assisted correction.

The compiler engine is responsible for lexical analysis, parsing, syntax diagnostics, and deterministic validation. CrewAI coordinates the AI correction workflow. Gemini generates contextual correction suggestions.

AI output must never be treated as proof that code is syntactically valid. Every proposed correction must pass the available deterministic validation process.

### 1.3 Target Users

- Students learning C and Compiler Design.
- Beginners who need understandable syntax diagnostics.
- Instructors demonstrating lexical analysis, parsing, error recovery, and correction.

### 1.4 Project Boundaries

The initial project focuses on C syntax errors and minimal syntax repairs.

It does not promise:
- Complete support for every feature of every C standard.
- Automatic repair of arbitrary logical bugs.
- Guaranteed preservation of programmer intent.
- Complete macro expansion or preprocessing compatibility.
- Guaranteed compilation of every accepted program.
- Guaranteed semantic correctness of AI-generated code.

Unsupported language features must be documented and reported rather than silently misinterpreted.

---

## 2. Technology Stack

### Frontend
- React
- Vite
- TypeScript
- A syntax-highlighted code editor, preferably Monaco Editor
- A diff viewer supporting removed and added lines
- A component library or consistent custom styling

### Backend
- Python
- FastAPI
- Pydantic for request and response validation
- Uvicorn as the development server

### Compiler Engine
- Custom C-oriented lexer
- Custom parser with a documented grammar and supported subset
- Structured syntax diagnostics
- Error recovery
- Correction candidate representation
- Re-parsing and validation of candidate code

### Agent Framework
- CrewAI
- Gemini API through a supported CrewAI LLM integration
- Environment variables for credentials and configuration

### Testing
- pytest
- pytest-cov for coverage reports
- FastAPI TestClient
- React Testing Library
- Vitest
- Mocked LLM responses for repeatable automated tests

### Storage
No database is required for the initial version.
Source code and corrections remain in the active session unless the user explicitly saves or exports them through a supported feature.

---

## 3. High-Level Architecture

User
  |
  v
React Frontend
  |
  v
FastAPI Backend
  |
  +--> Request Validation
  |
  +--> Compiler Engine
  |      |
  |      +--> Lexer
  |      +--> Token Stream
  |      +--> Parser
  |      +--> Diagnostics
  |      +--> Error Recovery
  |
  +--> Correction Workflow
         |
         +--> Build Error Context
         +--> CrewAI Agent
         +--> Candidate Corrections
         +--> Candidate Validation
         +--> Ranking and Filtering
         +--> Approval Workflow
  |
  v
Structured API Response
  |
  v
Frontend Diagnostics, Review UI and Diff

The frontend must never need direct access to the Gemini API key.

---

## 4. Repository Structure

Use a monorepo with separate frontend and backend directories.

project-root/
├── PROJECT_ROADMAP.md
├── PRD.md
├── PHASE_1.md
├── PHASE_2.md
├── PHASE_3.md
├── README.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── compiler/
│   │   │   ├── lexer.py
│   │   │   ├── tokens.py
│   │   │   ├── parser.py
│   │   │   ├── grammar.py
│   │   │   ├── ast_nodes.py
│   │   │   ├── diagnostics.py
│   │   │   ├── recovery.py
│   │   │   └── validator.py
│   │   ├── correction/
│   │   │   ├── candidates.py
│   │   │   ├── ranking.py
│   │   │   └── service.py
│   │   ├── agents/
│   │   │   ├── crew.py
│   │   │   ├── tasks.py
│   │   │   └── prompts.py
│   │   └── config.py
│   ├── tests/
│   │   ├── compiler/
│   │   ├── correction/
│   │   ├── api/
│   │   └── fixtures/
│   ├── requirements.txt
│   ├── pytest.ini
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── features/
    │   ├── services/
    │   ├── types/
    │   ├── hooks/
    │   └── App.tsx
    ├── tests/
    ├── package.json
    └── vite.config.ts

This is the intended logical structure, not a requirement to create every empty file immediately. Files may be grouped differently when there is a clear technical reason, but compiler, correction, agent, API, and UI responsibilities must remain separated.

---

## 5. Development Phases

### Phase 1: Deterministic Compiler Foundation

Goal: establish reliable C tokenization, parsing, diagnostics, and automated tests before introducing AI.

Deliverables:
- Python backend skeleton.
- Documented supported C subset.
- Lexer and token model.
- Parser and grammar.
- Structured error diagnostics.
- Error recovery that attempts to report multiple errors.
- Syntax validation API.
- pytest unit and integration tests.
- Test fixtures for valid and invalid C programs.

Exit criteria:
- Valid supported programs are accepted.
- Known invalid programs produce expected diagnostics.
- Line and column positions are correct for tested cases.
- Lexical errors are distinguished from syntax errors.
- Tests pass without internet access or an LLM API key.

### Phase 2: AI-Assisted Correction Engine

Goal: propose useful, minimal corrections and verify them before they reach the user.

Deliverables:
- Correction candidate data model.
- Candidate generation and ranking.
- CrewAI correction workflow.
- Gemini integration.
- Strict structured AI output.
- Validation of proposed changes through the compiler engine.
- Individual correction approval.
- Rejection of invalid or unsafe proposals.
- AI-mocked pytest tests and optional live API tests.

Exit criteria:
- AI failures do not crash the compiler API.
- Candidate fixes are independently validated.
- Invalid candidates cannot be marked verified.
- Users can accept or reject proposals individually.
- Core tests run without an API key.

### Phase 3: Web Application and Final Integration

Goal: deliver a complete and usable web application.

Deliverables:
- React interface.
- Code editor with C syntax highlighting and line numbers.
- Detect Errors and Auto Correct actions.
- Diagnostics panel.
- Correction review controls.
- Original and corrected code views.
- Red/green diff.
- FastAPI and frontend integration.
- Frontend and end-to-end tests.
- README, setup instructions, limitations, and evaluation results.

Exit criteria:
- Both applications run locally.
- Frontend and backend communicate successfully.
- Corrections require explicit approval.
- The original source is preserved.
- All required automated tests pass.
- The final demonstration uses documented test cases.

---

## 6. Development Rules

1. Read the relevant phase document before changing code.
2. Inspect existing files before creating or replacing them.
3. Do not regenerate the whole project when a focused change is sufficient.
4. Implement and test one module at a time.
5. Do not mix compiler logic with HTTP handlers.
6. Do not mix AI prompts with parsing logic.
7. Use typed request and response models.
8. Do not hard-code secrets.
9. Never send source code to an external AI provider without the application explicitly invoking the AI correction workflow.
10. Preserve the original code.
11. Never silently apply corrections.
12. Re-parse every proposed corrected version.
13. Report validation status accurately.
14. Do not label syntax-valid code as semantically correct.
15. Do not hide failing tests.
16. Do not disable or weaken tests merely to make a build pass.
17. Do not add a database, authentication, multiple agents, or unrelated features unless explicitly approved.
18. Avoid unnecessary dependencies.
19. Keep functions focused and code readable.
20. Update documentation whenever an API contract or supported-language boundary changes.

---

## 7. Testing Strategy

### Backend Unit Tests

Test each component independently:
- Lexer token types and source positions.
- Parser grammar rules.
- AST construction where implemented.
- Error detection and recovery.
- Candidate edit operations.
- Candidate ranking.
- Validation status.
- Request schema validation.

### Backend Integration Tests

Test:
- Valid source through the compiler service.
- Invalid source through the compiler service.
- Multiple diagnostics.
- Correction candidate validation.
- AI provider failure.
- Malformed AI output.
- API request and response contracts.

### Frontend Tests

Test:
- Editor input and state management.
- Detect Errors request.
- Auto Correct request.
- Diagnostic display.
- Accept and reject actions.
- Original code preservation.
- Diff display.
- Loading, timeout, and error states.

### End-to-End Tests

Verify complete user journeys:
1. Submit valid code.
2. Submit code containing a missing semicolon.
3. Detect errors without modifying source.
4. Request a correction.
5. Review and accept the proposal.
6. Inspect the resulting diff.
7. Reject a proposal and confirm the original remains unchanged.

### Offline Testing Requirement

Ordinary automated tests must not require:
- A live Gemini API.
- A paid API plan.
- An internet connection.
- A real C compiler, except in explicitly marked optional compiler integration tests.

Mock external AI calls in automated tests. Live API checks should be separate, opt-in tests.

---

## 8. Evaluation Metrics

Record measurable results rather than making unsupported accuracy claims.

- Lexer test pass rate.
- Parser test pass rate on the supported grammar.
- Diagnostic location accuracy on known test cases.
- Error detection rate on a curated invalid-code corpus.
- False positive rate on a curated valid-code corpus.
- Correction acceptance rate.
- Percentage of proposed fixes that pass re-parsing.
- Regression count after each release.
- Average response time, separated into compiler-only and AI-assisted requests.

For error detection, define the test corpus and expected outputs before reporting percentages. Avoid claiming complete C compatibility.

---

## 9. Security and Reliability

- Keep Gemini credentials in backend environment variables.
- Do not expose credentials to the browser.
- Set maximum source-code size and request time limits.
- Handle malformed requests gracefully.
- Do not execute arbitrary user-submitted C programs by default.
- Do not execute AI-generated code.
- Treat AI output as untrusted data.
- Limit AI output length and candidate count.
- Validate all edit positions and source ranges.
- Prevent corrections from unexpectedly replacing unrelated source regions.
- Do not log complete source code or secrets unnecessarily.
- Apply appropriate CORS restrictions for local development and deployment.
- Keep AI failures separate from compiler failures.

---

## 10. Definition of Done

The project is complete when:

- All three phases meet their acceptance criteria.
- The compiler engine works independently of AI.
- AI correction suggestions are validated before being presented as verified.
- Users explicitly approve each correction.
- The UI shows diagnostics and original-versus-corrected differences.
- Automated tests pass and their results are documented.
- Setup and run instructions are reproducible.
- Supported C features and limitations are documented.
- A demonstration can be completed using the documented sample programs.

The final goal is a reliable educational syntax-correction system, not an unrestricted replacement for a production C compiler.
