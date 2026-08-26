# Get Things Done Skill Pack Design

## Purpose

Get Things Done converts an unclear, messy, or incomplete idea into an executable work model, then continues through execution and verification when the user asks for delivery and the runtime has the required tools

The core is domain independent. Domain packs add vocabulary, field checks, and execution patterns without changing the core contract

## Product boundary

This is not a generic project manager and not a universal expert prompt. Its job is to move work from ambiguity to an explicit model, then from model to evidence-backed completion

The pack has two skills:

1. `get-things-done`: capture, clarify, model, execute, verify, and hand off work
2. `building-gtd-domain-packs`: create new domain packs that inherit the core contract

## Core model

Every run maintains:

- Intent: the outcome the user is trying to cause
- Knowledge ledger: Facts, Assumptions, Decisions, Unknowns
- Scope: what is in and out
- Work model: workstreams, dependencies, risks, deliverables, next executable action
- Verification: evidence required to claim completion

State machine:

`captured -> clarifying/researching/modeling -> ready -> executing -> verifying -> done`

`blocked` is allowed when a missing user decision, permission, dependency, or external condition prevents progress

## Routing

- unclear intent -> clarify
- missing discoverable fact -> research
- scope too broad -> decompose
- conflicting options -> decide
- uncertain feasibility -> validate
- enough context -> model
- model ready and delivery requested -> execute
- deliverable exists -> verify

Questions are reserved for decisions that materially change the outcome or cannot be safely inferred. Discoverable facts are looked up by the agent when tools are available

## Decision authority

- Fact: agent gathers evidence
- Assumption: agent may make a reversible, low-risk assumption if explicit
- Decision: user owns high-impact, hard-to-reverse, preference-heavy, financial, public, or outcome-changing decisions
- Unknown: remains visible until resolved, accepted, or proved non-blocking

## Definition of Ready

Ready requires an understandable outcome, bounded-enough scope, visible critical constraints and assumptions, resolved blocking decisions, checkable success, and one next executable action

## Definition of Done

Done requires promised deliverables, verification evidence, explicit remaining limitations, and a next action or clean handoff when work continues

No completion claim may rely only on confidence language

## Review model

Review through four lenses:

1. Outcome review: right problem, scope, and ambition
2. Domain review: field vocabulary, constraints, and quality criteria
3. Execution review: dependencies, sequence, interfaces, and failure modes
4. Verification review: evidence that can prove the result

Domain packs may add lenses but cannot remove these four

## Artifacts

The canonical machine artifact is `Execution Brief v1`, validated by `execution-brief.schema.json`. A human-readable Markdown rendering is also provided

## Domain inheritance

A domain pack may add selection signals, vocabulary, diagnostic questions, extra `domain_data`, readiness checks, workstream patterns, review additions, completion checks, and common traps

It must not override the core distinctions, decision authority, evidence requirements, readiness, completion, handoff, or tool honesty

## Initial domain packs

- software
- marketing
- product
- research

## Tooling

A dependency-free Python CLI provides `doctor`, `list-domains`, `new-domain`, `new-brief`, `validate-brief`, and `render-brief`

The agent supplies reasoning. The CLI supplies deterministic scaffolding and validation
