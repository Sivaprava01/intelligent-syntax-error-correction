# Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques

## 1. Project Overview

### 1.1 Project Title

**Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques**

### 1.2 Project Description

The proposed project is a web-based application that detects syntax errors in C programs and suggests appropriate corrections using fundamental compiler design techniques and a Large Language Model (LLM).

The system combines a deterministic compiler-based engine with an AI-assisted correction mechanism. The compiler engine is responsible for analyzing the source code, identifying lexical and syntactic errors, and generating structured diagnostic information. A CrewAI agent integrated with the Gemini API uses this diagnostic information and the surrounding source-code context to propose possible corrections.

Every proposed correction is validated by the backend before being presented to the user. The user can review each change individually, compare the original and corrected code, and explicitly accept or reject the suggestion.

The application is designed to make syntax-error detection and correction more understandable, transparent, and accessible, particularly for students and beginner programmers learning C and compiler design.

The primary objective is not to replace a compiler or guarantee that every C program can be repaired automatically. Instead, the project aims to demonstrate how traditional compiler techniques and AI-assisted reasoning can be combined to create a controlled and explainable syntax-error correction system.

---

# 2. Problem Statement

## 2.1 Background

Programming languages follow specific grammatical rules that determine how instructions, declarations, expressions, functions, and other language constructs must be written. A compiler uses these rules to analyze source code and determine whether the program follows the syntax of the programming language.

C is a widely used programming language in computer science education because it introduces fundamental programming concepts such as variables, data types, operators, control statements, functions, arrays, pointers, and memory management.

However, beginners frequently encounter syntax errors while writing C programs. These errors may include missing semicolons, unmatched parentheses, missing braces, incorrect declaration syntax, malformed expressions, misplaced keywords, and incorrectly structured control statements.

Although compilers report many of these errors, the reported diagnostic may not always clearly explain the original mistake or the most appropriate correction. A single syntax error may also cause additional errors to be reported later in the source code, making it difficult for beginners to identify the actual cause of the problem.

For example, consider the following C program:

```c
#include <stdio.h>

int main() {
    int a = 10
    printf("%d\n", a);
    return 0;
}
```

The declaration `int a = 10` is missing a semicolon.

A compiler can identify the resulting syntax problem, but a beginner may not immediately understand whether the declaration, the `printf` statement, or some other part of the program needs to be changed.

The proposed application addresses this difficulty by combining compiler-based diagnostics with context-aware correction suggestions and an interactive review process.

## 2.2 Formal Problem Statement

Traditional syntax-error detection systems primarily report violations of programming-language grammar. Although these diagnostics are essential, they may require the programmer to manually interpret the error, locate the underlying mistake, determine an appropriate correction, and verify whether the modification resolves the problem.

This process can be challenging for beginner programmers, particularly when multiple syntax errors occur together or when an earlier mistake causes misleading downstream diagnostics.

Furthermore, simply passing an entire program to a language model and requesting a corrected version can introduce additional risks. The model may modify valid code unnecessarily, change program logic, overlook language-specific rules, or produce a correction that still contains syntax errors.

Therefore, there is a need for a system that combines deterministic compiler techniques with AI-assisted correction while retaining control over the proposed changes.

**The problem addressed by this project is to design and implement a web-based system that detects lexical and syntactic errors in C source code, generates context-aware correction suggestions, validates the proposed corrections using compiler-based analysis, and allows users to review and approve each change before it is applied.**

## 2.3 Key Problems to Be Addressed

The project focuses on the following problems:

1. **Difficulty understanding compiler diagnostics:** Beginners may find conventional compiler messages difficult to interpret, particularly when the error is caused by a mistake earlier in the program.

2. **Time-consuming manual correction:** Identifying the exact location of an error and determining the correct modification can require repeated editing and compilation.

3. **Cascading syntax errors:** A single missing delimiter or incorrectly structured statement may cause multiple subsequent diagnostic messages.

4. **Lack of contextual correction suggestions:** A diagnostic message identifies a problem, but it may not provide an appropriate source-code edit tailored to the surrounding context.

5. **Unreliable unrestricted AI correction:** An LLM may rewrite valid portions of a program, introduce new syntax errors, or make unnecessary modifications if it is allowed to replace the entire source code without sufficient constraints.

6. **Lack of correction transparency:** Users need to understand exactly what will change before modifying their original source code.

7. **Need for safe and controlled correction:** A proposed edit must be checked before being offered as a valid correction, and the final decision must remain with the user.

---

# 3. Existing System

## 3.1 Traditional Compiler-Based Error Detection

A conventional compiler analyzes source code through several stages. Depending on the compiler, these stages include lexical analysis, syntax analysis, semantic analysis, and subsequent compilation stages.

Lexical analysis identifies tokens such as keywords, identifiers, operators, literals, and punctuation. Syntax analysis checks whether the sequence of tokens follows the grammar of the language.

When an error is encountered, the compiler produces a diagnostic message containing information such as the error type, location, or unexpected token.

### Limitations

- Compiler messages may be difficult for beginners to understand.
- The compiler generally expects the programmer to determine and implement the correction.
- One syntax error can cause multiple follow-up diagnostics.
- The compiler's primary purpose is compilation and error reporting, not necessarily interactive, individually reviewable correction suggestions.
- Error-recovery behavior and diagnostic quality differ between compilers.

These limitations do not mean conventional compilers are ineffective. They remain essential tools for detecting syntax errors. The proposed project builds upon compiler techniques and adds a dedicated correction and review workflow.

## 3.2 Direct LLM-Based Code Correction

Another possible approach is to send the source code to a Large Language Model and request a corrected program.

### Limitations

- The model may alter code that was already correct.
- It may change program logic while attempting to fix syntax.
- It may return code that still contains syntax errors.
- Its output may vary between requests.
- It may incorrectly identify the cause of an error.
- It may replace the entire source code when only a small edit is necessary.
- It cannot be assumed to validate its own suggestions correctly.

