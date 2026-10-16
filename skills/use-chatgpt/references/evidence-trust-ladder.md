# Evidence Trust Ladder & Ledger

All claims of completion or correctness must be backed by the highest available rung on the Evidence Trust Ladder.

---

## 1. The Evidence Trust Ladder

```text
LEVEL A: DIRECT CURRENT STATE
Live repository state, runtime database state, rendered browser UI, exact current artifact.
Verified via direct inspection of files, git status, live endpoints.

LEVEL B: EXECUTABLE PROOF
Focused unit/regression tests, integration tests, clean compiler/typecheck runs, 
linter passes, package validation, current-head CI workflow runs.
Verified via deterministic execution.

LEVEL C: INDEPENDENT REVIEW
Findings and summaries from CodeRabbit, Codex verification, Fallow static analysis, 
SonarQube, or security reviewers.
Improves confidence but CANNOT manufacture executable proof.

LEVEL D: EXTERNAL CONTRACT
Current primary documentation, official RFCs, framework specs, vendor API contracts.
Defines required external behavior but DOES NOT prove local compliance.

LEVEL E: CONTEXT / MEMORY / INFERENCE
Prior session notes, handoffs, agent memory, architectural hypotheses.
Valuable for initial orientation only; invalidated when contradicted by Level A or B.
```

---

## 2. Evidence Precedence Rules

1. **A Stronger Level Invalidates a Weaker Level**: A failing test (Level B) overrides ten reviewers saying the code looks clean (Level C).
2. **Completion Requires Levels A and/or B**: An issue or PR cannot be marked `COMPLETE` based on code inspection or reviewer sign-off alone.
3. **Reviewers Provide Confidence, Not Proof**: Reviewer count does not equal verification.
4. **Docs Define Contracts, Not Proof**: Quoting official docs (Level D) shows what should happen, not that the local code does it.

---

## 3. Standard Evidence Ledger Format

Every non-trivial engineering workflow must maintain an evidence ledger:

```markdown
### Evidence Ledger

- **Source of Truth Inspected**:
  [Exact files, branches, or database tables read]
- **Changes Made**:
  [Exact files modified, added, or removed]
- **Tests Executed**:
  [Specific commands and pass/fail outputs, e.g. `cargo test --test router`]
- **Runtime Checks**:
  [URLs hit, status codes, browser verification steps]
- **Review Evidence**:
  [CodeRabbit review summary, Fallow graph output, or security scan findings]
- **Open-PR Bot Context**:
  [Bot comments inspected, referenced SHAs, and their dispositions]
- **Known Limitations**:
  [Explicitly noted gaps, unverified edge cases, or non-blocking items]
- **Final Verdict**:
  [COMPLETE | COMPLETE_WITH_FOLLOWUPS | PARTIAL | BLOCKED | NOT_STARTED]
```
