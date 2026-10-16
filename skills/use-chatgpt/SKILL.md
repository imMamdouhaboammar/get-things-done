---
name: use-chatgpt
description: Use when coordinating multiple plugins or tools, routing complex engineering missions, repairing PRs with bot review comments, executing macOS native automation, or enforcing evidence-based completion gates.
version: 1.0.0
pack: engineering
inputs:
  - task_description
  - repository_context
  - pr_context
requires:
  - active_workspace
produces:
  - routing_packet
  - execution_dag
  - evidence_ledger
  - final_verdict
gates:
  - verified_source_of_truth
  - single_write_owner
  - open_pr_bot_context_inspected
  - executable_proof_before_complete
fallback: fable-plan
mutatesWorkspace: true
parallelSafe: false
neural_links:
  precursors:
    - fable-discover
    - fable-research
  continuations:
    - fable-verify
    - fable-review
  lateral_peers:
    - omni-skill
    - superpowers
---

# Use ChatGPT: Master Agentic Router & Coordination Skill

A modular, evidence-grounded agentic skill and execution engine for orchestrating installed ChatGPT plugins, connected data sources, GitHub Apps/bots, and local CLIs as coordinated roles rather than a flat list of `@mentions`.

```text
right source of truth
+ right planner
+ right executor
+ right specialist
+ right reviewer
+ right runtime verification
+ explicit completion gate
```

---

## ⚡ Quick Start: Native Rust CLI Engine

This skill is powered by the native Pure Rust engine `chatgpt-skill` (located in `crates/use-chatgpt-engine`).

```bash
# 1. Automatically classify intent and generate execution DAG
chatgpt-skill route "Build user authentication feature and verify with Playwright"

# 2. Inspect and classify open PR bot comments (CodeRabbit, Bugbot, Sourcery)
chatgpt-skill bot-gate inspect --pr 42

# 3. Initialize or update evidence ledger
chatgpt-skill evidence init --mission "Auth implementation"
chatgpt-skill evidence record --source "src/auth.ts" --test "bun test auth"

# 4. Advance through the 8-stage lifecycle
chatgpt-skill state transition EXECUTE --proof "Tests added"

# 5. Bridge to macOS native CLI (notifications, clipboard, keychain)
chatgpt-skill macos notify --title "PR Gate" --message "Verification passed"
```

---

## 1. Operating Invariants

Every workflow must enforce these five rules:

1. **Verified Source of Truth First**: Always inspect live connected state (`@GitHub`, `@Remote Desktop Commander`, local filesystem, database) before reasoning from memory or stale handoffs.
2. **Single Primary & Write Owner**: Only one plugin/agent owns primary lifecycle direction. Exactly one write owner per mutable surface at any time.
3. **Evidence Trust Ladder**: Level A (Direct State) and Level B (Executable Proof) outweigh Level C (Independent Review), Level D (External Docs), and Level E (Inference). A reviewer cannot manufacture executable proof.
4. **Mandatory Open-PR Bot Context Gate**: For any open PR in scope, inspect all bot comments (`coderabbitai`, `cursor bugbot`, `autofix.ci`, `sourcery`, `mergify`). Classify each finding before acting:
   `BOT != NOISE, BOT != TRUTH`. Verify claims against current head SHA.
5. **No Fake Completions**: Distinguish `COMPLETE`, `COMPLETE_WITH_FOLLOWUPS`, `PARTIAL`, `BLOCKED`, and `NOT_STARTED`. Never use vague completion language ("should work", "looks done") without physical verification.

---

## 2. Capability Precedence Algorithm

When multiple plugins or CLIs could assist, route through strict precedence:

$$\text{Source} \rightarrow \text{Contract} \rightarrow \text{Executor} \rightarrow \text{Verifier} \rightarrow \text{Reviewer} \rightarrow \text{Readiness} \rightarrow \text{Landing} \rightarrow \text{Handoff}$$

1. **Source**: Who owns current truth? (`@GitHub`, local repo, `@Supabase`, `@Vercel`)
2. **Contract**: Which specification or docs define behavior? (`@Context7`, `@OpenAI Developers`)
3. **Executor**: Who is authorized to mutate? (`@Remote Desktop Commander`, `@GitHub`, single write owner)
4. **Verifier**: What directly proves the change? (Native tests, CI, runtime checks)
5. **Reviewer**: Who provides an independent second perspective? (`@CodeRabbit`, `@Codex Engineering Guardrails`)
6. **Readiness**: Is evidence sufficient for the next gate? (`@PR Readiness Check`)
7. **Landing**: Who owns the irreversible state transition? (`@PR Completion`, Mergify, repository policy)
8. **Handoff**: What state must survive if work remains? (`@Create State`, `@get-fable handoff`)

