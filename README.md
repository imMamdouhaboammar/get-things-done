<div align="center">

# Get Things Done

### Your idea is not a task yet

Turn messy intent into a clear work model, identify the real blocker, execute the next useful action, and require evidence before calling anything done

[![CI](https://github.com/imMamdouhaboammar/get-things-done-skillpack/actions/workflows/ci.yml/badge.svg)](https://github.com/imMamdouhaboammar/get-things-done-skillpack/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Agent Plugins 1.0](https://img.shields.io/badge/Agent_Plugins-1.0-111111.svg)](https://agent-plugins.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)

**One canonical GTD core · Agent Skills · Agent Plugins · Host adapters · Execution Briefs · Domain Packs · Evidence-based completion**

</div>

## The problem

Most ideas do not arrive as clean requirements

They arrive half-formed, mixed with assumptions, missing decisions, unclear scope, and several possible next moves

A normal assistant can turn that into a long plan

That is not the same as making the work executable

**Get Things Done focuses on the gap between “I have an idea” and “there is a next action we can perform and verify”**

It separates what is known from what is assumed, identifies the current blocker, decides whether the work needs clarification, research, decomposition, a decision, validation, execution, or verification, then keeps the state in a reusable Execution Brief

## One GTD core, many agent hosts

GTD does not maintain a different reasoning workflow for every AI client

```text
                    Canonical GTD Skills
                           │
          ┌────────────────┼────────────────┐
          │                │                │
      Agent Skills     Agent Plugins    Host Adapters
          │                │                │
          └────────────────┼────────────────┘
                           │
 Claude · ChatGPT · Codex · Cursor · Kimi · Grok · DeepCode · more
```

The `skills/` tree remains the source of truth

Adapters own only discovery paths, manifests, packaging, installation layout, and compatibility checks

That means a host integration cannot quietly fork the GTD decision model or create a second version of the workflow

## Supported surfaces

The repository tracks **17 adapter contracts**. The label describes the package/export contract GTD verifies, not a claim that every vendor has approved or listed the package in its public marketplace

| Target | Support model | Delivery |
|---|---|---|
| Agent Skills / compatible agents | Native standard | canonical `skills/` tree |
| Agent Plugins | Native standard | root `plugin.json` |
| Claude AI Skills | Portable | Agent Skills package |
| Claude Code | First-class adapter | Claude plugin + skills |
| Claude Marketplace | First-class package | `.claude-plugin/marketplace.json` |
| Claude Cowork | First-class adapter | Claude plugin/skill package |
| ChatGPT Web | First-class adapter | OpenAI plugin package |
| ChatGPT Work | First-class adapter | OpenAI plugin package |
| ChatGPT Plugins | First-class package | `.codex-plugin/plugin.json` |
| Codex | First-class adapter | OpenAI plugin + Agent Skills fallback |
| Cursor | First-class adapter | `.cursor/skills` |
| Kimi Code | First-class adapter | `kimi.plugin.json` + `.kimi-code/skills` |
| Grok Build | First-class adapter | `.grok/skills` |
| DeepSeek DeepCode | First-class adapter | `.deepcode/skills` |
| Vercel skills.sh | First-class distribution metadata | `skills.sh.json` |
| Contentful Skill Kit | Authoring bridge | typed workflow compilation when needed |
| Glama | Conditional | enabled only when GTD ships a real `mcp.json` |

Glama is intentionally not marked native today because GTD does not currently ship an MCP server

The adapter CLI fails closed instead of manufacturing registry support that does not exist

Public marketplace approval, directory listing, vendor review, and local package conformance are separate states. This repository only claims the states it can verify

See [Host adapters and distribution](docs/adapters.md)

## What GTD does

```text
Messy idea
   ↓
Outcome
   ↓
Facts · Assumptions · Decisions · Unknowns
   ↓
Current blocker
   ↓
Executable work model
   ↓
Definition of Ready
   ↓
Action
   ↓
Review
   ↓
Evidence
   ↓
Done or next action
```

The core behavior is intentionally domain-independent

Software, marketing, product, and research are added through domain packs that inherit the same decision, readiness, evidence, and handoff rules

## Core ideas

### Knowledge has types

| Type | Meaning |
|---|---|
| **Fact** | supported by evidence or an explicit user statement |
| **Assumption** | reversible belief accepted so work can continue |
| **Decision** | selected option that changes what will be done |
| **Unknown** | information that is still unresolved |

This prevents an unanswered question from quietly becoming a made-up fact

### One active blocker at a time

GTD routes the current blocker to one working mode

`clarify` · `research` · `decompose` · `decide` · `validate` · `model` · `execute` · `verify`

After each meaningful cycle, it classifies again

### Ready and Done are different gates

**Definition of Ready** asks whether the next action can be performed safely and meaningfully

**Definition of Done** asks whether the promised result exists and has supporting evidence

A polished plan can pass neither

### Progress must leave evidence

A useful cycle should produce at least one concrete result

- a decision settled
- an artifact created or changed
- an external action executed
- verification evidence collected

More analysis alone does not count as execution

## Execution Brief

Substantial work is represented as a portable Execution Brief

```json
{
  "version": "1.0",
  "title": "Brand-aware landing page generation",
  "domain": "software",
  "status": "modeling",
  "intent": {
    "problem": "AI-generated landing pages drift toward generic design choices",
    "desired_outcome": "Generated pages consistently follow supplied brand direction",
    "actor": "Design and growth team"
  },
  "scope": {
    "in": ["brand context representation", "generation rules", "review checks"],
    "out": ["full CMS", "analytics platform"],
    "constraints": ["must work across more than one model"]
  },
  "knowledge": {
    "facts": [],
    "assumptions": [],
    "unknowns": []
  },
  "decisions": [],
  "open_decisions": [],
  "workstreams": [],
  "deliverables": [],
  "verification": {
    "success_criteria": [],
    "evidence": []
  },
  "next_action": ""
}
```

The schema lives at [`skills/get-things-done/references/execution-brief.schema.json`](skills/get-things-done/references/execution-brief.schema.json)

## Built-in domain packs

| Domain | Adds |
|---|---|
| **Software** | architecture, interfaces, failure modes, testing, deployment checks |
| **Marketing** | audience, offer, channel, measurement, experiment and campaign checks |
| **Product** | user, job, behavior, scope, trade-off and product outcome checks |
| **Research** | question framing, source quality, evidence, uncertainty and reproducibility checks |

Need another field such as finance, operations, legal, sales, branding, or media buying

Use the companion `building-gtd-domain-packs` skill to create a pack without forking the core contract

## GTD CLI

```bash
python scripts/gtd.py doctor
python scripts/gtd.py list-domains
python scripts/gtd.py new-brief --title "Campaign measurement cleanup" --domain marketing --out brief.json
python scripts/gtd.py validate-brief brief.json --root .
python scripts/gtd.py assess-brief brief.json
python scripts/gtd.py render-brief brief.json --out brief.md
python scripts/gtd.py package --out dist
```

## Adapter CLI

Inspect the compatibility registry

```bash
python scripts/adapters.py list
python scripts/adapters.py info cursor
python scripts/adapters.py validate
```

Export one host package

```bash
python scripts/adapters.py export cursor --out dist/adapters
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package
```

Export every non-conditional adapter

```bash
python scripts/adapters.py export-all --out dist/adapters
```

The command exports 16 targets and reports Glama separately until an MCP package exists

## Installation

Universal Agent Skills location

```bash
./install.sh --agents
```

Specific user-level host locations

```bash
./install.sh --target claude
./install.sh --target cursor
./install.sh --target kimi
./install.sh --target grok
./install.sh --target codex
./install.sh --target deepseek
```

Install to all distinct supported user skill roots

```bash
./install.sh --all
```

For project-level or plugin packages, use `scripts/adapters.py export`

## Distribution manifests

```text
plugin.json                       Agent Plugins 1.0.0
.codex-plugin/plugin.json         ChatGPT / Codex plugin
.claude-plugin/plugin.json        Claude plugin
.claude-plugin/marketplace.json   Claude marketplace
kimi.plugin.json                  Kimi Code plugin
skills.sh.json                    skills.sh repository metadata
adapters/registry.json            GTD compatibility registry
```

## Verification

CI verifies deterministic repository behavior across Python 3.10, 3.11, 3.12, and 3.13

- GTD core tests
- Execution Brief validation and Ready/Done assessment
- domain pack contracts
- skill catalog assets
- current OpenAI skill metadata
- adapter registry and manifest validation
- host export smoke tests
- standalone skill packaging
- installer syntax

Behavioral model evals remain separate from deterministic tests

Passing Python tests proves package invariants, not that every model will follow every workflow perfectly under every prompt

## Repository map

```text
plugin.json
.codex-plugin/
.claude-plugin/
kimi.plugin.json
skills.sh.json
adapters/
  registry.json
skills/
  get-things-done/
  building-gtd-domain-packs/
scripts/
  gtd.py
  adapters.py
docs/
evals/
examples/
tests/
```

## Docs

- [Docs index](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Host adapters](docs/adapters.md)
- [Execution Brief](docs/execution-brief.md)
- [Building domain packs](docs/domain-packs.md)
- [Evaluation](docs/evaluation.md)

## Design principle

> Never confuse thinking with progress

A useful agent should make uncertainty visible, move the smallest consequential thing forward, and prove what changed

## License

MIT

Maintained by [Mamdouh Aboammar](https://github.com/imMamdouhaboammar)