An LLM is useful for reasoning about possible corrections, but its output should not be treated as proof that the resulting program is syntactically valid.

## 3.3 Existing Approach Comparison

| Feature | Traditional compiler | Direct LLM correction | Proposed system |
|---|---|---|---|
| Detects lexical or syntax errors | Yes, depending on compiler support | May identify them | Deterministic compiler-based analysis |
| Provides structured diagnostics | Compiler-dependent | Prompt-dependent | Defined diagnostic schema |
| Suggests contextual corrections | Limited or compiler-dependent | Yes, potentially | AI-assisted suggestions |
| Validates proposed corrections | Compiler-based checks may be available | Not guaranteed | Independent backend validation |
| Shows exact source changes | Tool-dependent | Not guaranteed | Side-by-side diff |
| Individual correction approval | Tool-dependent | Not guaranteed | Required |
| Prevents all logic changes | Not guaranteed | Not guaranteed | Constrained edits and checks; not an absolute guarantee |
| Works without an AI API key | Yes, for compiler analysis | No | Detection and testing can work without a live LLM |
| Retains original source | Tool-dependent | Depends on implementation | Original source is preserved until approval |

---

# 4. Proposed Solution

## 4.1 Overview

The proposed solution is a web application that combines a custom compiler-analysis component with an AI-assisted correction component.

The system separates the responsibility for detecting errors from the responsibility for proposing corrections.

The compiler engine performs deterministic analysis of the input program. It identifies supported lexical and syntactic errors and produces structured diagnostics containing relevant locations, error categories, and contextual information.

A single CrewAI agent uses these diagnostics, together with the relevant source-code context, to suggest a small number of possible corrections. The agent can access explicitly defined tools for inspecting diagnostics and requesting candidate validation.

The backend then independently checks every proposed edit. It verifies that the edit is structurally valid, applies it to a separate copy of the source code, and runs the compiler-analysis engine again.

Only suitable candidates that pass the configured validation criteria are presented as validated suggestions. If a correction cannot be validated confidently, the application should communicate that limitation rather than presenting the candidate as guaranteed correct.

The frontend displays the original source code, detected errors, and proposed changes. Users can inspect each correction and accept or reject it individually.

The original source code is not automatically overwritten by the AI.

## 4.2 Core Objectives

The proposed system has the following objectives:

1. Detect supported lexical and syntactic errors in C source code.
2. Report error locations and concise explanations.
3. Reduce misleading diagnostics where possible through syntax-aware error recovery.
4. Generate context-aware correction suggestions using an LLM.
5. Use CrewAI to organize the correction agent and its tools.
6. Validate proposed corrections using deterministic backend checks.
7. Preserve the original source code throughout the correction process.
8. Display changes through a readable, GitHub-style red-and-green diff.
9. Require explicit user approval for every individual correction.
10. Provide automated tests for compiler analysis, correction validation, API behavior, and the frontend workflow.
11. Support testing without depending on live AI API calls.
12. Clearly document the implemented grammar and unsupported C features.

## 4.3 Proposed Workflow

The system follows this sequence:

1. The user enters or pastes C source code into the editor.
2. The user selects **Detect Errors**.
3. The backend validates the request and tokenizes the source code.
4. The parser analyzes the token sequence using the supported grammar.
5. The backend generates structured diagnostics.
6. The frontend displays the errors and their source locations.
7. The user selects **Auto Correct**.
8. The backend provides the diagnostics and relevant source context to the CrewAI correction agent.
9. The agent proposes one or more minimal edits.
10. The backend validates the edit ranges and candidate source code.
11. The compiler-analysis engine analyzes the candidate again.
12. Suitable candidates are returned as correction proposals.
13. The frontend displays each proposed change in a diff view.
14. The user accepts or rejects each correction individually.
15. Accepted changes are applied to the current working source only after the backend confirms that the proposal is still applicable.
16. The user can run detection again on the resulting source code.

A failed correction must not be silently accepted. If validation fails, the candidate should be rejected or marked as unvalidated, depending on the implemented policy.

---

# 5. Detailed Technical Solution

## 5.1 System Architecture

The application consists of five major components:

1. Frontend user interface
2. Backend API
3. Compiler-analysis engine
4. AI-assisted correction engine
5. Validation and approval mechanism

### High-Level Architecture

```text
                    USER
                     |
                     v
          +-----------------------+
          | React + TypeScript UI |
          |                       |
          | C Code Editor         |
          | Detect Errors         |
          | Auto Correct          |
          | Diagnostics           |
          | Diff and Approval     |
          +-----------+-----------+
                      |
                      v
          +-----------------------+
          | FastAPI Backend       |
          |                       |
          | Request Validation    |
          | API and Orchestration |
          +-----------+-----------+
                      |
             +--------+---------+
             |                  |
             v                  v
  +--------------------+  +---------------------+
  | Compiler Engine    |  | Correction Engine   |
  |                    |  |                     |
  | Lexer              |  | CrewAI Agent        |
  | Token Stream       |  | Gemini API          |
  | Parser             |  | Diagnostic Context  |
  | Diagnostics        |  | Candidate Edits     |
  | Error Recovery     |  | Correction Tools    |
  +----------+---------+  +----------+----------+
             |                       |
             |                       v
             |            +---------------------+
             +----------->| Backend Validation  |
                          |                     |
                          | Edit Range Checks   |
                          | Candidate Parsing   |
                          | Safety Checks       |
                          +----------+----------+
                                     |
                                     v
                          +---------------------+
                          | Validated Proposals |
                          | Await User Approval |
                          +---------------------+
```

The diagram represents logical responsibilities rather than a requirement to run every component as a separate service. The initial implementation can be a single FastAPI application containing separate Python modules.

## 5.2 Frontend

### Technology

- React
- Vite
- TypeScript
- Monaco Editor or an equivalent code editor
- A diff-view component or a dedicated Monaco diff editor
- Fetch or Axios for API communication

### Responsibilities

