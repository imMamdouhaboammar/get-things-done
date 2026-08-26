<div align="center">

# Get Things Done

### Your idea is not a task yet

Turn messy intent into a clear work model, identify the real blocker, execute the next useful action, and require evidence before calling anything done

[![CI](https://github.com/imMamdouhaboammar/get-things-done-skillpack/actions/workflows/ci.yml/badge.svg)](https://github.com/imMamdouhaboammar/get-things-done-skillpack/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)

**Agent Skill Pack · Execution Briefs · Domain Packs · Deterministic Readiness & Done checks**

</div>

## The problem

Most ideas do not arrive as clean requirements

They arrive like this

> I want something around AI agents that helps marketing teams work faster, maybe a plugin, maybe a workflow, and it should understand the brand and somehow manage execution too

A normal assistant can turn that into a long plan

That is not the same as making the work executable

**Get Things Done focuses on the gap between "I have an idea" and "there is a next action we can perform and verify"**

It separates what is known from what is assumed, finds the current blocker, decides whether the work needs clarification, research, decomposition, a decision, validation, execution, or verification, then keeps the state in a reusable Execution Brief

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

## A small example

**Input**

> I want to build a tool that makes AI-generated landing pages feel less generic and more on-brand

**Instead of jumping straight to a backlog, GTD models the work**

```yaml
outcome: AI-generated landing pages consistently follow a supplied brand direction
current_mode: validate
facts:
  - the requested output is a landing page
assumptions:
  - brand guidance can be represented as reusable constraints and examples
open_decisions:
  - whether the first version targets code generation, visual review, or both
success_criteria:
  - independent runs can be reviewed against the same brand checks
next_action: test three candidate brand-context representations on the same page brief
```

The point is not the YAML

The point is that the next move is now explicit and testable

## Core ideas

### 1. Knowledge has types

GTD keeps four categories distinct

| Type | Meaning |
|---|---|
| **Fact** | supported by evidence or an explicit user statement |
| **Assumption** | reversible belief accepted so work can continue |
| **Decision** | selected option that changes what will be done |
| **Unknown** | information that is still unresolved |

This prevents a common agent failure where an unanswered question quietly becomes a made-up fact

### 2. One active blocker at a time

GTD does not run a giant generic workflow on every request

It routes the current blocker to one mode

`clarify` · `research` · `decompose` · `decide` · `validate` · `model` · `execute` · `verify`

After each cycle, it classifies again

### 3. Ready and Done are different gates

**Definition of Ready** asks whether the next action can be performed safely and meaningfully

**Definition of Done** asks whether the promised result exists and has supporting evidence

A polished plan can pass neither

A generated artifact can be ready for verification without being done

### 4. Progress must leave evidence

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

The JSON Schema lives at [`skills/get-things-done/references/execution-brief.schema.json`](skills/get-things-done/references/execution-brief.schema.json)

## Built-in domain packs

| Domain | Adds |
|---|---|
| **Software** | architecture, interfaces, failure modes, testing, deployment checks |
| **Marketing** | audience, offer, channel, measurement, experiment and campaign checks |
| **Product** | user, job, behavior, scope, trade-off and product outcome checks |
| **Research** | question framing, source quality, evidence, uncertainty and reproducibility checks |

Need another field such as finance, operations, legal, sales, branding, or media buying

Use the companion `building-gtd-domain-packs` skill to create a pack without forking the core contract

## CLI

The included Python CLI makes the work model inspectable outside the conversation

```bash
python scripts/gtd.py doctor
python scripts/gtd.py list-domains
python scripts/gtd.py new-brief --title "Campaign measurement cleanup" --domain marketing --out brief.json
python scripts/gtd.py validate-brief brief.json --root .
python scripts/gtd.py assess-brief brief.json
python scripts/gtd.py render-brief brief.json --out brief.md
python scripts/gtd.py package --out dist
```

### `assess-brief`

`assess-brief` applies deterministic structural checks for the core Ready and Done gates

```text
READY: NO
- ready gap: success criteria are empty
- ready gap: next executable action is missing
DONE: NO
- done gap: deliverables are empty
- done gap: verification evidence is empty
```

It does not replace domain review or human judgment

It catches obvious state claims that the brief itself cannot support

## Installation

### Universal agent skills directory

```bash
./install.sh --agents
```

### Claude Code skills directory

```bash
./install.sh --claude
```

### Both

```bash
./install.sh --both
```

### Standalone archives

```bash
python scripts/gtd.py package --out dist
```

This produces

```text
dist/get-things-done.zip
dist/building-gtd-domain-packs.zip
```

Each archive is self-contained for hosts that accept folder-based skill bundles

## Repository map

```text
skills/
├── get-things-done/
│   ├── SKILL.md
│   ├── domains/
│   ├── references/
│   ├── templates/
│   ├── scripts/
│   └── agents/
└── building-gtd-domain-packs/
    ├── SKILL.md
    ├── references/
    └── templates/

docs/
├── README.md
├── architecture.md
├── quickstart.md
├── domain-packs.md
└── evaluation.md

evals/
examples/
tests/
```

## Docs

- [Docs index](docs/README.md)
- [Architecture](docs/architecture.md)
- [Quickstart](docs/quickstart.md)
- [Building domain packs](docs/domain-packs.md)
- [Evaluation approach](docs/evaluation.md)

## Verification status

The repository CI checks the deterministic parts of the pack across supported Python versions

- skill file and reference integrity
- domain pack contract shape
- Execution Brief validation
- CLI behavior
- standalone packaging
- catalog assets
- install script syntax

Behavioral agent eval cases are included under [`evals/`](evals/) and are intentionally reported separately from deterministic test coverage

That distinction matters because passing Python tests does not prove that every model will follow a skill correctly under every prompt

## Design principle

> Never confuse thinking with progress

A useful agent should make uncertainty visible, move the smallest consequential thing forward, and prove what changed

## License

MIT

Maintained by [Mamdouh Aboammar](https://github.com/imMamdouhaboammar)
