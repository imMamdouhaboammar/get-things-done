# Freshness Search Contract

GTD Deliberation must not treat model memory as current evidence.

## Freshness Gate

Before a substantive direction is accepted:

1. resolve the current local date from the runtime
2. formulate search queries that include or are explicitly scoped to the current date or current version context
3. inspect current, relevant sources
4. compare current evidence with remembered or previously supplied knowledge
5. record whether the evidence confirms, changes, or invalidates the initial framing

For example, if the runtime date is 2026-09-22, a query may explicitly include "September 2026" or "2026-09-22" when that improves freshness.

Do not hard-code today's date in the Skill. Resolve it at runtime.

## Search priority

Prefer, in order:

1. current first-party or authoritative sources
2. current source-of-truth systems such as the live repository, official docs, current product pages, standards, laws, schedules, or primary datasets
3. recent high-quality reporting or research when primary evidence is unavailable
4. community evidence for experience, sentiment, or edge cases, clearly labeled as such

## Required record

A Problem Model should record:

- `searched_at`
- `search_scope`
- `queries`
- `sources`
- `freshness_findings`
- `stale_or_changed_claims`
- `freshness_gaps`

## Failure policy

If current search is unavailable:

- do not imply current verification
- mark the freshness status `blocked`
- identify which conclusions depend on remembered knowledge
- proceed only when the decision is reversible and the evidence gap is acceptable
- otherwise stop at the relevant Decision or blocker

If the user explicitly forbids web or external search, respect that constraint and mark the freshness limitation.

## Local and versioned work

For repository or software work, freshness can include:

- current repository state
- lockfile or manifest versions
- current official docs for those versions
- current upstream release notes when relevant

A local code snapshot alone does not prove an external API or dependency contract is still current.