---

## 3. Capability Availability States

Every tool is classified into one of six runtime states:
- `CALLABLE`: Usable tool contract visible in the current host session.
- `CONNECTED`: Live connector accessible for current account.
- `INSTALLED_BUT_NOT_CALLABLE_HERE`: Plugin installed in ChatGPT/Codex, but inactive in current session.
- `KNOWN_NAME_UNRESOLVED`: Name referenced in prompt, but no canonical contract resolved.
- `UNAVAILABLE`: Integration explicitly reports it cannot execute.
- `BLOCKED`: Constrained by rate limits, billing, auth, or policy.

*Rule: Never silently promote an uncallable or blocked tool into a functioning one.*

---

## 4. Universal 8-Stage Lifecycle

```text
STAGE 0: CLASSIFY   -> Domain, source of truth, write surfaces, risk, gates
STAGE 1: RESTORE    -> Fetch live repo/PR/account state; reconcile handoff
STAGE 2: INVESTIGATE-> Collect minimal evidence to remove uncertainty
STAGE 3: PLAN       -> Bounded scope, acceptance criteria, tests, rollback
STAGE 4: EXECUTE    -> Implement slice under single write owner
STAGE 5: VERIFY     -> Run tests, builds, and runtime checks (Levels A & B)
STAGE 6: REVIEW     -> Independent code, security, and UX reviews (Level C)
STAGE 7: RELEASE    -> Exact-head landing, CI verification, merge queue
STAGE 8: HANDOFF    -> Persist durable state if unfinished work remains
```

---

## 5. Decision Rules & Boundaries

- **When to Use**:
  - Coordinating multiple ChatGPT plugins, skills, or CLIs on non-trivial engineering tasks.
  - Inspecting and repairing open PRs with bot/app review threads.
  - Multi-stage delivery requiring strict evidence ledgers and state machine tracking.
  - Cross-platform agentic missions (ChatGPT, Claude Code, Cursor, Antigravity).
- **When NOT to Use**:
  - Trivial single-file edits or simple syntax questions (use direct inline execution).
  - General web browsing or knowledge lookup with no tooling orchestration.
  - Building new skills from scratch (delegate to `skill-creator` or `omni-skill`).

---

## 6. Progressive Disclosure & Reference Map

Deep-dive operational knowledge is partitioned into domain references:

| Reference | Topic & Canonical Contents |
| :--- | :--- |
| **`references/operating-contract.md`** | Core invariants, trust boundaries, PR head refresh, and reporting vocabulary. |
| **`references/plugin-role-model.md`** | 10 role categories: Source, Research, Planning, Execution, Review, Security, QA, etc. |
| **`references/execution-surfaces.md`** | Surface taxonomy: Plugins vs Connected Sources vs GitHub Apps vs CI Gates. |
| **`references/open-pr-bot-gate.md`** | Deep rules for CodeRabbit, Bugbot, autofix.ci, Qlty, Sourcery, Mergify, and rate limits. |
| **`references/evidence-trust-ladder.md`** | Evidence levels A–E, proof precedence, and evidence ledger format. |
| **`references/capability-graph.md`** | Full routing matrix, availability state vocabulary, and unresolved names policy. |
| **`references/workflow-state-machine.md`** | Detailed state machine transitions, invariants, and skipped-stage policies. |
| **`references/agentic-recipes.md`** | Standard mission recipes: PR repair, feature build, bug debug, security audit, backlog audit. |
| **`references/prompt-contracts.md`** | Prompt contract standard, copy-ready autonomous prompt skeleton, master router. |

---

## 7. Artifact Templates

Standard machine-readable templates in `templates/`:
- `templates/routing-packet.yaml`: Machine-readable capability routing packet.
- `templates/evidence-ledger.md`: Evidence ledger Markdown block.
- `templates/prompt-contract.yaml`: Prompt contract standard.
- `templates/agentic-mission-skeleton.md`: Copy-ready autonomous prompt skeleton.

---

## 8. Verification & Completion Criteria

A task orchestrated under this skill is complete ONLY when:
1. All changes are verified by Level A (Direct State) or Level B (Executable Proof).
2. Open PR bot context is completely dispositioned and reflected in current head SHA.
3. Evidence ledger is fully recorded with zero unverified assumptions.
4. Final verdict is explicitly emitted as `COMPLETE` or `COMPLETE_WITH_FOLLOWUPS`.
