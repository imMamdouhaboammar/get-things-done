# Repository and Pull Request Playbook

Use this playbook whenever repository state, an Issue, an open Pull Request, CI, a GitHub App, or landing is in scope.

## Authority order

1. current repository state
2. repository-native gates and current-head CI
3. executed local/runtime verification
4. current review and bot findings
5. handoff prose or remembered state

Old context may explain history but cannot overrule current state.

## Open Pull Request context gate

Before planning, repairing, judging readiness, or landing an open Pull Request, inspect materially relevant top-level PR comments, review submissions, inline review threads, useful resolved history, checks/statuses, bot summaries, bot-authored commits, and current head SHA.

Classify each material automated item as CURRENT_ACTIONABLE, CURRENT_CONTEXT, ALREADY_FIXED, STALE_AFTER_NEW_HEAD, DUPLICATE, FALSE_POSITIVE, or NEEDS_DECISION.

Then verify the claim against current code, current checks, tests, runtime evidence, or the relevant external contract.

BOT != NOISE
BOT != TRUTH

Consume useful existing feedback before triggering duplicate review.

## Mutation invalidation

After any push, bot-authored commit, conflict resolution, migration, or other material mutation:

1. refresh current head/state
2. refresh review and bot context
3. rerun affected verification
4. invalidate readiness or landing evidence tied to the old state

## Review policy

Default to self-review, then one independent reviewer, then one specialist second lens only when risk justifies it.

Reviewers identify risk. They do not replace tests, build evidence, runtime checks, or current-head CI.

## Landing policy

Before merge or equivalent landing, establish current exact state, confirm required checks, handle unresolved material findings, choose one active landing owner, obey stricter repository gates, and never treat queue submission as merge completion.
