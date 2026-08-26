# Architecture

Get Things Done is split into a small universal core and optional domain packs

The core owns semantics that must remain stable across fields

- knowledge classification
- decision authority
- work states
- blocker routing
- Definition of Ready
- execution progress rules
- review protocol
- Definition of Done
- handoff and tool honesty

Domain packs add field-specific vocabulary, diagnostics, readiness checks, workstream patterns, review checks, and completion evidence

## Runtime model

```text
User intent
   ↓
Capture outcome
   ↓
Load core contract
   ↓
Select zero or one domain pack
   ↓
Classify active blocker
   ↓
Resolve current frontier
   ↓
Update Execution Brief
   ↓
Ready gate
   ↓
Execute or hand off
   ↓
Review
   ↓
Verify
   ↓
Done or next cycle
```

## Why the core is small

A universal skill becomes unreliable when it tries to contain specialist knowledge for every field

GTD keeps only cross-domain execution semantics in core and moves specialist behavior into additive packs

This gives domain authors a stable contract while keeping routing readable

## Execution Brief as boundary object

The Execution Brief is the durable interface between thinking, execution, verification, and handoff

It records

- intent
- scope and constraints
- Facts, Assumptions, and Unknowns
- settled and open Decisions
- workstreams and dependencies
- deliverables
- verification criteria and evidence
- blockers
- next executable action

The brief is intentionally useful even when the next agent does not have the original conversation

## State model

States describe what kind of work is currently possible

- `captured`: intent exists
- `clarifying`: meaning blocks progress
- `researching`: discoverable evidence blocks progress
- `modeling`: structure is being made executable
- `ready`: next action can be performed
- `executing`: an action is changing artifacts or external state
- `verifying`: a result exists and is being checked
- `done`: completion has supporting evidence
- `blocked`: progress requires unavailable authority, dependency, evidence, or capability

The detailed transition contract lives in [`core-contract.md`](../skills/get-things-done/references/core-contract.md)

## Deterministic and model-driven layers

GTD deliberately contains both

### Deterministic

- JSON validation
- file and package integrity checks
- domain contract shape
- basic Ready and Done structural assessment
- packaging

### Model-driven

- interpreting messy intent
- deciding which unknown matters now
- choosing the active blocker mode
- deciding when a domain pack is relevant
- evaluating trade-offs
- field-specific review

The CLI does not replace contextual judgment, and the skill does not pretend model judgment is deterministic
