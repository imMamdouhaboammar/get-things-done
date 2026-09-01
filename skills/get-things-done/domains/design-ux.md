---
domain: design-ux
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Design & UX
## Selection signals
Wireframes, mockups, design systems, user flows, accessibility audits, usability testing, component design, interaction patterns, visual design, design critique, design handoff, prototyping. Non-selection: implementation of already-approved designs (software domain), pure user research without design artifacts.
## Domain vocabulary
Keep distinct: user vs persona (user is a real person observed; persona is a composite model — designing for the persona instead of the evidence is a leading cause of misfit solutions), wireframe vs prototype (wireframe is structure; prototype simulates interaction — using wrong fidelity wastes iteration cycles before the problem is validated), usability vs desirability (can they do it vs do they want to — solving only one fails both), accessibility vs compliance (compliance is the floor; accessibility is the goal — treating them as equal produces WCAG checkbox culture with no real improvement), feedback vs direction (feedback describes what is wrong; direction says what to change — giving only feedback stalls work).
## Diagnostic questions
Ask only when blocking: Who is this designed for and what evidence supports that? What decision does this prototype need to answer? What fidelity is appropriate for the current question? What accessibility requirements apply? Who has sign-off authority?
## Extra brief fields
`user_segment`, `prototype_fidelity`, `decision_being_tested`, `stakeholder_sign_off`, `accessibility_standard`, `design_system_ref`, `critique_mode`
## Readiness additions
- user segment is defined with at least one real observation or explicitly recorded as an assumption
- design decision being tested is explicit before prototype work starts
- prototype fidelity matches the question being answered, not aspirational quality
- accessibility requirements are stated before design begins, not after
## Workstream patterns
- discovery to design: user observation → problem framing → concept generation → prototype → test → iteration → handoff
- design system: audit → pattern inventory → component spec → accessibility check → documentation → review → publish
- critique: scope framing → structured observation → gap identification → direction proposals → prioritization
- accessibility: WCAG audit → issue classification → remediation plan → remediation → re-audit → confirmation
## Review additions
Check whether design decisions are grounded in user evidence rather than persona assumption, whether prototype fidelity matches the question, whether accessibility was considered before implementation, whether stakeholder alignment was confirmed before handoff, and whether handoff artifacts are implementation-complete (specs, assets, annotations).
## Completion checks
Design artifact reflects final decisions, accessibility review completed at the stated standard, stakeholder sign-off confirmed and traceable, implementation-ready handoff produced when applicable, and usability or A/B evidence cited when effectiveness is claimed.
## Common traps
Designing for the persona instead of observed users, using high fidelity before the problem is validated, treating accessibility as a final-step audit, collecting feedback without actionable direction, and claiming design is complete without stakeholder sign-off.
