# Execution Brief

The Execution Brief is the durable work model used by Get Things Done for substantial tasks

It is designed to survive context changes, handoffs, and tool boundaries without requiring another agent to reconstruct the original conversation

## Core sections

- **Intent**: problem, desired outcome, actor or beneficiary
- **Scope**: in, out, constraints
- **Knowledge**: Facts, Assumptions, Unknowns
- **Decisions**: settled choices with rationale and reversibility
- **Open decisions**: unresolved choices that can block Ready
- **Workstreams**: independently understandable units with dependencies
- **Deliverables**: artifacts or results expected from the work
- **Verification**: success criteria and collected evidence
- **Blockers**: conditions preventing the next useful action
- **Next action**: one executable step

## State and gate relationship

A brief can exist in any GTD state

`captured` and `modeling` briefs are expected to be incomplete

A `ready` brief should satisfy the Ready gate

A `verifying` brief should contain a deliverable and active checks

A `done` brief should contain evidence that supports the promised result

## Structural assessment

Use the CLI for basic structural checks

```bash
python scripts/gtd.py assess-brief brief.json
```

The command checks visible gaps such as missing success criteria, open decisions, blockers, missing deliverables, or missing evidence

It does not determine whether the strategy is good or whether field-specific evidence is sufficient. Those remain model and domain review responsibilities

## Export formats

Use `export-brief` to project one validated Execution Brief into deterministic representations:

| Format | CLI value | Output | Purpose |
|---|---|---|---|
| Markdown | `md` | `.md` | Human review and handoff |
| JSON | `json` | `.json` | Lossless machine-readable brief |
| TOON | `toon` | `.toon` | Token-efficient LLM context using [TOON Specification 4.1](https://github.com/toon-format/spec/blob/main/SPEC.md) |
| Mermaid | `mermaid` | `.mmd` | Renderable relationship diagram |
| Graph JSON | `graph-json` | `.graph.json` | Directed `nodes`/`edges` model for tools and UIs |

```bash
# One representation: --out is a file
python scripts/gtd.py export-brief brief.json --format toon --out brief.toon

# Both relational graph representations: --out is a directory
python scripts/gtd.py export-brief brief.json --format graph --out dist/brief-graph

# Every representation: --out is a directory
python scripts/gtd.py export-brief brief.json --format all --out dist/brief
```

The relational graph includes workstreams and their dependencies, deliverables, success criteria, blockers, and the next executable action. A dependency matching a workstream name links to that workstream; an unmatched dependency becomes an explicit `external_dependency` node instead of being dropped.

`render-brief` remains available as the backward-compatible Markdown-only command.

## Schema

The machine-readable contract is [`execution-brief.schema.json`](../skills/get-things-done/references/execution-brief.schema.json)