The frontend is responsible for collecting source code, displaying diagnostics, requesting corrections, and managing the user's review workflow.

It should not be responsible for deciding whether an AI-generated correction is syntactically valid. That decision belongs to the backend.

### Main Interface Components

**A. Source Code Editor**

The editor allows users to enter, paste, and modify C source code.

It should support:

- C syntax highlighting
- Line numbers
- Readable indentation
- A clear-code or reset action
- Displaying diagnostic markers where practical
- A reasonable source-code size limit

**B. Detect Errors Button**

When selected, this button sends the current source code to the backend for deterministic analysis.

The interface displays:

- Total detected diagnostics
- Error category
- Line and column
- Short error message
- Diagnostic details where available

**C. Auto Correct Button**

This button requests correction proposals based on the current source code and its diagnostics.

It should be disabled when the source is empty, a request is already running, or the current version has no eligible correction request under the implemented policy.

**D. Diagnostics Panel**

The diagnostics panel displays the detected errors in an organized list.

Selecting an error should navigate to or highlight the corresponding source location when possible.

**E. Correction Review Panel**

Each correction proposal should contain:

- A short description
- The relevant diagnostic
- The original source fragment
- The proposed replacement
- Validation status
- Accept and Reject actions

**F. Diff Viewer**

The diff viewer displays the original and proposed versions of the relevant code.

A GitHub-style convention can be used:

- Red highlighting indicates removed or replaced text.
- Green highlighting indicates inserted or replacement text.
- Unchanged code remains visually neutral.

The diff must be based on the actual source change, not merely on a description generated by the LLM.

**G. Final Working Code**

Accepted corrections update the current working copy. Rejected corrections do not alter the working code.

The original input should remain recoverable within the current session.

## 5.3 Backend

### Technology

- Python
- FastAPI
- Pydantic for request and response validation
- Pytest for automated tests
- CrewAI for agent orchestration
- Gemini API for LLM-based correction suggestions

### Responsibilities

The backend acts as the central control layer.

It must:

1. Validate incoming requests.
2. Invoke the compiler-analysis engine.
3. Convert parser findings into structured diagnostics.
4. Prepare relevant context for the correction agent.
5. Execute the correction workflow.
6. Validate candidate edits independently.
7. Re-run compiler analysis on candidate source code.
8. Return correction proposals and their validation status.
9. Apply only explicitly approved and still-applicable proposals.
10. Handle timeouts, malformed AI responses, and API failures.

The backend must not trust an agent's statement that a candidate is valid. It must perform the relevant checks itself.

---

# 6. Compiler-Analysis Engine

## 6.1 Purpose

The compiler-analysis engine is the deterministic foundation of the project.

It analyzes the source code using explicit lexical and syntactic rules instead of relying on an LLM to identify errors.

This component is essential because it provides repeatable diagnostics, source locations, and an independent method of validating proposed corrections.

The engine should be developed and tested before integrating the AI component.

## 6.2 Lexical Analysis

Lexical analysis is the first stage of source-code analysis.

The lexer reads the source code character by character and groups characters into tokens.

Examples of tokens include:

| Source text | Token category |
|---|---|
| `int` | Keyword |
| `main` | Identifier |
| `42` | Integer literal |
| `3.14` | Floating-point literal |
| `+` | Arithmetic operator |
| `=` | Assignment operator |
| `;` | Statement terminator |
| `(` and `)` | Parentheses |
| `{` and `}` | Braces |
| `#include` | Preprocessor-related syntax, according to the implemented lexer design |

Each token should store useful metadata, such as its type, original text, starting line, starting column, and source offsets.

The lexer should also recognize comments and string or character literals correctly. For example, a semicolon inside a string literal must not be treated as a statement terminator.

### Lexer Error Examples

- Invalid or unsupported characters
- Unterminated string literals
- Unterminated character literals
- Unterminated block comments
- Malformed numeric literals, where covered by the lexer rules

The lexer must distinguish an actual lexical error from a construct that is simply outside the currently implemented language subset.

## 6.3 Syntax Analysis

Syntax analysis checks whether the token sequence follows the supported grammar of C.

The parser uses grammar productions to recognize constructs such as:

- Variable declarations
- Expressions
- Assignments
- Function definitions
- Function calls
- Compound statements
- Conditional statements
- Loops
- Return statements
- Supported array and pointer declarations, as the grammar expands

For example, a simplified grammar might contain rules such as:

```text
program         -> external_declaration*

function        -> type identifier "(" parameters ")" compound_statement

compound_statement
                -> "{" statement* "}"

declaration     -> type identifier initializer? ";"

if_statement    -> "if" "(" expression ")" statement
                   ("else" statement)?

return_statement
                -> "return" expression? ";"
```

These productions are illustrative, not a complete C grammar. The actual grammar must be specified and implemented consistently with the supported subset.

A parser should use a documented parsing strategy, such as recursive descent, where appropriate for the chosen grammar.

## 6.4 Syntax Error Detection

The parser identifies violations of the implemented grammar.

Examples include:

**Missing semicolon**

```c
int x = 10
printf("%d", x);
```

**Unmatched parenthesis**

```c
if (x > 5 {
    printf("Large");
}
```

**Missing opening brace**

```c
int main()
    printf("Hello");
    return 0;
}
```

**Malformed function declaration**

```c
int add(int a, int b {
    return a + b;
}
```

The parser should report the relevant location and a concise diagnostic message. It should avoid claiming that a specific correction is certain when multiple interpretations are possible.

## 6.5 Diagnostic Structure

Each diagnostic should follow a defined schema.

For example:

```json
{
  "code": "SYN_MISSING_SEMICOLON",
  "category": "syntax",
  "severity": "error",
  "message": "Expected ';' after declaration.",
  "line": 4,
  "column": 15,
  "start_offset": 47,
  "end_offset": 47,
  "source_excerpt": "int a = 10",
  "recoverable": true
}
```

The values above are illustrative.

