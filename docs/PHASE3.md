
# PHASE 3 — React Web Application, Integration and Final Evaluation

## 1. Objective

Build the complete web interface for the C syntax correction system and integrate it with the FastAPI backend.

The finished application must support:
- Editing C source code.
- Detecting syntax errors.
- Requesting AI-assisted correction proposals.
- Reviewing and approving each correction.
- Rejecting unwanted corrections.
- Viewing the original and corrected code.
- Inspecting a red/green diff.
- Handling loading states and failures.
- Running automated frontend and integration tests.

## 2. Prerequisites to Study

Before implementing the frontend, study:

### 2.1 React
Understand:
- Components.
- Props and state.
- Controlled inputs.
- Hooks.
- Conditional rendering.
- Lists and stable keys.
- Event handlers.
- Loading and error states.

### 2.2 TypeScript
Understand:
- Interfaces and types.
- API response types.
- Optional fields.
- Union types for status values.
- Type-safe event handlers.
- Avoiding unnecessary use of any.

### 2.3 HTTP and FastAPI
Understand:
- HTTP methods and status codes.
- JSON requests and responses.
- Fetch or Axios.
- Request timeouts and network errors.
- CORS.
- API response validation.

### 2.4 Code Editor and Diff
Study:
- Monaco Editor or an equivalent maintained editor.
- C syntax highlighting.
- Line numbers.
- Editor change events.
- Diagnostic markers where supported.
- Original and modified text models.
- Side-by-side diff rendering.

### 2.5 Frontend Testing
Study:
- Vitest.
- React Testing Library.
- Mocking network requests.
- Testing visible behavior.
- Testing asynchronous UI states.
- Avoiding brittle tests based on implementation details.

## 3. Technology Stack

Use:
- React.
- Vite.
- TypeScript.
- Monaco Editor or a suitable equivalent.
- A diff viewer that supports side-by-side changes.
- Vitest.
- React Testing Library.
- A consistent CSS strategy.

Use existing dependencies when the project already contains a suitable editor or diff viewer.

Do not install several competing libraries that provide the same functionality.

## 4. Step 1 — Inspect the Backend API

Before implementing the frontend, inspect the actual FastAPI routes and Pydantic schemas.

Document the final request and response contracts for:
- POST /api/v1/analyze
- POST /api/v1/correct

The frontend must use these real contracts.

Do not invent response fields or hard-code sample diagnostics into production UI code.

If the backend contract changes, update the frontend types and tests together.

## 5. Step 2 — Initialize the Frontend

Create or inspect the frontend application.

Suggested commands if the frontend does not exist:

    npm create vite@latest frontend -- --template react-ts
    cd frontend
    npm install

Install an editor and diff library after checking compatibility with the selected React version.

Add test dependencies:

    npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom

Add a test script in package.json:

    "test": "vitest run",
    "test:watch": "vitest"

Preserve any existing scripts that the project already needs.

Run:

    npm run dev

Confirm that the default development page loads before implementing application features.

## 6. Step 3 — Create the Application Layout

Create a clear, professional developer-tool interface.

### Header
Include:
- Application name.
- Short description.
- Current analysis or correction status.
- Optional indication of the supported C language profile.

### Main Editor
Include:
- C syntax highlighting.
- Line numbers.
- Code input.
- Detect Errors button.
- Auto Correct button.
- Clear or reset control.

### Diagnostics Panel
Include:
- Error count.
- Diagnostic list.
- Short message.
- Error category.
- Line and column.
- A way to navigate to the relevant line where supported.

### Correction Review Panel
Include:
- Candidate explanation.
- Validation status.
- Accept button.
- Reject button.
- Related diagnostics.

### Comparison Area
Include:
- Original source.
- Current corrected source.
- Side-by-side red/green diff.
- Clear indication of which corrections have been accepted.

Do not build the entire interface as one enormous React component. Use focused components with clear responsibilities.

## 7. Step 4 — Define Frontend Types

Create TypeScript types that match the backend API.

Suggested conceptual types:

    type DiagnosticSeverity = "error" | "warning" | "info";

    type ValidationStatus =
      | "proposed"
      | "syntax_validated"
      | "rejected_invalid_edit"
      | "rejected_syntax_invalid"
      | "unverified"
      | "ai_unavailable";

    interface Diagnostic {
      code: string;
      category: string;
      severity: DiagnosticSeverity;
      message: string;
      line: number;
      column: number;
    }

    interface CorrectionProposal {
      candidate_id: string;
      explanation: string;
      validation_status: ValidationStatus;
    }

These are illustrative examples. Extend or adjust them to match the real backend schemas.

Avoid maintaining duplicate incompatible definitions of the same API contract.

## 8. Step 5 — Build the API Client

Create a centralized API service.

