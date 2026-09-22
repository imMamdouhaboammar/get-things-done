# GTD Deliberation

GTD Deliberation is the reasoning layer between a messy request and committed execution.

It exists for cases where direct planning can lock in a bad premise.

## Why it exists

A user request can contain three different things:

- a real desired outcome
- an explanation of why the problem exists
- a proposed solution

Those are not equally reliable.

Deliberation separates them, refreshes current knowledge, tests assumptions, reconstructs the problem, explores alternatives, and only then allows implementation planning.

## Runtime

```text
Messy request
  ↓
Activation Router
  ├─ bypass → normal GTD
  └─ activate
       ↓
     Contemplate
       ↓
     Freshness Gate
       ↓
     Research
       ↓
     Challenge
       ↓
     Reframe
       ↓
     Ideate
       ↓
     Critique + Synthesize
       ↓
     Direction Gate
       ↓
     Superpowers-style planning
       ↓
     Backlog
       ↓
     GTD execution
```

## Freshness is mandatory when activated

Deliberation must not treat remembered model knowledge as current evidence.

The agent resolves the current date at runtime and searches relevant current sources. The Problem Model stores the search scope, queries, sources, findings, changed claims, and any freshness gaps.

If search is unavailable or forbidden, that limitation remains visible.

## Problem Model

The Problem Model is the durable artifact for the thinking phase.

It records:

- original request
- desired outcome
- proposed solution
- current framing
- current-date freshness evidence
- assumptions
- supporting and contradicting evidence
- alternative framings
- second-order effects
- candidate directions
- rejected directions
- recommended direction
- open user Decisions
- Direction Gate status
- reason to stop contemplating

Schema: `skills/gtd-deliberation/references/problem-model.schema.json`

## Direction Gate

Use `pending`, `approved`, `rejected`, or `provisional`.

High-impact or hard-to-reverse implementation directions require user approval.

A reversible experiment may proceed provisionally when testing is cheaper than another analysis cycle.

## Backlog

After direction approval, planning methodology may decompose the work.

The durable backlog records:

- approved direction
- source Problem Model
- epics
- tasks
- dependencies
- acceptance criteria
- required evidence
- decision log
- risks
- next action

Schema: `skills/gtd-deliberation/references/backlog.schema.json`

## CLI

```bash
python skills/gtd-deliberation/scripts/deliberation.py new-problem-model \
  --title "Engagement diagnosis" \
  --request "Add AI because engagement is low" \
  --out problem.json

python skills/gtd-deliberation/scripts/deliberation.py validate-problem-model problem.json

python skills/gtd-deliberation/scripts/deliberation.py new-backlog \
  --title "Activation experiment" \
  --direction "Test onboarding friction first" \
  --problem-model problem.json \
  --next-action "Draft experiment brief" \
  --out backlog.json

python skills/gtd-deliberation/scripts/deliberation.py validate-backlog backlog.json
```

## What it is not

It is not a requirement to perform maximum-depth reasoning on every task.

The activation router should bypass deliberation when work is obvious, low risk, fully specified, or cheaper to test than to discuss.