The actual implementation should define consistent rules for source offsets, line and column numbering, and insertion ranges. In particular, a missing-token diagnostic may use a zero-width range to identify where a token is expected.

The diagnostic schema should also distinguish lexical errors, syntax errors, unsupported constructs, and internal analysis failures.

## 6.6 Error Recovery

Stopping at the first syntax error would make the application less useful for programs containing multiple mistakes.

Therefore, the parser should implement a controlled recovery mechanism that attempts to continue analysis after a recoverable error.

Possible techniques include:

- Skipping tokens until a synchronization token is encountered.
- Synchronizing at semicolons or closing braces where appropriate.
- Recovering at statement boundaries.
- Tracking delimiter nesting.
- Reporting an error and continuing with the next plausible construct.

Recovery must be conservative. An incorrect recovery decision can generate misleading downstream errors.

The engine should distinguish primary errors from diagnostics that may have been caused by an earlier unresolved error when that relationship can be established.

## 6.7 Compiler-Based Validation

After a correction candidate is applied to a copy of the source code, the compiler-analysis engine should run again.

The backend should compare the diagnostics before and after the edit.

A candidate is more suitable for presentation when:

- The edit is structurally valid.
- The parser can analyze the relevant source.
- The original targeted error is resolved.
- The candidate does not introduce additional syntax errors under the supported grammar.
- The change is limited to the intended source region.
- The correction has not altered unrelated source text.

A candidate should not automatically be considered valid merely because the total number of diagnostics decreases. One error could disappear while a new error is introduced elsewhere.

The validator should compare diagnostic identities, locations, and relevant surrounding context as far as the implementation permits.

**Important limitation:** Passing the project's parser does not prove that a program is semantically correct, compiles with every C compiler, or produces the intended output. It only establishes that the candidate passes the checks actually implemented.

---

# 7. AI-Assisted Correction Engine

## 7.1 Purpose

The AI-assisted correction engine generates plausible repairs for errors detected by the compiler-analysis engine.

The AI component is intended to handle contextual reasoning, such as determining which missing delimiter is most likely intended or identifying a likely replacement for an incorrectly written token.

The AI component does not replace the lexer, parser, or validator.

## 7.2 Why Use Gemini?

Gemini is selected as the LLM for the proposed implementation because it is the model family the project intends to integrate.

The model can be prompted to analyze a structured diagnostic, examine the relevant source context, and return a proposed edit in a predefined format.

The exact Gemini model, API availability, quota, and integration method must be verified during implementation. Access to the Gemini chat interface does not automatically mean that API access or a particular free quota is available.

The application should handle missing API credentials, rate limits, timeouts, and unavailable models gracefully.

## 7.3 Why Use CrewAI?

CrewAI is used to organize the correction workflow around a single agent with a defined role, goal, and tools.

A direct Gemini API call could also receive role and goal instructions. The main reason for using CrewAI is not that an agent is automatically more intelligent. The benefit is the ability to organize the correction task and provide explicitly defined tools through which the agent can inspect diagnostics and request validation.

The proposed initial design uses **one correction agent**, not a multi-agent system.

### Agent Role

C Syntax Correction Specialist

### Agent Goal

Propose minimal, context-aware corrections for supported C lexical and syntax errors while preserving unrelated source code and returning structured edit proposals.

### Agent Responsibilities

- Read structured compiler diagnostics.
- Inspect the relevant source-code context.
- Determine plausible corrections.
- Prefer the smallest reasonable source change.
- Explain the intended correction briefly.
- Use available tools when additional diagnostic information or candidate validation is required.
- Return correction proposals in the specified schema.
- Avoid claiming that a candidate is valid unless the backend validation result supports that claim.

### Agent Restrictions

The agent must not:

- Replace the entire source file when a local edit is sufficient.
- Claim to have executed a compiler unless an actual validation tool did so.
- Override the backend's validation result.
- Apply a correction without user approval.
- Change unrelated valid code intentionally.
- Invent source offsets.
- Return an edit that does not match the supplied source version.
- Treat unsupported language features as confirmed syntax errors without adequate evidence.

## 7.4 Agent Tools

The agent should be provided with a small set of narrowly defined tools.

### Tool 1: Get Syntax Diagnostics

Purpose: Retrieve deterministic diagnostics for the current source version.

Input may include a source version identifier or a reference to the current analysis.

Output should contain structured diagnostics and relevant parser context.

The agent should not need to independently reinterpret the entire source file if the parser has already provided precise diagnostic information.

### Tool 2: Inspect Source Context

Purpose: Retrieve the relevant lines and token information surrounding a diagnostic.

This tool can limit the amount of source code sent to the model and make the relevant location easier to understand.

The backend should enforce source-size and context-size limits.

### Tool 3: Validate Candidate Correction

Purpose: Request validation of a proposed edit against the current source version.

The tool should:

1. Validate the edit schema.
2. Check the source offsets and expected original text.
3. Apply the edit to a separate candidate copy.
4. Run the compiler-analysis engine.
5. Compare the candidate's diagnostics with the original diagnostics.
6. Return the validation outcome and any remaining diagnostics.

The tool should not approve the edit for the user. It only returns validation information.

The backend must independently enforce validation and approval rules even if the agent calls the tool correctly.

## 7.5 Agent Workflow

The correction workflow can be summarized as follows:

```text
Input: Source code and structured diagnostics

1. Identify eligible syntax errors.
2. Retrieve relevant source context.
3. Ask the agent to propose a minimal edit.
4. Validate the returned edit schema.
5. Check source version and edit boundaries.
6. Apply the edit to a separate candidate copy.
7. Re-run compiler analysis.
8. Compare original and candidate diagnostics.
9. Reject unsafe or invalid candidates.
10. Return suitable proposals for user review.
```

The backend controls this sequence.

The agent may request tool operations, but it must not be the final authority on whether an edit is accepted by the validator.

## 7.6 Correction Proposal Format

The AI should return structured data rather than unrestricted prose containing an entire rewritten program.

