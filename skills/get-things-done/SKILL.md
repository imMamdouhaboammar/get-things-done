---
name: get-things-done
description: Use when a user has a messy, unclear, broad, incomplete, or partially formed idea and needs it turned into work that can actually be decided, executed, verified, or handed off across domains
---

# Get Things Done

Convert ambiguity into an executable work model, then continue through delivery when the user asked for execution and the runtime can act

**REQUIRED REFERENCE:** Read `references/core-contract.md`

Load one matching file from `domains/` when the task clearly belongs to a supported domain. If none fits, use the core alone. Never force a domain

## Run

1. **Capture** the user's intended outcome and separate it from proposed solutions
2. **Diagnose** the current blocker with the core mode router. Do not run every mode
3. **Maintain** an Execution Brief using `references/execution-brief.schema.json`. In chat-only environments, preserve the same fields conceptually
4. **Resolve the frontier**. Find discoverable Facts yourself. Make only reversible, low-risk Assumptions. Ask only for blocking Decisions that materially change the outcome
5. **Model** scope, dependencies, risks, deliverables, and one next executable action
6. **Gate on Ready** using the core Definition of Ready plus loaded domain additions
7. **Execute when requested**. If the user asked only for clarity or planning, stop at the executable model. If delivery was requested and tools are available, act instead of only describing action
8. **Review** through Outcome, Domain, Execution, and Verification lenses plus loaded domain checks
9. **Verify** against observable success criteria. Never claim completion from confidence language
10. **Finish or hand off** with evidence, remaining limitations, blockers, and the next executable action

## Interaction rules

Do not interrogate the user for information you can obtain yourself

Do not dump a long questionnaire. Ask only the smallest blocking decision set

Do not hide uncertainty. Label Facts, Assumptions, Decisions, and Unknowns when the distinction matters

Do not pretend a tool, source, file, or action was used when it was unavailable

A plan is not progress. Prefer a concrete Decision, artifact, executed action, or verification result each cycle

## Outputs

For small tasks, answer directly with the clarified outcome and next executable action

For substantial tasks, produce or update an Execution Brief. Use `templates/execution-brief.md` for human output and JSON when a machine-readable handoff is useful
