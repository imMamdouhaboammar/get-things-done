# Open-PR Bot Context Gate

Autonomous workflows must treat GitHub Apps and bots as bounded actors inside the Pull Request lifecycle.

---

## 1. The Core Invariant

$$\text{BOT} \neq \text{NOISE} \quad \text{and} \quad \text{BOT} \neq \text{TRUTH}$$

- Useful automated context must **not** be ignored merely because it is automated.
- Existing bot feedback must be consumed before asking another bot to repeat the same review.
- Bot feedback is review evidence, **never** executable proof.

---

## 2. Mandatory PR Context Protocol

Whenever an open PR is in scope, perform this 6-step evaluation before planning, repair, readiness checks, or landing:

1. **Identify the author and app** (`coderabbitai`, `bugbot`, `sourcery`, etc.).
2. **Establish the referenced head SHA** to verify whether findings apply to current code.
3. **Classify each material comment/thread into a canonical disposition**:
   - `CURRENT_ACTIONABLE`: Valid issue on the current head commit that requires a code change.
   - `CURRENT_CONTEXT`: Useful architectural or behavioral context; no fix required.
   - `ALREADY_FIXED`: Resolved by a subsequent commit on the PR branch.
   - `STALE_AFTER_NEW_HEAD`: Rendered obsolete by branch updates or refactors.
   - `DUPLICATE`: Repeated issue already captured by another reviewer or check.
   - `FALSE_POSITIVE`: Incorrect claim refuted by executable tests or repository contracts.
   - `NEEDS_DECISION`: Requires architectural or product sign-off.
4. **Verify claims against current code and tests**.
5. **Fix only real in-scope issues** and re-verify.
6. **Refresh after every push or bot commit**: Any bot-authored commit (`autofix.ci`, Gitar) invalidates prior verification of the PR head SHA.

---

## 3. Specific GitHub App Profiles & Controls

### 3.1 CodeRabbit
Resolve handle from repository activity (`@coderabbitai` is standard default).
- `<CODERABBIT_HANDLE> review`: Incremental review of new changes.
- `<CODERABBIT_HANDLE> full review`: Fresh full review of the PR.
- `<CODERABBIT_HANDLE> pause` / `resume`: Control automatic reviews.
- `<CODERABBIT_HANDLE> resolve`: Top-level comment asking CodeRabbit to resolve addressed threads.
- `<CODERABBIT_HANDLE> approve`: Request approval (only submits approval if `request_changes_workflow` is enabled; otherwise resolves threads).

*Rule: Never blindly implement CodeRabbit prose without verifying current code.*

### 3.2 Cursor Bugbot
- `cursor review` / `bugbot run`: Trigger manual PR review.
- `cursor review verbose=true` / `bugbot run verbose=true`: Trigger with diagnostic details.
- Findings represent review evidence, not verified bugs.

### 3.3 autofix.ci
- Workflow-driven via GitHub Actions (`autofix.ci`).
- Runs deterministic fixers/formatters and commits patches to PR branch.
- Any bot-authored commit creates a new head SHA and invalidates previous test verification.

### 3.4 Sourcery
- `@sourcery-ai review`: Fresh review.
- `@sourcery-ai resolve`: Resolve addressed comments.
- `@sourcery-ai summary` / `guide`: Generate PR summaries.
- Do not request both Sourcery and CodeRabbit full reviews by default unless distinct perspectives are needed.

### 3.5 Qodo & Reviewer Availability Gates
- Qodo may report paused reviews due to trial or credit expiration.
- **Rule**: `availability: BLOCKED` (billing or rate limited) **is NOT** `PASS`.
- The absence of findings from a reviewer that did not run does not constitute a clean review pass.

### 3.6 Mergify
- `@mergifyio queue`: Request enrollment into merge queue.
- Mergify is a landing/queue surface, not an implementation or review tool.
- Exact-head confirmation contract applies before requesting merge queue enrollment.

---

## 4. Rate Limits & Unavailable States

```text
availability: BLOCKED
block_reason: review_rate_limited != PASS

availability: BLOCKED
block_reason: billing_blocked != PASS
```

- Do not spam review triggers when a service is rate-limited.
- Use already-valid current-head evidence and other distinct available reviewers.
- If a blocked reviewer is a required branch protection gate, the PR remains blocked until resolved.
