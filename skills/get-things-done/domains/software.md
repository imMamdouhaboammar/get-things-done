---
domain: software
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Software
## Selection signals
Software features, codebases, APIs, services, data models, architecture, migrations, bugs, infrastructure, deployment, security, performance, developer tooling, multi-plugin routing, PR repair bot triage (use-chatgpt)

Non-selection signal: Tasks that only mention technical objects while the requested outcome is research, marketing, design, operations, or another specialist decision rather than changing software behavior.
## Domain vocabulary
Keep distinct: requirement, behavior, interface, dependency, invariant, state, data, failure mode, test, deployment, migration, rollback, routing precedence, disposition (CURRENT_ACTIONABLE, STALE_AFTER_NEW_HEAD, ALREADY_FIXED), evidence trust ladder (Levels A through E)
## Diagnostic questions
Ask only when blocking: Who or what calls this? What observable behavior changes? Which interface must remain compatible? What state changes? What failure is unacceptable? What environment must run it? Is the review feedback actionable against current Git HEAD or stale? What evidence trust level (A-E) certifies this change?
## Extra brief fields
`repository`, `runtime`, `interfaces`, `data_state`, `compatibility`, `security`, `deployment`, `rollback`, `test_strategy`, `chatgpt_routing`, `bot_gate`, `evidence_grade`
## Readiness additions
- changed behavior is observable
- affected interfaces and compatibility expectations are known
- data or state impact is understood when relevant
- a verification seam exists
- open PR bot reviews are fenced via bot-gate (BOT != NOISE, BOT != TRUTH) with zero unclassified actionable blockers
- routing packet and execution DAG established for multi-capability tasks
## Workstream patterns
- behavior contract -> implementation -> integration -> verification
- migration: inventory -> transform -> compatibility -> verify -> cutover -> rollback
- architecture: boundaries -> interfaces -> data/state -> failure/security -> delivery sequence
- agentic execution (use-chatgpt): classify -> restore -> investigate -> plan -> execute -> verify (Level B) -> review (Level C) -> release
## Review additions
Check interface clarity, state transitions, backward compatibility, failure modes, security boundaries, operability, testability, and independent AI/human review dispositions
## Completion checks
Relevant tests pass with Level A deterministic machine proof (exit code 0, pytest, cargo test) or Level B integration proof, static checks pass, integration behavior is exercised, failure cases are checked, and deployment or rollback implications are explicit
## Common traps
Coding before behavior is defined, treating typecheck as full verification, unrelated refactors, mock-only verification, claiming production readiness without Level A/B deployment evidence, and blindly trusting or ignoring bot reviews without disposition fencing
