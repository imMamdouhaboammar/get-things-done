---
domain: product
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Product
## Selection signals
Product discovery, feature definition, user problems, requirements, MVP scope, prioritization, roadmap decisions, onboarding, retention, pricing, product metrics
## Domain vocabulary
Keep distinct: user, buyer, job, problem, current behavior, constraint, opportunity, solution, feature, requirement, trade-off, metric, adoption, retention
## Diagnostic questions
Ask only when blocking: Who has the problem? What do they do today? What event makes it urgent? What outcome would cause switching or payment? Which assumption can invalidate the idea? What is the smallest useful behavior change?
## Extra brief fields
`user`, `buyer`, `job`, `current_behavior`, `pain`, `opportunity`, `solution_hypothesis`, `requirements`, `non_goals`, `product_metrics`, `adoption_risk`
## Readiness additions
- target user and current behavior are explicit
- problem evidence is separated from solution preference
- smallest useful scope is defined
- primary product metric and failure signal are defined
## Workstream patterns
- discovery: evidence -> user/job -> current behavior -> problem -> opportunity
- definition: solution hypothesis -> requirements -> non-goals -> risks -> acceptance
- launch: build -> instrument -> release -> observe -> decide
## Review additions
Check whether the problem is real, whether scope changes user behavior, whether non-goals protect focus, whether metrics detect success and harm, and whether cheaper validation exists before build
## Completion checks
Requirements are testable, non-goals are visible, acceptance evidence exists, instrumentation is defined when needed, and the next product decision is tied to observed behavior
## Common traps
Starting from features, treating stakeholder requests as user evidence, calling a long backlog an MVP, activity-only metrics, and skipping the current behavior baseline
