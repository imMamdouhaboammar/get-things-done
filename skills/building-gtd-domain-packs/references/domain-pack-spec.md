# GTD Domain Pack Specification

A domain pack extends Get Things Done for a field such as software, marketing, product, law, operations, finance, or research

## Inheritance rule

Every domain pack **must inherit** `core-contract.md`

A domain pack **must not override** Fact, Assumption, Decision, and Unknown semantics, decision authority, Definition of Ready, evidence-backed Definition of Done, tool honesty, or Handoff semantics

A domain pack may add stricter checks

## Required sections

Every pack contains these headings exactly once:

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

Describe task shapes and intent signals that indicate the field. Use intent, not keyword matching alone

## Domain vocabulary

Define concepts the agent must keep distinct

## Diagnostic questions

Include only questions that can materially change scope, decisions, execution, or verification

## Extra brief fields

Add optional keys under `domain_data`. Keep the core schema stable

## Readiness additions

Add checks required before execution in this field

## Workstream patterns

Provide reusable decompositions, not mandatory templates

## Review additions

Add field-specific review lenses after the four core lenses

## Completion checks

Define observable evidence that proves the field-specific deliverable works or is complete

## Common traps

Capture productive-looking mistakes that do not move the outcome

## Versioning

Use metadata with `domain`, `version`, and `extends: gtd-core-v1`