An illustrative correction proposal is:

```json
{
  "proposal_id": "proposal_001",
  "diagnostic_code": "SYN_MISSING_SEMICOLON",
  "description": "Insert a semicolon after the variable declaration.",
  "edit": {
    "start_offset": 47,
    "end_offset": 47,
    "expected_text": "",
    "replacement_text": ";"
  },
  "reason": "The declaration is not terminated before the next statement."
}
```

This is an example of the desired structure, not a fixed source position.

The backend must verify that the offsets refer to the exact source version used to generate the proposal.

The final response returned to the frontend should additionally contain:

- A unique proposal identifier
- The diagnostic associated with the proposal
- The proposed replacement
- A validation status
- Remaining diagnostics, if relevant
- A brief validation explanation

## 7.7 Why Minimal Edits Matter

Suppose the source contains:

```c
int main() {
    int a = 10
    printf("%d\n", a);
    return 0;
}
```

A suitable correction is:

```c
int main() {
    int a = 10;
    printf("%d\n", a);
    return 0;
}
```

Only the missing semicolon is inserted.

The system should not rewrite the program into a different style, rename variables, replace `printf`, or restructure the function.

Minimal edits reduce the chance of introducing unrelated errors and make the proposed correction easier to understand.

## 7.8 Failure Handling

If the AI service is unavailable, the system should not pretend that AI-based correction succeeded.

The backend should:

- Preserve the original source code.
- Return an appropriate error or unavailable status.
- Allow deterministic error detection to continue.
- Avoid accepting incomplete or malformed AI responses.
- Support retrying the correction request where appropriate.
- Record useful technical logs without exposing API credentials.

Some simple corrections may eventually be handled by a deterministic repair rule without invoking the LLM. Such rules should be implemented explicitly and tested rather than silently presented as AI-generated reasoning.

---

# 8. Correction Validation and User Approval

## 8.1 Why Validation Is Necessary

LLMs can generate plausible-looking but incorrect source code. Even a correction that looks reasonable may introduce another syntax error or modify a different part of the program.

For this reason, the system separates three operations:

1. **Suggestion:** The agent proposes an edit.
2. **Validation:** The backend checks the candidate source.
3. **Approval:** The user decides whether to apply the validated proposal.

These operations must not be merged into one automatic action.

## 8.2 Validation Rules

Each candidate should undergo the following checks:

1. The response matches the expected schema.
2. The proposal refers to a known diagnostic or explicitly justified repair.
3. The source version has not changed since the proposal was generated.
4. The edit range is within the source boundaries.
5. The original text at the edit range matches the expected text.
6. The edit does not overlap another pending edit in an unsafe way.
7. The resulting candidate can be analyzed by the implemented lexer and parser.
8. The target diagnostic is resolved or the outcome is clearly classified.
9. No new syntax errors are introduced under the configured validation policy.
10. The change is limited to the intended scope as far as the validator can establish.

A candidate that fails an essential check must not be labelled as validated.

## 8.3 Source Versioning and Stale Proposals

A user may edit the source code after requesting corrections. The original edit offsets may then point to the wrong text.

To avoid this problem, every correction request should be associated with a source version or source fingerprint.

Before applying a proposal, the backend must confirm that it still refers to the correct source version and that the expected original text is present.

If the source has changed, the application should ask the user to re-run detection or regenerate the correction rather than applying a stale edit.

## 8.4 Individual Approval

The user must approve or reject each correction independently.

For example, if three proposals are available, the interface may display:

- Proposal 1: Insert a missing semicolon.
- Proposal 2: Add a missing closing parenthesis.
- Proposal 3: Correct a malformed declaration.

Each proposal should have separate Accept and Reject actions.

Accepting Proposal 1 must not automatically accept Proposals 2 and 3.

The backend should apply an accepted proposal only after rechecking that it is still applicable. Rejected proposals must not alter the source.

The UI may optionally support accepting all proposals in a later version, but this must be a deliberate additional feature and must not replace individual review.

## 8.5 Preserving the Original Program

The original input must remain unchanged while correction proposals are being generated and reviewed.

The system should maintain distinct representations of:

- Original source
- Current working source
- Proposed candidate source
- Accepted edits
- Rejected proposals

The backend should never treat an unreviewed AI response as the user's accepted program.

---

# 9. Functional Requirements

## FR-01: Source Code Input

The system shall allow the user to enter or paste C source code into an editor.

## FR-02: Syntax Analysis

The system shall analyze source code using the implemented lexer and parser.

## FR-03: Error Reporting

The system shall display supported lexical and syntax errors with relevant source locations and concise messages.

## FR-04: Multiple Error Detection

The system shall attempt to detect multiple errors in one source file using the implemented parser's error-recovery mechanism.

## FR-05: AI-Assisted Correction

The system shall request correction suggestions from the configured CrewAI agent and LLM when correction is available.

## FR-06: Structured Suggestions

The system shall represent each proposed correction as a structured edit rather than relying only on a rewritten source file.

## FR-07: Candidate Validation

The system shall validate each candidate edit independently before marking it as validated.

## FR-08: Diff Display

The system shall display the original and proposed source changes in a readable diff view.

## FR-09: Individual Approval

The system shall allow the user to accept or reject each proposal separately.

## FR-10: Source Preservation

The system shall preserve the original source while corrections remain unapproved.

## FR-11: Stale Proposal Protection

The system shall prevent the application of a correction when its source version or expected original text no longer matches.

## FR-12: Re-analysis

The system shall allow the user to analyze the updated working source after corrections are accepted.

## FR-13: Error Handling

The system shall handle invalid requests, unsupported constructs, malformed model output, and unavailable AI services gracefully.

## FR-14: Automated Testing

The system shall provide automated tests for compiler analysis, correction validation, API behavior, and essential frontend workflows.

## FR-15: Offline Testing

The system shall support ordinary automated tests without requiring a live Gemini API key.

---

# 10. Non-Functional Requirements

## 10.1 Reliability

