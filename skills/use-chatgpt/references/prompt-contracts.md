# Prompt Contract Standard & Master Router

For reusable prompts, autonomous Goals, and long-running repository missions, define an explicit contract before entering the execution loop.

---

## 1. Prompt Contract Standard

```yaml
outcome:
  # Observable finished state
  description: "User authentication implemented with OAuth2 and verified via unit & E2E tests."

success_criteria:
  - "Unit test coverage for auth module >= 90%"
  - "E2E login flow passes in Playwright"
  - "Zero high-severity security findings in CodeRabbit review"

source_of_truth:
  - "Local git repository and active branch"
  - "Supabase schema definitions"

boundaries:
  in_scope:
    - "Auth routes, JWT validation, user session cookies"
  out_of_scope:
    - "Billing tiers, password reset emails"

permissions:
  allowed:
    - "File reads and writes in src/auth/"
    - "Running test commands: bun test, cargo test"
  confirmation_required:
    - "Database migrations against production"
    - "Force-pushing git branches"

write_owner:
  "Codex Engineering Guardrails code-work"

tools:
  source: "@GitHub"
  planner: "@Superpowers"
  executor: "@Remote Desktop Commander"
  verifier: "bun test"
  reviewer: "@CodeRabbit"
  landing: "@PR Completion"

evidence_required:
  - "Clean test output from test runner"
  - "Diff inspection confirming zero secrets committed"

stop_conditions:
  - "COMPLETE: All criteria verified"
  - "BLOCKED: Missing OAuth client credentials"
  - "AUTHORITY_REQUIRED: Production deployment requested"
```

---

## 2. Master Router Prompt

Use this prompt when the optimal workflow or plugin stack is not known in advance:

```text
@Plugin Management @Superpowers

Use my installed plugin stack intelligently for the task below.

Task:
[TASK DESCRIPTION]

Context:
[INPUT MATERIAL]

Before doing work, classify:
1. Domain
2. Current stage in the 8-stage lifecycle
3. Source of truth (live repo, database, or docs)
4. Whether live connected data is required
5. Whether local terminal execution is required
6. Whether external research is required
7. Write surfaces and designated single write owner
8. Security risk and trust boundary changes
9. Runtime verification needs
10. Final completion gate

Then choose the smallest useful plugin stack using exact installed @Plugin Name syntax.
Assign explicit roles:
- Source
- Planner
- Executor
- Specialist
- Reviewer
- Security Gate
- Runtime QA
- Release Gate
- State/Handoff

Execute the task after routing. Maintain the evidence ledger and emit a completion verdict.
```