Suggested responsibilities:
- Submit source for analysis.
- Request correction candidates.
- Handle request errors.
- Enforce reasonable client-side timeouts.
- Normalize error messages for display.
- Return typed responses.

Configure the backend base URL through a frontend environment variable.

Example:

    VITE_API_BASE_URL=http://localhost:8000

Do not place the Gemini API key in any VITE_ environment variable. Vite exposes such variables to browser code.

Configure CORS on the backend for the local frontend development origin. Do not use unrestricted CORS in a deployed production environment.

## 9. Step 6 — Implement Detect Errors

Expected behavior:

1. User enters source code.
2. User clicks Detect Errors.
3. Button enters a loading state.
4. Frontend submits the source to the analysis endpoint.
5. Backend returns diagnostics.
6. Diagnostics appear in the panel.
7. The editor source remains unchanged.
8. Previous results are replaced with the current analysis result.

Requirements:
- Disable repeated submissions when appropriate.
- Handle empty source.
- Handle network failure.
- Display a no-errors state when appropriate.
- Do not confuse a failed request with a valid program.
- Do not trigger the AI correction workflow.

## 10. Step 7 — Implement Auto Correct

Expected behavior:

1. User enters source code.
2. User clicks Auto Correct.
3. Frontend submits source to the correction endpoint.
4. Backend analyzes the source and proposes corrections.
5. Frontend displays the returned proposals.
6. Each proposal shows its explanation and validation status.
7. No proposal is automatically accepted.
8. The original code remains unchanged.

When the backend returns no safe candidate, explain that no validated correction is available.

When the AI service fails, preserve and display the diagnostics returned by the backend.

## 11. Step 8 — Implement Correction Approval

Each proposal must support Accept and Reject.

### Accept

When the user accepts a proposal:
- Confirm that it belongs to the current source version.
- Ask the backend to apply the edit or use a clearly defined backend-controlled approval contract.
- Ensure the edit does not conflict with previously accepted edits.
- Re-validate the combined working source.
- Update the corrected source only after successful application.
- Update the diff.
- Mark the proposal as accepted.

If acceptance changes the source version, stale proposals must be invalidated or revalidated.

### Reject

When the user rejects a proposal:
- Leave the working corrected source unchanged.
- Mark the proposal as rejected.
- Update the review panel.
- Keep the original source intact.

### Important Design Rule

Do not trust an arbitrary corrected-source string returned by the browser.

The backend must enforce the correction contract and verify edit application. If the initial backend API does not support approval and rejection, extend the API deliberately and add tests before wiring the UI to it.

## 12. Step 9 — Implement the Diff Viewer

Use a maintained diff viewer or Monaco's diff editor.

Display:
- Original source on the left.
- Current accepted version on the right.
- Removed lines in red.
- Added lines in green.
- Unchanged lines normally.

The diff must be computed from actual source strings.

Do not use the AI explanation to decide which lines are highlighted.

Ensure:
- Empty source is supported.
- Long lines remain readable.
- Scrolling is usable.
- The layout works at typical laptop screen sizes.
- Diff updates after accepted corrections.
- Rejected proposals do not appear as applied changes.

## 13. Step 10 — Improve the User Experience

Implement:
- Loading indicators.
- Disabled buttons while requests are running.
- Clear success and failure messages.
- Empty states.
- Accessible button labels.
- Keyboard-friendly controls.
- Visible validation statuses.
- Error counts.
- A way to return to the editor from a diagnostic.
- A way to start a fresh analysis.

Avoid unnecessary animations and excessive visual effects.

Do not show a fake progress percentage for an operation whose progress is unknown.

## 14. Step 11 — Frontend Unit Tests

Create tests for:
- Initial application rendering.
- Editor input state.
- Detect Errors button.
- Auto Correct button.
- Loading indicators.
- API error messages.
- Diagnostic list rendering.
- No-errors state.
- Correction proposal rendering.
- Accept action.
- Reject action.
- Original source preservation.
- Diff updates.
- AI-unavailable state.
- Invalid or empty requests.

Mock API responses for normal unit tests.

Tests should verify what the user sees and how the application behaves, not depend on internal component implementation details.

Run:

    npm test

Run a production build:

    npm run build

Both must succeed.

## 15. Step 12 — Backend Integration Tests

Use FastAPI TestClient for backend integration tests.

Verify:
- Request schemas.
- Response schemas.
- Analysis endpoint behavior.
- Correction endpoint behavior.
- AI failure handling.
- Invalid candidate rejection.
- Approval and rejection contracts, if implemented.
- Stale correction handling.
- CORS configuration where practical.

Keep the tests independent of a real Gemini API.

## 16. Step 13 — End-to-End Testing

Use a browser automation tool such as Playwright only if it is compatible with the environment and adds useful coverage.

Test these scenarios:

### Scenario A: Valid Program
Input:

    int main(void) {
        return 0;
    }