Repeated analysis of the same source code under the same configuration should produce consistent deterministic diagnostics.

## 10.2 Safety

No AI-generated correction shall be applied automatically without explicit user approval.

## 10.3 Maintainability

The lexer, parser, correction engine, API, and frontend should be separated into understandable modules.

## 10.4 Usability

The interface should present short diagnostic messages, clear source locations, and understandable correction differences.

## 10.5 Performance

The system should handle reasonable source-code inputs without unnecessary processing or repeated LLM requests. Exact performance targets should be established through testing.

## 10.6 Security

- API keys must remain on the backend.
- Secrets must not be committed to version control.
- Source-code input must be subject to size and request limits.
- The backend must validate all incoming edit data.
- Logs must not expose secrets or unnecessarily retain user source code.
- The application must not execute arbitrary submitted C code merely to detect syntax errors.

## 10.7 Testability

Core compiler behavior must be testable independently of the frontend, CrewAI, and live Gemini API calls.

## 10.8 Transparency

The interface must distinguish detected errors, proposed corrections, and validated candidates. It must not imply that syntax validation proves full program correctness.

---

# 11. Technology Stack and Justification

| Component | Proposed technology | Reason |
|---|---|---|
| Frontend | React | Component-based user interface |
| Development server | Vite | Fast frontend development workflow |
| Language | TypeScript | Type checking and clearer data contracts |
| Code editor | Monaco Editor | Code editing, syntax highlighting, and diff support |
| Backend | Python | Suitable for compiler prototyping and AI integration |
| API framework | FastAPI | Request validation and API development |
| Request/response schemas | Pydantic | Structured input and output validation |
| Compiler engine | Custom lexer and parser | Deterministic detection based on implemented rules |
| AI orchestration | CrewAI | Organizes the single correction agent and its tools |
| LLM | Gemini API | Context-aware correction suggestions |
| Testing | Pytest | Backend and compiler unit/integration tests |
| Frontend testing | Vitest and a suitable React testing library | UI behavior and component testing |
| API testing | FastAPI test client | Endpoint and request/response tests |
| Version control | Git | Tracking changes and collaboration |

A database is not required for the initial version. Source code, diagnostics, and correction proposals can remain in application memory during the user's session.

Persistent accounts, saved projects, and correction history may be added later if the project requires them.

---

# 12. System API Design

The following endpoints are proposed for the initial implementation.

## 12.1 Detect Errors

**Endpoint:** `POST /api/analyze`

Purpose: Analyze source code and return diagnostics.

Example request:

```json
{
  "source_code": "#include <stdio.h>\nint main() { int x = 10 return 0; }"
}
```

Example response:

```json
{
  "analysis_id": "analysis_example",
  "status": "completed",
  "diagnostics": [
    {
      "code": "SYN_MISSING_SEMICOLON",
      "category": "syntax",
      "severity": "error",
      "message": "Expected ';' after declaration.",
      "line": 2,
      "column": 23
    }
  ]
}
```

The source and diagnostic positions are illustrative. Actual positions must be computed by the parser.

## 12.2 Request Correction Suggestions

**Endpoint:** `POST /api/corrections`

Purpose: Request correction proposals for a source version and its diagnostics.

Example request:

```json
{
  "source_code": "int main() { int x = 10 return 0; }",
  "diagnostic_codes": [
    "SYN_MISSING_SEMICOLON"
  ],
  "source_version": "version_example"
}
```

The backend should perform its own analysis rather than trusting diagnostic information supplied by the client.

The response should contain structured proposals and their validation status.

## 12.3 Validate a Candidate

**Endpoint:** `POST /api/corrections/validate`

Purpose: Validate a proposed edit against a particular source version.

This endpoint may initially be an internal backend operation or an explicit API endpoint, depending on how the CrewAI tool workflow is implemented.

## 12.4 Apply an Approved Correction

**Endpoint:** `POST /api/corrections/{proposal_id}/apply`

Purpose: Apply one explicitly approved proposal if it is still valid for the current source version.

Example request:

```json
{
  "source_version": "version_example",
  "approved": true
}
```

The backend must verify the proposal, source version, and edit range before returning the updated working source.

A rejected proposal must not be applied.

## 12.5 API Design Principles

- Use defined request and response schemas.
- Return appropriate HTTP status codes.
- Reject malformed requests.
- Limit source-code size.
- Avoid accepting arbitrary file paths or shell commands from clients.
- Treat all client-supplied offsets and proposal identifiers as untrusted.
- Never expose Gemini credentials to the frontend.
- Return concise error messages without leaking stack traces or internal secrets.

---

# 13. Implementation Plan

The project will be implemented in three major phases.

## Phase 1: Deterministic Compiler Foundation

### Objective

Build a working backend that can tokenize C source code, parse the supported grammar, detect syntax errors, and return structured diagnostics.

### Tasks

1. Create the project repository and folder structure.
2. Set up Python and FastAPI.
3. Define token types and token metadata.
4. Implement lexical analysis.
5. Implement the initial C grammar.
6. Implement the parser.
7. Add syntax diagnostics with source locations.
8. Implement conservative syntax-error recovery.
9. Add the `/api/analyze` endpoint.
10. Create unit tests for tokens and grammar rules.
11. Create tests for invalid and valid source programs.
12. Document supported language constructs and known limitations.

### Deliverable

A working compiler-analysis backend that detects supported syntax errors without requiring an LLM.

### Completion Criteria

- The lexer produces correct tokens for supported examples.
- The parser accepts programs that conform to the implemented grammar.
- Supported invalid programs produce meaningful diagnostics.
- The API returns structured responses.
- Automated tests run without a Gemini API key.

## Phase 2: AI-Assisted Correction Engine

### Objective

Integrate one CrewAI agent with Gemini and validate its proposed edits using the compiler engine.

### Tasks

