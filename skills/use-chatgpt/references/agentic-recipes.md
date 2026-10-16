# Agentic Mission Recipes

Default operational recipes for recurring engineering missions.

---

## 1. Continue a Long Existing Session

```text
PRIMARY OWNER: @get-fable or @Superpowers
SOURCE: @GitHub + local repo via @Remote Desktop Commander
PROCESS: @Superpowers
DOCS: @Context7 (only when version-specific contracts matter)
REVIEW: @CodeRabbit (after meaningful diff)
STATE: @Create State or @get-fable handoff

Sequence:
1. Inspect default branch, active branch, git status, open PRs, bot comments, and local uncommitted changes.
2. Restore latest project handoff.
3. Reconcile handoff claims with live state.
4. Construct a completion matrix: complete / in-progress / blocked / not-started.
5. Pick highest-value unfinished item that can safely progress.
6. Implement smallest complete slice.
7. Test changed behavior and regression paths.
8. Review final diff.
9. Persist durable handoff only if work remains unfinished.
```

---

## 2. Build a Product Feature End-to-End

```text
PRIMARY OWNER: @get-fable or @Riqor
SOURCE: @GitHub + local repository
REQUIREMENTS: @AI Task Brief Builder
PROCESS: @Superpowers (TDD & planning)
GUARDRAILS: @Codex Engineering Guardrails code-work
REVIEWER: @CodeRabbit
RUNTIME QA: @Testifly (when user-facing UI changes)
READINESS: @PR Readiness Check

Sequence:
1. Convert feature request into confirmed requirements, out-of-scope items, acceptance criteria, and tests.
2. Trace data, API, auth, and UI execution paths.
3. Add unit/integration tests before or alongside code.
4. Implement under single write owner.
5. Run targeted tests and regression checks.
6. Verify runtime UI/flow.
7. Perform CodeRabbit review on final diff.
8. Check PR readiness only after evidence is recorded.
```

---

## 3. Debug a Real Bug

```text
PRIMARY OWNER: @Superpowers
RUNTIME EVIDENCE: @Remote Desktop Commander / local terminal
SOURCE: @GitHub
DOCS: @Context7
ANALYSIS: @Fallow Code Analysis
REVIEWER: @CodeRabbit

Sequence:
1. Reproduce before editing; record actual vs expected behavior.
2. Capture relevant logs, stack traces, and database states.
3. Form ranked hypotheses; eliminate with evidence.
4. Identify root cause, not just visible symptom.
5. Add regression test that fails on the bug.
6. Apply smallest correct fix.
7. Re-run reproduction test until green.
8. Run nearby tests to confirm no regressions.
```

---

## 4. Existing PR Repair with Open-PR Bot Gate

```text
PRIMARY OWNER: @PR Completion (nominal) + @GitHub
EXECUTION: @Codex Engineering Guardrails code-work
BOT GATE: Inspect CodeRabbit, Bugbot, Sourcery, autofix.ci comments
REVIEW: @CodeRabbit incremental review

Sequence:
1. Inspect live PR conversation, inline review threads, and bot annotations.
2. Classify each bot comment (CURRENT_ACTIONABLE, STALE, FALSE_POSITIVE, etc.).
3. Verify claims against current head SHA.
4. Apply bounded code repair for verified issues.
5. Re-run affected unit/integration tests.
6. Push fixes to PR branch.
7. Refresh PR head SHA; resolve bot threads with evidence.
8. Verify all required CI checks pass.
```

---

## 5. Security-Sensitive Change

```text
POLICY: @ArmorCodex
SOURCE: @GitHub + local repository
IMPLEMENTATION: @Codex Engineering Guardrails code-work
SECURITY REVIEW: @Codex Security (fallback: @get-fable fable-security or @gstack cso)
STATIC ANALYSIS: @Fallow Code Analysis
GENERAL REVIEW: @CodeRabbit

Sequence:
1. Identify changed trust boundaries (auth, tokens, secrets, public inputs).
2. Register security policy and implementation constraints.
3. Implement minimal change; never expose credentials in code or logs.
4. Add security tests (auth bypass, permission check, input sanitization).
5. Run dedicated security review.
6. Run general code review only after security verification passes.
```
