# Example: End-to-End Feature Implementation

A walkthrough of implementing an authentication feature using the `use-chatgpt` skill and pure Rust engine.

---

## 1. Intent Classification & Routing

Prompt:
```text
Build OAuth2 login endpoint and Google provider in Rust backend with unit tests
```

Execution via CLI:
```bash
chatgpt-skill route "Build OAuth2 login endpoint and Google provider in Rust backend with unit tests"
```

Output:
```yaml
mission:
  title: "Build OAuth2 login endpoint and Google provider in Rust backend with unit tests"
  outcome: "OAuth2 authentication routes implemented, integrated with Google provider, verified with unit tests."
  current_stage: "PLAN"

source_of_truth:
  primary: "Local git repository"
  secondary: "@GitHub"

ownership:
  orchestrator: "@Superpowers"
  write_owner: "Codex Engineering Guardrails code-work"
  landing_owner: "@PR Completion"

specialists:
  - capability: "@Context7"
    reason: "Verify latest OAuth2 crate API conventions"
    entry_trigger: "Implementation of token exchange"
    expected_output: "Crate API snippets"
    continuation: "Implement handler"

verification:
  executable:
    - "cargo test --test auth_test"
    - "cargo check"

review:
  primary: "@CodeRabbit"
  optional_second_lens: "@Codex Security"
```

---

## 2. State Machine Transitions

```bash
chatgpt-skill state transition INVESTIGATE --proof "Inspected src/auth.rs and Cargo.toml"
chatgpt-skill state transition PLAN --proof "Created test-first plan for token verification"
chatgpt-skill state transition EXECUTE --proof "Implemented Google OAuth handler"
chatgpt-skill state transition VERIFY --proof "cargo test passed with 4 unit tests"
chatgpt-skill state transition REVIEW --proof "CodeRabbit review passed with 0 critical findings"
chatgpt-skill state transition RELEASE --proof "PR #12 merged to main"
```

---

## 3. Evidence Ledger

```markdown
### Evidence Ledger

- **Source of Truth Inspected**: `Cargo.toml`, `src/auth.rs`, `src/handlers.rs`
- **Changes Made**: Added `src/auth/oauth.rs`, updated routes in `src/main.rs`
- **Tests Executed**: `cargo test test_oauth_flow` (All 4 tests passed)
- **Runtime Checks**: Local curl to `http://localhost:8080/auth/login` returned 302 redirect to accounts.google.com
- **Review Evidence**: CodeRabbit incremental review clean; Codex Security confirmed CSRF state parameter verified
- **Open-PR Bot Context**: None (new local branch)
- **Known Limitations**: Apple and GitHub OAuth providers deferred to next sprint
- **Final Verdict**: `COMPLETE`
```