1. Set up CrewAI and the selected Gemini integration.
2. Configure API credentials through environment variables.
3. Define the agent's role, goal, and restrictions.
4. Define the correction task and structured output format.
5. Implement diagnostic-context preparation.
6. Implement source-context inspection.
7. Implement candidate-validation tools.
8. Validate edit ranges and source versions.
9. Re-run the parser on candidate source code.
10. Compare diagnostics before and after edits.
11. Reject unsafe or malformed proposals.
12. Return correction proposals with validation status.
13. Implement mock LLM responses for ordinary automated tests.
14. Add optional live API tests that run only when configured.

### Deliverable

A backend that can request AI-assisted correction suggestions and return independently validated proposals.

### Completion Criteria

- The agent returns structured correction proposals.
- Invalid output is rejected safely.
- Candidate validation is performed by the backend.
- Original source code remains unchanged during suggestion generation.
- Mocked tests run without live model access.
- Live API failure does not break deterministic error detection.

## Phase 3: Frontend and Full Integration

### Objective

Build the complete web interface and connect it to the backend.

### Tasks

1. Create the React, Vite, and TypeScript application.
2. Integrate the code editor.
3. Implement the Detect Errors action.
4. Display diagnostic messages and source locations.
5. Implement the Auto Correct action.
6. Display individual correction proposals.
7. Integrate the diff viewer.
8. Implement Accept and Reject actions.
9. Implement source-version and stale-proposal handling.
10. Preserve the original source code.
11. Add loading, empty, error, and success states.
12. Write frontend component tests.
13. Write integration tests for the full workflow.
14. Document installation and execution instructions.

### Deliverable

A working web application in which users can enter C code, detect supported errors, review validated correction suggestions, and approve changes individually.

### Completion Criteria

- The frontend communicates correctly with FastAPI.
- Diagnostics are displayed clearly.
- The diff reflects the actual proposed edit.
- Each proposal can be accepted or rejected independently.
- Stale corrections are not applied.
- The application handles unavailable AI services gracefully.
- The complete workflow passes the defined automated tests.

---

# 14. Testing Strategy

Testing is a core part of the project rather than a final activity.

## 14.1 Lexer Unit Tests

Test the lexer with:

- Keywords and identifiers
- Integer and floating-point literals
- Operators and delimiters
- String and character literals
- Single-line comments
- Multi-line comments
- Newlines and whitespace
- Unterminated strings and comments
- Invalid characters
- Line and column tracking

## 14.2 Parser Unit Tests

Test valid examples covering:

- Variable declarations
- Assignments and expressions
- Function declarations and definitions
- Function calls
- `if` and `else`
- `for` and `while`
- `return`
- Compound statements
- Nested blocks
- Other constructs as the grammar expands

For each supported construct, include both valid and invalid examples.

## 14.3 Error-Recovery Tests

Test programs containing:

- A single missing semicolon
- An unmatched parenthesis
- A missing brace
- Multiple independent syntax errors
- An early error followed by valid statements
- Malformed constructs that should stop or limit recovery

The objective is to verify not only that errors are detected, but also that recovery does not produce an excessive number of misleading diagnostics.

## 14.4 Correction Engine Tests

Use predetermined mock responses to test:

- A correct minimal edit
- Malformed JSON or structured output
- Missing required fields
- Out-of-range source offsets
- A mismatched expected source fragment
- A candidate that still contains the original error
- A candidate that introduces a new syntax error
- An unnecessary rewrite of valid code
- An unavailable AI service
- A stale proposal generated for an older source version

## 14.5 Frontend Tests

Test:

- Entering source code
- Running error detection
- Displaying diagnostics
- Requesting correction suggestions
- Displaying the diff
- Accepting a correction
- Rejecting a correction
- Accepting one proposal without accepting others
- Handling backend failures
- Preventing stale proposals from being applied

## 14.6 Integration Tests

Test the complete workflow:

1. Submit invalid C code.
2. Receive diagnostics.
3. Request a correction.
4. Generate a candidate using a mocked AI response.
5. Validate the candidate.
6. Display the correction.
7. Accept the proposal.
8. Verify the updated source.
9. Run analysis again.
10. Confirm that the targeted syntax error is resolved.

Also test the rejection workflow and ensure that rejecting a correction preserves the current source.

## 14.7 Testing Without a Live LLM

Ordinary tests must not depend on Gemini API availability.

The correction service should allow its model interaction to be replaced with a fake or mocked implementation.

This enables predictable testing of validation, API contracts, source editing, and approval behavior.

Live Gemini tests should be optional, separately configured, and excluded from the normal test suite unless the required credentials are available.

---

# 15. Evaluation Metrics

The system should be evaluated using measurable criteria rather than relying only on a successful demonstration.

## 15.1 Detection Accuracy

Measure the proportion of known, supported syntax errors that the engine correctly identifies in a test corpus.

## 15.2 Diagnostic Quality

Evaluate whether reported locations and messages correspond to the actual error and whether recovery produces excessive false diagnostics.

## 15.3 Correction Success Rate

Measure the proportion of eligible correction requests for which the system produces a validated candidate that resolves the targeted syntax error.

## 15.4 Validation Rejection Rate

Measure how often the validator rejects candidates that fail the defined checks. Review representative cases to determine whether the validation rules are useful.

## 15.5 Unintended Change Rate

Measure how often proposed corrections modify source text outside the intended correction region.

## 15.6 User Review Usability

Assess whether users can identify the problem, understand the proposed change, and accept or reject it through the interface.

## 15.7 Response Time

Measure deterministic analysis time separately from AI-assisted correction time.

## 15.8 Test Coverage

Track coverage for the lexer, parser, diagnostics, candidate validator, API endpoints, and important frontend workflows.

Evaluation should clearly distinguish between results obtained on the supported grammar and claims about the full C language.

---

# 16. Scope of the Project

## 16.1 Included in the Initial Scope

