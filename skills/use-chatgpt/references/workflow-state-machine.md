# Universal Workflow State Machine

Every engineering mission passes through an 8-stage lifecycle. Tasks only traverse the stages they actually need, but gates cannot be bypassed without justification.

---

## 1. The 8 Stages

```text
[STAGE 0: CLASSIFY]
    │
    ▼
[STAGE 1: RESTORE]
    │
    ▼
[STAGE 2: INVESTIGATE]
    │
    ▼
[STAGE 3: PLAN]
    │
    ▼
[STAGE 4: EXECUTE]
    │
    ▼
[STAGE 5: VERIFY]
    │
    ▼
[STAGE 6: REVIEW]
    │
    ▼
[STAGE 7: RELEASE / CLOSE]
    │
    ▼
[STAGE 8: HANDOFF]
```

### Stage Details:
- **STAGE 0: CLASSIFY**: Identify domain, current phase, source of truth, write surfaces, risk profile, and completion criteria.
- **STAGE 1: RESTORE**: Fetch live repository state, branches, open PRs, bot comments, and reconcile prior handoff context.
- **STAGE 2: INVESTIGATE**: Collect the minimal evidence needed to resolve architectural or functional unknowns.
- **STAGE 3: PLAN**: Define smallest complete scope, dependencies, acceptance criteria, test plan, and rollback strategy.
- **STAGE 4: EXECUTE**: Implement the change under the designated single write owner.
- **STAGE 5: VERIFY**: Execute targeted tests, regression checks, compiler/build checks, and runtime inspections (Levels A & B).
- **STAGE 6: REVIEW**: Conduct independent AI review (CodeRabbit), security checks, and static analysis (Level C).
- **STAGE 7: RELEASE / CLOSE**: Verify exact-head SHA, pass required repository CI checks, and trigger merge/deploy.
- **STAGE 8: HANDOFF**: Record durable project decisions and state if unfinished work remains for subsequent sessions.

---

## 2. Skipped Stage Policy

Do not force trivial tasks through all 8 stages. The risk profile governs stage necessity:

| Task Type | Required Stages | Justification for Skipped Stages |
| :--- | :--- | :--- |
| **Documentation / Copy Edit** | `CLASSIFY` $\rightarrow$ `EXECUTE` $\rightarrow$ `REVIEW` | No runtime logic, build steps, or external services affected. |
| **Simple Bugfix** | `RESTORE` $\rightarrow$ `INVESTIGATE` $\rightarrow$ `EXECUTE` $\rightarrow$ `VERIFY` $\rightarrow$ `RELEASE` | Formal planning stage skipped in favor of direct reproduction and test-driven fix. |
| **Core Product Feature** | All 8 Stages | Complex dependencies require requirements brief, TDD, and full verification. |
| **Production Migration** | All 8 Stages + Rollback Plan | Critical trust boundaries and data integrity at stake. |

---

## 3. Transition Rules & Invariants

1. **Mutation Invalidates Verification**: If code is modified in `STAGE 6 (REVIEW)` to address a finding, the state machine **must** transition back to `STAGE 5 (VERIFY)` to re-run test suites.
2. **Bot Commits Invalidate Current Head**: Any commit authored by an automated bot (`autofix.ci`, Gitar) forces a transition back to `STAGE 1 (RESTORE)` to fetch the new head SHA.
3. **No Release Without Proof**: Transition to `STAGE 7 (RELEASE)` is blocked unless `STAGE 5 (VERIFY)` has passing Level A or B evidence recorded in the ledger.
