---
name: building-gtd-domain-packs
description: Use when Get Things Done needs to be adapted to a new professional field, discipline, organization practice, or specialized workflow without forking the core skill
---

# Building GTD Domain Packs

Create a domain extension that inherits the Get Things Done core instead of copying it

**REQUIRED REFERENCE:** Read local `references/domain-pack-spec.md` and `references/core-contract.md`

## Method

1. Name the field at the level where terminology and completion criteria meaningfully differ
2. Collect real task examples that fail for different reasons
3. Extract canonical vocabulary and important distinctions
4. Keep only diagnostic questions that can change scope, Decisions, execution, or verification
5. Define optional `domain_data` fields rather than modifying the core schema
6. Add field-specific Definition of Ready checks
7. Add 2 to 4 reusable workstream patterns
8. Add review checks that catch field-specific failure
9. Define observable Completion checks
10. Add Common traps from real failure patterns
11. Validate every required heading in the domain pack specification
12. Test one messy idea, one well-formed task, one deceptive near-complete task, and one task that should not select this domain

Use `templates/domain-pack-template.md`

## Rules

Do not copy the core workflow into the domain pack

Do not turn field knowledge into a mandatory questionnaire

Do not create a new domain when an existing pack only needs additive vocabulary or checks

A domain pack can be stricter than core. It cannot weaken decision authority, evidence requirements, readiness, completion, handoff, or tool honesty
