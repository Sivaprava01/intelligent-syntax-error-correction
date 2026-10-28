# Project Demo Script (4 Persons: 2 Frontend, 2 Backend)
**Project:** Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques  
**Course:** Compiler Design (CD_CBP)

---

## Person 1: Backend Developer 1 (Lexer, Parser & Diagnostics)

### What They Did (10 Key Points):
1. Designed and built the C-subset Lexer that scans source code character-by-character into tokens.
2. Implemented token definitions (`TokenType`, keywords, identifiers, literals, and multi-char operators).
3. Tracked exact 1-indexed `line`, `column`, `start_offset`, and `end_offset` for every token.
4. Added preprocessor directive skipping (`#include`, `#define`) and comment stripping (`//`, `/* */`).
5. Built the Recursive-Descent Parser supporting variable declarations, functions, blocks, loops, and conditionals.
6. Structured the Abstract Syntax Tree (AST) node hierarchy (`Program`, `FunctionDef`, `VarDecl`, statements, expressions).
7. Handled expression parsing with standard operator precedence and associativity.
8. Implemented **Panic-Mode Error Recovery** to prevent cascading errors across statements and functions.
9. Created structured compiler diagnostic codes (`E101`–`E105` for lexical, `E201`–`E211` for syntax).
10. Built the `CompilerEngine` facade and wrote automated unit tests in `test_lexer.py` and `test_parser.py`.

### Code Snippets & File Locations:

#### 1. Panic-Mode Recovery in [`backend/app/compiler/parser.py`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/backend/app/compiler/parser.py#L151-L167)
```python
def _synchronize_statement(self) -> None:
    """Conservative recovery: skip tokens until a safe statement boundary."""
    self._panic_mode = False
    while not self._check(TokenType.EOF):
        if self._previous().type in (TokenType.SEMICOLON, TokenType.RBRACE):
            return
        if self._peek().type in STATEMENT_STARTERS:
            return
        if self._peek().type == TokenType.SEMICOLON:
            self._advance()
            return
        self._advance()
```

#### 2. Lexical Offset Tracking in [`backend/app/compiler/lexer.py`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/backend/app/compiler/lexer.py#L32-L46)
```python
def _advance(self) -> str:
    ch = self._peek()
    self.pos += 1
    if ch == "\n":
        self.line += 1
        self.column = 1
    else:
        self.column += 1
    return ch
```

---

## Person 2: Backend Developer 2 (AI Repair, Validator & APIs)

### What They Did (10 Key Points):
1. Built `SourceEditor` to safely apply character-offset string edits without file corruption.
2. Designed reverse-offset edit sorting so earlier offsets aren't invalidated by prior replacements.
3. Implemented `CandidateValidator` for "Compiler-in-the-Loop" re-parsing of candidate fixes.
4. Created diagnostic diffing (`new_codes - orig_codes`) to immediately reject AI hallucinations that introduce new errors.
5. Formulated `CandidateRanker` to mathematically score candidates based on error reduction and minimal change footprint.
6. Integrated Google Gemini LLM API with structured prompts for automated C syntax repairs.
7. Built the deterministic offline `MockCorrectionAgent` for rule-based repairs without an API key.
8. Implemented SHA-256 source code version hashing (`compute_source_version`) to protect against stale edit proposals.
9. Created `CorrectionService` to coordinate analysis, candidate generation, validation, ranking, and application.
10. Built FastAPI endpoints (`/api/analyze`, `/api/corrections`, `/api/corrections/apply`, `/api/health`) in `routes.py`.

### Code Snippets & File Locations:

#### 1. Reverse-Order Safe Edits in [`backend/app/correction/editor.py`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/backend/app/correction/editor.py#L70-L79)
```python
# Apply edits from end to beginning to preserve earlier offsets
reversed_edits = sorted(edits, key=lambda e: (e.start_offset, e.end_offset), reverse=True)
result = source

for edit in reversed_edits:
    before = result[: edit.start_offset]
    after = result[edit.end_offset :]
    result = before + edit.replacement + after

return True, result, []
```

#### 2. Re-parsing Validation & Hallucination Guard in [`backend/app/correction/validator.py`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/backend/app/correction/validator.py#L50-L67)
```python
# Compare diagnostic sets before and after
orig_codes = {d.code for d in original_diagnostics}
new_codes = {d.code for d in candidate_result.diagnostics}
introduced_codes = new_codes - orig_codes

if candidate_result.is_valid:
    candidate.validation_status = ValidationStatus.SYNTAX_VALIDATED
elif introduced_codes:
    candidate.validation_status = ValidationStatus.REJECTED_SYNTAX_INVALID
    candidate.warnings.append(f"Candidate introduced new syntax error(s): {', '.join(introduced_codes)}")
```

---

## Person 3: Frontend Developer 1 (Monaco Editor & Diagnostics UI)

