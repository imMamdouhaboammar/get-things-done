# Quickstart

Start with the idea as you actually have it. Do not rewrite it into a formal prompt first.

For substantial work, Get Things Done should make these elements explicit before a large plan appears:

- desired outcome
- important Facts
- explicit Assumptions
- open Decisions
- blocking Unknowns
- scope boundaries
- success criteria
- one next executable action

## 1. Verify your setup

Check repository health and registered domain packs:

```bash
python scripts/gtd.py doctor
```

Inspect adapter ecosystem status and capabilities across all 19 supported targets:

```bash
python scripts/adapters.py status
python scripts/adapters.py capabilities
```

## 2. Create a machine-readable brief

```bash
python scripts/gtd.py new-brief \
  --title "Brand-aware generation" \
  --domain software \
  --out brief.json
```

Validate its structure against the schema:

```bash
python scripts/gtd.py validate-brief brief.json --root .
```

Assess the basic Ready and Done gates:

```bash
python scripts/gtd.py assess-brief brief.json
```

Render the brief into human-readable Markdown:

```bash
python scripts/gtd.py render-brief brief.json --out brief.md
```

Export every plan representation in one pass:

```bash
python scripts/gtd.py export-brief brief.json --format all --out dist/brief
```

This writes Markdown, lossless JSON, TOON, Mermaid, and graph JSON. Use a single format when needed:

```bash
python scripts/gtd.py export-brief brief.json --format toon --out brief.toon
python scripts/gtd.py export-brief brief.json --format graph --out dist/brief-graph
```

## 3. Export for your agent host

Export a ready-to-use adapter package for your target host:

```bash
# Export for Cursor IDE
python scripts/adapters.py export cursor --out dist/adapters

# Export for ChatGPT / Codex with a deterministic ZIP bundle
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package

# Inspect companion boundaries (e.g. Context7 documentation retrieval)
python scripts/adapters.py interop context7
```

## 4. Choose the right stopping point

If the request is for clarity, a Ready brief can be the correct endpoint.

If the request includes implementation and the runtime can perform it, continue into action and verification.

If action cannot happen in the current runtime, preserve the blocker and the exact next action instead of implying that delivery occurred.

## 5. Verify before Done

A deliverable is not automatically a completed outcome.

Examples of useful evidence include tests or inspected behavior for software, measurement checks for marketing, source-backed findings for research, and acceptance evidence for product work.

