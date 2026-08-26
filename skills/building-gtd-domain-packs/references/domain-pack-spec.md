# GTD Domain Pack Specification

A domain pack extends Get Things Done for a field where vocabulary, diagnosis, readiness, review, or completion meaningfully differs from the generic core

## Inheritance rule

Every domain pack **must inherit** `core-contract.md`

A domain pack **must not override**

- Fact, Assumption, Decision, and Unknown semantics
- decision authority
- state meanings
- Definition of Ready
- evidence-backed Definition of Done
- tool honesty
- handoff semantics

A domain pack may add stricter checks

## When a new domain is justified

Create a new pack only when at least two of these are true

1. the field has vocabulary that must remain distinct to avoid wrong work
2. the field needs diagnostic questions that materially change execution
3. the field has readiness requirements not covered by core
4. the field requires specialist review checks
5. completion requires evidence patterns unique to the field

If none apply, use the core or extend an existing pack

## Required metadata

```yaml
---
domain: example-domain
version: 1
extends: gtd-core-v1
---
```

The domain slug uses lowercase letters, numbers, and hyphens

## Required sections

Every pack contains these headings exactly once

1. `## Selection signals`
2. `## Domain vocabulary`
3. `## Diagnostic questions`
4. `## Extra brief fields`
5. `## Readiness additions`
6. `## Workstream patterns`
7. `## Review additions`
8. `## Completion checks`
9. `## Common traps`

## Selection signals

Describe task shapes, requested outcomes, artifacts, and constraints that indicate the field

Select from intent, not keyword matching alone

Also include at least one **non-selection signal** so agents can distinguish adjacent domains

## Domain vocabulary

Define concepts the agent must keep distinct and explain why confusing them changes the work

Avoid turning the pack into a glossary of obvious terms

## Diagnostic questions

Include only questions whose answers can materially change scope, decisions, execution, risk, or verification

Questions are candidates, not a mandatory questionnaire

## Extra brief fields

Add optional keys under `domain_data`

Keep the core schema stable and do not duplicate core fields under domain data

## Readiness additions

Add checks that must pass before execution in this field

Every check must be observable enough that another agent could tell whether it passed

## Workstream patterns

Provide 2 to 4 reusable decompositions

Each pattern should describe when it applies, expected outcome, and common dependency edges

Patterns are not mandatory project templates

## Review additions

Add field-specific checks after the four core review lenses

Review additions should catch plausible but harmful near-misses, not restate generic quality advice

## Completion checks

Define observable evidence required for field-specific completion

Prefer inspectable artifacts, tests, measurements, approvals, or source-backed findings over subjective language

## Common traps

Capture productive-looking failure patterns that do not move the requested outcome

## Collision testing

Before publishing a domain pack, test four cases

1. a messy task that should select the domain
2. a well-formed task that should select the domain
3. a deceptive near-complete task that should fail completion
4. an adjacent task that should **not** select the domain

If the fourth case routes to the new pack, tighten selection signals before release

## Versioning

Increment `version` when domain behavior changes in a way that can alter routing, readiness, review, or completion expectations

Editorial wording changes that do not change behavior do not require a version increment