### What They Did (10 Key Points):
1. Built the main IDE shell layout and core application state in `App.tsx`.
2. Integrated the Monaco Code Editor for C syntax editing with line numbers and dark theme in `CodeEditorPanel.tsx`.
3. Created the in-editor error marker system (`setModelMarkers`) to render red/amber squiggly underlines.
4. Mapped compiler diagnostic coordinates (`line`, `column`) directly to Monaco marker ranges.
5. Implemented interactive line-jumping (`revealLineInCenter`, `setPosition`) when clicking an error card.
6. Designed the structured `DiagnosticsPanel` showing error codes (`E101`, `E203`), categories, and severity badges.
7. Added code excerpt previews with monospace styling inside diagnostic cards.
8. Displayed compiler recovery status badges (e.g., "Recovered at next statement").
9. Built the top control `Toolbar` with sample C code presets (`samples.ts`) and "Detect Errors" button.
10. Handled editor loading states, empty input guards, and clean syntax state indicators.

### Code Snippets & File Locations:

#### 1. Monaco Diagnostic Markers in [`frontend/src/components/CodeEditorPanel.tsx`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/frontend/src/components/CodeEditorPanel.tsx#L35-L48)
```typescript
const markers: editor.IMarkerData[] = diagnostics.map((diag) => ({
  startLineNumber: Math.max(1, diag.line),
  startColumn: Math.max(1, diag.column),
  endLineNumber: Math.max(1, diag.line),
  endColumn: Math.max(1, diag.column + 1),
  message: `[${diag.code}] ${diag.message}`,
  severity:
    diag.severity === 'error'
      ? monacoRef.current!.MarkerSeverity.Error
      : monacoRef.current!.MarkerSeverity.Warning,
}));

monacoRef.current.editor.setModelMarkers(model, 'compiler', markers);
```

#### 2. Jump to Line on Diagnostic Click in [`frontend/src/components/CodeEditorPanel.tsx`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/frontend/src/components/CodeEditorPanel.tsx#L51-L57)
```typescript
useEffect(() => {
  if (targetLine && editorRef.current) {
    editorRef.current.revealLineInCenter(targetLine);
    editorRef.current.setPosition({ lineNumber: targetLine, column: 1 });
    editorRef.current.focus();
  }
}, [targetLine]);
```

---

## Person 4: Frontend Developer 2 (Diff Viewer, Approval Workflow & API)

### What They Did (10 Key Points):
1. Integrated Monaco Side-by-Side Diff Editor (`DiffEditor`) in `DiffViewerPanel.tsx` showing original vs corrected code.
2. Added visual green/red syntax highlighting for additions and deletions.
3. Built the proposal navigation carousel (`Proposal X of Y`) to switch between multiple repair options.
4. Added proposal metadata cards showing summary, compiler explanation, and confidence percentage.
5. Implemented the "Syntax Validated" shield badge verified by the compiler re-parser.
6. Built the "Accept & Apply" workflow that commits the fix and updates the editor in `App.tsx`.
7. Built the "Reject" workflow that dismisses proposals without touching the user's source code.
8. Created the `NotificationBanner` toast component for success, warning, and error alerts.
9. Implemented the type-safe REST API client (`api.ts`) with custom `ApiError` handling.
10. Defined full TypeScript interfaces in `types/index.ts` matching backend Pydantic schemas.

### Code Snippets & File Locations:

#### 1. Monaco Side-by-Side Diff Editor in [`frontend/src/components/DiffViewerPanel.tsx`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/frontend/src/components/DiffViewerPanel.tsx#L137-L157)
```tsx
<DiffEditor
  height="100%"
  language="c"
  theme="vs-dark"
  original={originalCode}
  modified={currentProposal.corrected_source}
  options={{
    readOnly: true,
    fontSize: 14,
    fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
    renderSideBySide: true,
    automaticLayout: true,
  }}
/>
```

#### 2. Accept & Apply Correction in [`frontend/src/App.tsx`](file:///c:/Users/sivap/Desktop/VNR%20SYLLABUS/3rd%20year%201st%20sem%20PDF/CD_CBP/frontend/src/App.tsx#L147-L168)
```typescript
const res = await applyCorrection(code, sourceVersion, proposal);

if (res.success) {
  setCode(res.updated_source);
  setSourceVersion(res.new_source_version);
  setDiagnostics(res.diagnostics);
  setIsValid(res.is_valid);

  const remaining = proposals.filter((p) => p.candidate_id !== proposal.candidate_id);
  setProposals(remaining);
  setActiveView('editor');
}
```

---

## Quick Demo Flow to Show Lecturer:
1. **Person 1:** Select `"1. Missing Semicolons & Variables"` -> click **"Detect Errors"** -> points to `parser.py` error recovery and terminal tests (`pytest -v`).
2. **Person 3:** Shows the red squiggly line at line 4 in Monaco Editor and clicks the `[E203]` card in `DiagnosticsPanel.tsx` to jump to the line.
3. **Person 2:** Explains how `validator.py` and `editor.py` test the fix in memory and prevent LLM hallucinations.
4. **Person 4:** Clicks **"Auto Correct"** -> shows side-by-side green/red Monaco Diff -> clicks **"Accept & Apply"** -> code is cleanly fixed and validated!
