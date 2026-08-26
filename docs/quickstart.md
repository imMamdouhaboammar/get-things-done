# Quickstart

Start with the idea as you actually have it. Do not rewrite it into a formal prompt first

For substantial work, Get Things Done should make these elements explicit before a large plan appears

- desired outcome
- important Facts
- explicit Assumptions
- open Decisions
- blocking Unknowns
- scope boundaries
- success criteria
- one next executable action

## Create a machine-readable brief

```bash
python scripts/gtd.py new-brief \
  --title "Brand-aware generation" \
  --domain software \
  --out brief.json
```

Validate its structure

```bash
python scripts/gtd.py validate-brief brief.json --root .
```

Assess the basic Ready and Done gates

```bash
python scripts/gtd.py assess-brief brief.json
```

## Choose the right stopping point

If the request is for clarity, a Ready brief can be the correct endpoint

If the request includes implementation and the runtime can perform it, continue into action and verification

If action cannot happen in the current runtime, preserve the blocker and the exact next action instead of implying that delivery occurred

## Verify before Done

A deliverable is not automatically a completed outcome

Examples of useful evidence include tests or inspected behavior for software, measurement checks for marketing, source-backed findings for research, and acceptance evidence for product work