Expected:
- No syntax errors under the supported grammar.
- Original source remains unchanged.
- No correction is automatically applied.

### Scenario B: Missing Semicolon
Input:

    int main(void) {
        int x = 10
        return 0;
    }

Expected:
- A diagnostic is reported near the missing separator.
- A correction may be proposed.
- The candidate is re-parsed.
- The user must approve it.
- The diff shows the actual change.

### Scenario C: Missing Parenthesis
Input:

    int main(void) {
        if (1 > 0 {
            return 0;
        }
        return 1;
    }

Expected:
- A useful diagnostic is shown.
- A candidate may be proposed.
- The candidate is independently validated.
- The application does not silently change the source.

### Scenario D: Reject a Correction
Expected:
- Rejected proposal is not applied.
- Working source remains unchanged.
- Original source remains unchanged.

### Scenario E: AI Unavailable
Expected:
- Detection remains functional.
- UI reports that correction assistance is unavailable.
- No fabricated candidate is shown.

### Scenario F: Conflicting Proposals
Expected:
- Stale proposals are detected.
- The backend does not overwrite unrelated accepted edits.
- The user is asked to refresh or review the updated source when necessary.

### Scenario G: Multiple Errors
Expected:
- Multiple diagnostics appear when recovery succeeds.
- The interface distinguishes diagnostics from correction proposals.
- It does not imply that all errors were necessarily discovered.

## 17. Step 14 — Run the Complete Test Suite

From the backend directory:

    python -m pytest

With coverage:

    python -m pytest --cov=app --cov-report=term-missing

From the frontend directory:

    npm test
    npm run build

Run optional end-to-end tests using the configured browser test runner.

Record:
- Commands executed.
- Pass/fail counts.
- Skipped optional tests.
- Known failures.
- Environment requirements.

Do not claim all tests pass if a command was not actually executed.

## 18. Step 15 — Run the Complete Application Locally

### Terminal 1: Backend

    cd backend
    .\.venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --port 8000

Open:

    http://localhost:8000/docs

Confirm that the API routes are available.

### Terminal 2: Frontend

    cd frontend
    npm run dev

Open the local URL printed by Vite.

Check that the frontend is configured to call the backend on port 8000.

Ensure the actual API route prefixes match the documented routes.

## 19. Step 16 — Documentation and Final Cleanup

Update README.md with:
- Project overview.
- Features.
- Architecture.
- Supported C subset.
- Limitations.
- Prerequisites.
- Environment setup.
- API key setup.
- Backend run instructions.
- Frontend run instructions.
- Test commands.
- Example inputs.
- Troubleshooting.
- Privacy and security notes.

Ensure:
- .env is ignored by Git.
- No real credentials are committed.
- No temporary debugging output remains.
- No hard-coded fake results remain.
- No unnecessary dependencies are installed.
- No failing tests are hidden.
- No unsupported features are described as complete.

## 20. Final Evaluation

Prepare a test corpus containing:
- Valid supported C programs.
- Programs with a missing semicolon.
- Programs with missing delimiters.
- Malformed expressions.
- Misspelled keywords.
- Multiple independent errors.
- Strings and comments containing punctuation.
- Unsupported C constructs.
- Inputs designed to test recovery and robustness.

For every test, record:
- Source program.
- Expected validity.
- Expected diagnostic category.
- Expected error location where deterministic.
- Whether a correction was proposed.
- Whether the candidate passed re-parsing.
- Whether the correction was accepted.
- Whether unrelated source was preserved.

Calculate evaluation metrics from the actual results.

Do not claim complete C support or perfect correction accuracy.

## 21. Phase 3 Acceptance Criteria

- Frontend and backend run together.
- Detect Errors works without AI.
- Auto Correct uses the real correction service.
- Original source remains unchanged until a correction is accepted.
- Every correction is reviewed individually.
- The diff reflects actual source changes.
- Validation status is accurate.
- Loading and failure states work.
- Frontend tests pass.
- Backend tests pass.
- Production frontend build succeeds.
- Setup and testing instructions are documented.
- Known limitations are disclosed.

## 22. Antigravity Execution Instructions

1. Read PROJECT_ROADMAP.md and PRD.md.
2. Read this entire phase before implementation.
3. Inspect existing frontend and backend code.
4. Reuse working code and dependencies where practical.
5. Verify API contracts before writing frontend integration.
6. Implement one user journey at a time.
7. Write or update tests for every feature.
8. Run frontend and backend tests separately.
9. Test the integrated application manually.
10. Report actual results and remaining defects.
11. Preserve the user's original source code.
12. Never silently apply corrections.
13. Do not mark the project complete until all acceptance criteria are checked.

The final application must demonstrate a genuine compiler-plus-AI correction workflow, not just a chat interface that returns rewritten C code.
