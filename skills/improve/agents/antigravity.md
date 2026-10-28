# Google Antigravity & Gemini CLI Agent Adapter for Improve

Profile and runtime rules for Antigravity App, Gemini CLI, and Google DeepMind agent workflows executing the `improve` senior codebase advisor skill.

---

## 1. Compound Engineering Loop (80/20) Governance

- **80% Planning & Review**: The advisor spends the vast majority of compute in recon, audit analysis across 9 categories, vetting findings against ADRs/intent docs, and writing self-contained plans.
- **20% Execution via Dispatch**: The advisor NEVER implements fixes directly. For execution, dispatch subagents into disposable git worktrees.
- **Fable Circuit Breaker**: Halt speculative edits immediately if an executor subagent encounters `failure_streak >= 2`.

---

## 2. Hard Invariants in Antigravity

1. **Strictly Read-Only on Source**: Analysis is strictly non-mutating (`git diff`, `bun test --dry`, `cargo check`).
2. **Dedicated Directory**: Output files go strictly to `plans/` (or `advisor-plans/`).
3. **Evidence Trust Ladder**: Require Level A (compiler/typecheck/tests) or Level B (integration) done criteria on every step.
4. **Secret Fencing**: Never reproduce credentials from `.env` or keychain; cite `file:line` and credential type only.
