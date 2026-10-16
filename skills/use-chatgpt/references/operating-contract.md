# Operating Contract

The canonical operating contract for coordinating agentic workflows, installed plugins, and external CLIs.

---

## 1. Core Operating Invariants

```text
Use listed @plugins and external CLIs when they are actually available and materially useful.

Do not claim that a plugin, skill, search, review, test, deployment, code change, file edit, commit, PR action, account action, migration, or external action happened unless it was actually executed.

If a named plugin is installed but its callable interface is not available in the current session:
1. Continue with the useful available stack.
2. Do not simulate its output.
3. State the missing capability only if it materially affects confidence or completion.
```

---

## 2. Source of Truth

Always identify the source of truth before taking any action:
- **Live Remote State**: `@GitHub` for issues, PRs, review comments, CI checks, remote branches.
- **Local Runtime State**: `@Remote Desktop Commander` or local terminal/filesystem for current worktree, active files, uncommitted diffs, local test execution.
- **Backend & Cloud State**: `@Supabase` for schemas, SQL, RLS, functions; `@Vercel` for deployments and logs.
- **External Specifications**: Current primary documentation (e.g. via `@Context7` or vendor docs).

---

## 3. Mandatory Open-PR Bot Context Invariant

For any open Pull Request in scope:
- Inspect top-level PR conversation comments.
- Inspect review submissions and inline review threads (including resolved threads when they preserve useful history).
- Inspect GitHub App / bot-authored comments, summaries, annotations, and check output.
- Extract material context before planning, repairing, judging readiness, or landing.
- Verify every material bot claim against the current PR head SHA and live repository state before acting.
- Refresh bot/review context after every push or bot-authored commit.
- Never ignore feedback merely because it came from a bot (`BOT != NOISE`).
- Never trust feedback merely because it came from a bot (`BOT != TRUTH`).
- Consume useful existing bot output before triggering duplicate automated reviews.

---

## 4. Continuation & Implementation Discipline

### For Continuation Work:
- Inspect live state first.
- Reconcile previous handoffs with current reality.
- Never restart completed work from zero.
- Never duplicate existing implementation.
- Preserve user-authored uncommitted changes.

### For Implementation Work:
- Inspect before editing.
- Keep changes coherent, minimal, and reversible.
- Test the changed behavior directly.
- Test nearby regression risks.
- Review the final diff.
- Verify acceptance criteria using evidence.

### For Risky Work:
- Identify trust boundaries (auth, secrets, public/private APIs).
- Protect credentials, tokens, and production data.
- Avoid destructive operations unless explicitly authorized.
- Prefer staging or local non-production verification.

---

## 5. Reporting Vocabulary

When reporting status, always use one of five standard completion verdicts:

1. **`COMPLETE`**: All requested scope and required verification gates are physically verified with Level A or B evidence.
2. **`COMPLETE_WITH_FOLLOWUPS`**: Requested core scope is complete; remaining items are explicitly non-blocking and documented.
3. **`PARTIAL`**: Meaningful progress made, but one or more required completion gates remain unverified.
4. **`BLOCKED`**: A real external dependency, permission restriction, or billing limit prevents further safe progress.
5. **`NOT_STARTED`**: No execution occurred.

*Rule: Never use vague completion language ("should be done", "looks complete", "probably working") when stronger verification is possible.*
