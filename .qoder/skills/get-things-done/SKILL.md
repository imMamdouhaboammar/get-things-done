---
name: get-things-done
description: Use when a user has a messy, unclear, broad, incomplete, contradictory, or partially formed idea and needs help turning it into work that can be decided, executed, verified, or handed off across domains
---

# Get Things Done

Turn unclear intent into an executable work model, then continue through delivery when execution was requested and the runtime can act

**REQUIRED REFERENCE:** Read `references/core-contract.md`

Load one matching pack from `domains/` only when task intent clearly belongs to a supported field. If selection is ambiguous, stay on the core until evidence favors a domain. Never force a domain from keywords alone

## Operating loop

1. **Capture the outcome**
   Separate the user's desired result from the solution they happened to propose

2. **Classify the current blocker**
   Choose one active mode from the router in `core-contract.md`: clarify, research, decompose, decide, validate, model, execute, or verify

3. **Maintain the work model**
   For substantial work, keep an Execution Brief compatible with `references/execution-brief.schema.json`. In chat-only contexts, preserve the same concepts without pretending a file exists

4. **Resolve only the current frontier**
   Discover Facts yourself when tools or sources can answer them. Make reversible low-risk Assumptions explicitly. Ask the user only for blocking Decisions that materially change scope, cost, risk, preference, or outcome

5. **Create an executable unit**
   Bound scope, dependencies, risks, deliverables, success criteria, and one next action that can actually be performed

6. **Pass the Ready gate**
   Do not call work ready while a blocking Decision, blocker, unverifiable outcome, or missing next action remains

7. **Act when action was requested**
   If the user asked only for clarification or planning, stop at the executable model. If they asked for delivery and tools are available, perform the next action instead of narrating it

8. **Review the result**
   Review through Outcome, Domain, Execution, and Verification lenses plus any loaded domain checks

9. **Prove completion**
   Record observable evidence against success criteria. A confident explanation, plan, generated draft, or agent report is not proof by itself

10. **Finish, continue, or hand off**
    Mark Done only when the completion contract is satisfied. Otherwise preserve blockers, limitations, evidence, and the next executable action

## Interaction policy

- Do not interrogate the user for discoverable information
- Do not dump a generic questionnaire
- Do not ask questions whose answers will not change the work
- Do not silently promote an Unknown into a Fact
- Do not hide trade-offs inside recommendations
- Do not claim a file, connector, command, website, or external action was used when it was unavailable
- Do not confuse analysis volume with progress

## Progress rule

Each meaningful cycle should produce at least one of these

- a Decision settled
- an artifact created or changed
- an external action executed
- verification evidence collected

If none happened, the cycle remained analysis

## Output profiles

**Small task:** clarified outcome, relevant assumptions, and next executable action

**Substantial task:** updated Execution Brief plus the active blocker or next action

**Handoff:** current outcome, status, scope, knowledge ledger, decisions, artifacts, evidence, blockers, and next action without duplicating existing artifacts
