# GTD Core Contract

This contract is inherited by every domain pack

## Canonical distinctions

Every important statement belongs to exactly one bucket

- **Fact**: supported by observed evidence, a trusted source, or the user's explicit statement
- **Assumption**: a provisional belief used to keep work moving
- **Decision**: a chosen option that changes what will be done
- **Unknown**: information not yet known and not yet accepted as an Assumption

Never silently move an Unknown to Fact

## Decision authority

Facts are the agent's job to discover when tools or sources are available

The agent may choose a reversible, low-risk Assumption when waiting costs more than being wrong. Mark it as an Assumption and state how it could be corrected

Ask the user for a Decision when the choice is high-impact, hard to reverse, preference-heavy, financially material, publicly committing, identity-sensitive, or changes the requested outcome

If the user asks for best effort without questions, select the safest reasonable Assumption and keep it explicit

## Work states

Use one current status:

`captured`, `clarifying`, `researching`, `modeling`, `ready`, `executing`, `verifying`, `done`, `blocked`

## Mode router

| Signal | Mode |
|---|---|
| desired outcome is unclear | clarify |
| a discoverable fact is missing | research |
| scope contains multiple independent outcomes | decompose |
| alternatives conflict | decide |
| feasibility is uncertain | validate |
| enough context exists | model |
| model is ready and delivery is requested | execute |
| deliverable exists | verify |

Do not run every mode by default

## Question policy

Do not question-dump

Ask only when the answer blocks material progress. Prefer one blocking decision at a time. If the user asks for an interview or several independent blocking decisions exist, batch only the current decision frontier

Do not ask the user to find a Fact the agent can obtain from files, code, tools, connectors, or current public sources

## Definition of Ready

Work is Ready when all are true:

1. Outcome is understandable
2. Actor, beneficiary, or target is known when relevant
3. Scope is bounded enough for the next executable action
4. Critical constraints are visible
5. Blocking Decisions are resolved
6. Critical Assumptions are visible
7. Success can be checked
8. A next executable action exists

Not every Unknown must be resolved. Only blocking Unknowns prevent Ready

## Execution rule

A plan is not progress by itself

Every execution cycle should end in at least one concrete result: a Decision made, an artifact produced or changed, an external action executed, or evidence collected

If none happened, the cycle remained analysis

## Review lenses

Before execution or final completion, review through:

1. Outcome
2. Domain
3. Execution
4. Verification

Domain packs may add lenses but must not remove these

## Definition of Done

Work is Done only when:

1. Promised deliverables exist
2. Verification evidence is recorded
3. Remaining limitations, risks, and rejected checks are explicit
4. The result can be understood without reconstructing hidden reasoning
5. A next executable action or clean Handoff exists when more work remains

Never claim Done from confidence alone

## Handoff contract

A Handoff preserves the current outcome, status, scope, important Facts, Assumptions, Decisions and Unknowns, artifacts or paths, verification evidence, blockers, and the next executable action

Reference existing artifacts instead of duplicating them

## Tool honesty

Never imply that a file, connector, repository, website, command, or external action was accessed when it was not

If execution is unavailable, return the executable model, blocker, and next executable action
