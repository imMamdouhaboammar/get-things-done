---
name: building-gtd-domain-packs
description: Use when Get Things Done needs adaptation for a professional field, discipline, organization practice, or specialized workflow without forking the core skill
---

# Building GTD Domain Packs

Create a focused domain extension that inherits Get Things Done instead of copying it

**REQUIRED REFERENCES:** Read local `references/domain-pack-spec.md` and `references/core-contract.md`

## Build method

1. **Collect failure examples first**
   Gather at least four realistic tasks: messy in-domain, well-formed in-domain, deceptive near-complete, and adjacent out-of-domain

2. **Prove the core is insufficient**
   Identify which field-specific vocabulary, readiness, review, or completion behavior is missing. If the core already handles the examples, do not create a pack

3. **Define selection boundaries**
   Write positive and negative selection signals based on intent and artifacts, not isolated keywords

4. **Extract only consequential vocabulary**
   Keep terms whose confusion would change decisions, execution, or verification

5. **Add diagnostic candidates**
   Include only questions that can change material work. Do not make them mandatory

6. **Extend the brief safely**
   Put optional field data under `domain_data`. Never fork core fields

7. **Add stricter gates where needed**
   Define domain-specific readiness checks, 2 to 4 workstream patterns, specialist review checks, and observable completion evidence

8. **Test routing collisions**
   The adjacent out-of-domain case must remain outside this pack. Tighten selection signals until it does

9. **Test deceptive completion**
   A plausible deliverable without field-specific proof must not pass Done

10. **Validate the contract**
    Confirm every required heading appears exactly once and the pack does not weaken the core

Use `templates/domain-pack-template.md` as the output shape

## Rules

- Do not copy the core workflow into the domain pack
- Do not turn field knowledge into a questionnaire
- Do not create a new domain for branding or naming alone
- Do not weaken decision authority, readiness, evidence, completion, handoff, or tool honesty
- Do not claim a domain is validated until the four collision cases were actually exercised
