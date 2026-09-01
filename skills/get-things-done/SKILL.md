---
name: get-things-done
description: >
  Use when someone says "I have an idea but don't know where to start", "help me figure out what to do next on X", "turn this into a plan I can actually execute", "I'm stuck and need to find the blocker", or "what's the next action here" — even if they don't mention GTD or execution models. Turn messy, unclear, broad, or contradictory intent into an executable work model and drive it through delivery. Do not use for simple one-step questions with a known answer, tasks already fully specified and ready to execute, or pure research or writing with no decision component.
---

# Get Things Done

Turn unclear intent into an executable work model, then continue through delivery when execution was requested and the runtime can act.

Load `references/core-contract.md` at the start of every cycle — the knowledge ledger, mode router, and gate contracts live there.

## Domain quick-select

Load one matching pack from `domains/` only when task intent clearly belongs to a supported field. Stay on core when domain is ambiguous — never force a domain from keywords alone.

| Domain | Load when |
|---|---|
| `domains/software.md` | code, APIs, architecture, bugs, infra |
| `domains/product.md` | user problems, features, prioritization, roadmap |
| `domains/research.md` | evidence synthesis, literature, technical investigation |
| `domains/marketing.md` | campaigns, positioning, acquisition, content |
| `domains/advisory.md` | strategic crossroads, career forks, direct honest feedback |
| `domains/data-ai.md` | data pipelines, ML, model training, AI system design |
| `domains/design-ux.md` | UX research, interaction design, design systems |
| `domains/operations.md` | incidents, runbooks, SLO management, postmortems |
| `domains/legal-compliance.md` | contracts, compliance gaps, regulatory mapping |

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

## Output

See `references/output-profiles.md` for output shape by task size.
