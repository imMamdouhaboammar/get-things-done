---
domain: software
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Software
## Selection signals
Software features, codebases, APIs, services, data models, architecture, migrations, bugs, infrastructure, deployment, security, performance, developer tooling
## Domain vocabulary
Keep distinct: requirement, behavior, interface, dependency, invariant, state, data, failure mode, test, deployment, migration, rollback
## Diagnostic questions
Ask only when blocking: Who or what calls this? What observable behavior changes? Which interface must remain compatible? What state changes? What failure is unacceptable? What environment must run it?
## Extra brief fields
`repository`, `runtime`, `interfaces`, `data_state`, `compatibility`, `security`, `deployment`, `rollback`, `test_strategy`
## Readiness additions
- changed behavior is observable
- affected interfaces and compatibility expectations are known
- data or state impact is understood when relevant
- a verification seam exists
## Workstream patterns
- behavior contract -> implementation -> integration -> verification
- migration: inventory -> transform -> compatibility -> verify -> cutover -> rollback
- architecture: boundaries -> interfaces -> data/state -> failure/security -> delivery sequence
## Review additions
Check interface clarity, state transitions, backward compatibility, failure modes, security boundaries, operability, and testability
## Completion checks
Relevant tests pass, static checks pass when present, integration behavior is exercised, failure cases are checked, and deployment or rollback implications are explicit
## Common traps
Coding before behavior is defined, treating typecheck as full verification, unrelated refactors, mock-only verification, and claiming production readiness without deployment evidence