- C source-code input through a web editor
- Lexical analysis for the implemented token set
- Syntax analysis using a documented grammar
- Structured lexical and syntax diagnostics
- Source-location reporting
- Basic error recovery
- AI-assisted correction suggestions
- One CrewAI agent
- Gemini API integration
- Structured edit proposals
- Backend validation of candidate corrections
- Original-versus-proposed code diff
- Individual correction approval
- Rejection of proposed corrections
- Automated backend and frontend tests
- Mocked LLM tests
- Documentation of supported features and limitations

## 16.2 Outside the Initial Scope

The initial version does not promise:

- Complete support for every construct in the C standard
- Guaranteed correction of every syntax error
- Guaranteed identification of the programmer's intended logic
- Automatic correction of semantic errors
- Proof of runtime correctness
- Guaranteed preservation of program behavior for every accepted edit
- Automatic program optimization
- Automatic code execution in the browser
- Multi-language support
- User accounts or persistent project storage
- A multi-agent AI architecture
- Fully autonomous correction without user approval

These features may be considered later if the initial system is stable.

## 16.3 Supported Language Subset

The exact subset of C must be determined and documented during Phase 1.

The implementation should expand incrementally, starting with basic declarations, expressions, function definitions, and common control structures.

Preprocessor directives, complex declarators, advanced pointer syntax, structures, unions, enumerations, typedefs, and other more complex language features should be added only when the corresponding lexical and grammatical behavior has been implemented and tested.

The system should report unsupported or unrecognized constructs appropriately instead of claiming that every such construct is necessarily a syntax error.

---

# 17. Risks and Mitigation

## Risk 1: Incomplete C Grammar

**Problem:** Implementing a complete C grammar is a substantial task.

**Mitigation:** Begin with a documented subset, implement grammar rules incrementally, and maintain positive and negative tests for each supported construct.

## Risk 2: Cascading Diagnostics

**Problem:** One syntax error may produce misleading errors later in the file.

**Mitigation:** Implement conservative parser recovery, track synchronization points, and test multiple-error examples.

## Risk 3: Incorrect AI Corrections

**Problem:** The agent may suggest a syntactically incorrect or unnecessary edit.

**Mitigation:** Require structured output, validate every candidate independently, and retain user approval.

## Risk 4: Unintended Source Modifications

**Problem:** An AI-generated replacement may alter unrelated code.

**Mitigation:** Use minimal edits, expected-text checks, source-version tracking, and diff-based review.

## Risk 5: API Availability or Quota Limits

**Problem:** The configured Gemini API may be unavailable or restricted.

**Mitigation:** Keep the compiler engine independent of the LLM, handle failures gracefully, and mock model responses during ordinary testing.

## Risk 6: CrewAI Adds Unnecessary Complexity

**Problem:** A single LLM request does not inherently require an orchestration framework.

**Mitigation:** Use CrewAI for its defined agent-and-tool workflow. Keep the agent count to one and avoid unnecessary agent delegation or repeated model calls.

## Risk 7: False Confidence from Validation

**Problem:** Passing the implemented parser may be mistaken for proof of full C correctness.

**Mitigation:** Label the result accurately as validation against the supported grammar. Keep syntax validation separate from semantic and runtime validation.

## Risk 8: Unsafe Code Execution

**Problem:** Running arbitrary submitted programs could expose the development environment to harmful code.

**Mitigation:** Do not execute user-submitted programs merely to detect syntax errors. If compiler-based validation is added later, use a carefully controlled execution environment with suitable restrictions.

---

# 18. Expected Outcomes

At the end of the project, the expected outcome is a functional web application demonstrating how compiler design and AI-assisted reasoning can work together.

The system is expected to:

1. Accept C source code through a browser-based editor.
2. Detect supported lexical and syntax errors using deterministic analysis.
3. Display concise diagnostics with source locations.
4. Use a CrewAI agent and Gemini to propose context-aware repairs.
5. Validate candidate edits independently using the backend.
6. Present suitable corrections through a readable diff interface.
7. Allow users to accept or reject each correction individually.
8. Preserve original source code until changes are approved.
9. Prevent stale or malformed edits from being applied.
10. Support automated testing without a live AI API.
11. Demonstrate the practical use of lexical analysis, parsing, error recovery, structured diagnostics, AI integration, and validation.
12. Provide a foundation for future improvements in grammar coverage and correction quality.

The project should demonstrate measurable performance on a documented test corpus rather than claim perfect accuracy or complete support for C.

---

# 19. Future Enhancements

The following features may be considered after the initial version is complete:

- Broader C grammar coverage
- Improved syntax-error recovery
- Deterministic rules for common, unambiguous corrections
- Better handling of misspelled C keywords
- Optional validation using a real C compiler
- Additional semantic checks
- User-configurable correction preferences
- Correction history and undo/redo
- Persistent projects and user accounts
- Exporting corrected source code
- Support for additional programming languages
- Expanded evaluation datasets
- More detailed explanations of compiler diagnostics
- Accessibility and interface improvements

Any new feature should preserve the separation between correction suggestions, independent validation, and user approval.

---

# 20. Conclusion

The proposed project, **Intelligent Syntax Error Detection and Automatic Correction Using Compiler Techniques**, aims to improve the process of identifying and repairing syntax errors in C programs by combining traditional compiler design techniques with AI-assisted correction.

The compiler-analysis engine provides a deterministic foundation for lexical analysis, syntax analysis, structured diagnostics, and candidate validation. A single CrewAI agent integrated with Gemini proposes context-aware corrections using the diagnostic information and relevant source-code context.

The backend independently checks the proposed edits before presenting them to the user. The frontend provides an interactive editing environment, a clear comparison between original and proposed code, and individual approval controls.

The system is designed to reduce the effort involved in understanding and correcting common syntax errors without surrendering control of the source code to an AI model.

The central principle of the project is that **AI proposes the correction, compiler-based analysis evaluates it, and the user decides whether to apply it**.

By following this approach, the project demonstrates a practical integration of compiler design, Python backend development, AI orchestration, API engineering, and interactive frontend development while maintaining clear boundaries around correctness, safety, and supported language features.
