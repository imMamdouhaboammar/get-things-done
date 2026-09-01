<div align="center">

# Get Things Done

### Your idea is not a task yet

Turn messy intent into a clear work model · identify the real blocker · execute the next useful action · require evidence before calling anything done

[![CI](https://github.com/imMamdouhaboammar/get-things-done/actions/workflows/ci.yml/badge.svg)](https://github.com/imMamdouhaboammar/get-things-done/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.4.0-111111.svg)](docs/changelog-v1.4.md)
[![Agent Plugins 1.0](https://img.shields.io/badge/Agent_Plugins-1.0-111111.svg)](https://agent-plugins.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-111111.svg)](LICENSE)

**One canonical GTD core · Agent Skills · Agent Plugins · Host adapters · Execution Briefs · Domain Packs · Evidence-based completion**

</div>

---

## Table of contents

- [The problem](#the-problem)
- [What GTD does](#what-gtd-does)
- [Core ideas](#core-ideas)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Domain packs](#domain-packs)
- [Execution Brief](#execution-brief)
- [CLI reference](#cli-reference)
- [Supported surfaces](#supported-surfaces)
- [Companion tools](#companion-tools)
- [Architecture](#architecture)
- [Repository map](#repository-map)
- [Verification](#verification)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## The problem

Most ideas do not arrive as clean requirements.

They arrive half-formed, mixed with assumptions, missing decisions, unclear scope, and several possible next moves.

A normal assistant can turn that into a long plan. That is not the same as making the work **executable**.

> **Get Things Done focuses on the gap between "I have an idea" and "there is a next action we can perform and verify"**

It separates what is known from what is assumed, identifies the current blocker, decides whether the work needs clarification, research, decomposition, a decision, validation, execution, or verification — then keeps the state in a reusable Execution Brief.

---

## What GTD does

```text
Messy idea
   ↓
Capture outcome (separate result from proposed solution)
   ↓
Classify current blocker
   ↓  clarify · research · decompose · decide · validate · model · execute · verify
Resolve the current frontier
   ↓
Update Execution Brief
   ↓
Definition of Ready gate
   ↓
Act (if execution was requested and tools are available)
   ↓
Review through Outcome · Domain · Execution · Verification lenses
   ↓
Collect evidence
   ↓
Done  ← or loop back to next action
```

The core behavior is **intentionally domain-independent**. Software, marketing, product, and research are added through [domain packs](#domain-packs) that inherit the same decision, readiness, evidence, and handoff rules.

---

## Core ideas

### Knowledge has types

| Type | Meaning |
|---|---|
| **Fact** | supported by evidence or an explicit user statement |
| **Assumption** | reversible belief accepted so work can continue |
| **Decision** | selected option that changes what will be done |
| **Unknown** | information that is still unresolved |

This prevents an unanswered question from quietly becoming a made-up fact.

### One active blocker at a time

GTD routes the current blocker to exactly one working mode per cycle:

`clarify` · `research` · `decompose` · `decide` · `validate` · `model` · `execute` · `verify`

After each meaningful cycle, it classifies again.

### Ready and Done are different gates

**Definition of Ready** — can the next action be performed safely and meaningfully?  
**Definition of Done** — does the promised result exist with supporting evidence?

A polished plan can pass neither.

### Progress must leave evidence

A useful cycle produces at least one concrete result:

- a decision settled
- an artifact created or changed
- an external action executed
- verification evidence collected

More analysis alone does not count as execution.

---

## Quick start

**Prerequisites:** Python 3.10+, `pyyaml` (installed automatically with the package).

### 60-second setup

```bash
# 1. Clone and install to the universal Agent Skills location
git clone https://github.com/imMamdouhaboammar/get-things-done.git
cd get-things-done
./install.sh --agents

# 2. Verify the install
python scripts/gtd.py doctor

# 3. Create your first Execution Brief
python scripts/gtd.py new-brief \
  --title "Brand-aware landing page generation" \
  --domain software \
  --out brief.json

# 4. Validate its structure
python scripts/gtd.py validate-brief brief.json --root .

# 5. Assess Ready / Done gates
python scripts/gtd.py assess-brief brief.json

# 6. Render to human-readable Markdown
python scripts/gtd.py render-brief brief.json --out brief.md

# 7. Export Markdown, JSON, TOON, Mermaid, and graph JSON
python scripts/gtd.py export-brief brief.json --format all --out dist/brief
```

Start with the idea **as you actually have it**. GTD will make the outcome, facts, assumptions, decisions, and next action explicit without requiring a perfectly formed prompt first.

See [docs/quickstart.md](docs/quickstart.md) for the full five-step walkthrough.

---

## Installation

GTD ships one canonical `skills/` tree and multiple thin adapters around it. Choose the path that matches your agent host.

### Universal (fastest)

```bash
git clone https://github.com/imMamdouhaboammar/get-things-done.git
cd get-things-done
./install.sh --agents        # → ~/.agents/skills
```

Any custom Agent Skills root:

```bash
./install.sh --target-path "$HOME/.my-agent/skills"
```

### Via skills.sh (all detected agents)

```bash
npx skills add imMamdouhaboammar/get-things-done --all
```

Install for specific agents:

```bash
npx skills add imMamdouhaboammar/get-things-done -g -a claude-code -a codex -a cursor -y
```

Update installed skills later:

```bash
npx skills update
```

### Named host targets

```bash
./install.sh --target claude        # → ~/.claude/skills
./install.sh --target cursor        # → ~/.cursor/skills
./install.sh --target kimi          # → ~/.kimi-code/skills
./install.sh --target grok          # → ~/.grok/skills
./install.sh --target codex         # → ~/.agents/skills
./install.sh --target deepseek      # → ~/.agents/skills
./install.sh --target antigravity   # → ~/.gemini/config/skills
```

Install to all distinct supported roots at once:

```bash
./install.sh --dry-run --all     # preview first
./install.sh --all               # install
./install.sh --all --force       # overwrite existing installs
```

### Homebrew (HEAD)

```bash
brew install --HEAD ./Formula/get-things-done.rb
gtd doctor
```

> **Note:** The Homebrew formula is HEAD-only until a versioned release artifact is published.

### Full installation guide

See [docs/installation.md](docs/installation.md) for per-host export commands, adapter packaging, and release artifact verification.

---

## Domain packs

The core skill is domain-independent. Load a domain pack when the task clearly belongs to a supported field.

| Domain | Adds |
|---|---|
| **Software** | architecture, interfaces, failure modes, testing, deployment checks |
| **Marketing** | audience, offer, channel, measurement, experiment and campaign checks |
| **Product** | user, job, behavior, scope, trade-off and product outcome checks |
| **Research** | question framing, source quality, evidence, uncertainty and reproducibility checks |
| **Advisory** | root dilemmas, reversibility, strategic trade-offs, founder alignment, decision frameworks |
| **Data & AI** | data pipelines, ML experiments, model training, evaluation harnesses, reproducibility |
| **Design & UX** | user observation, prototype fidelity matching, design systems, accessibility gates |
| **Operations** | incident triage, blast-radius-first analysis, rollback readiness, runbooks, MTTD/MTTR |
| **Legal & Compliance** | jurisdiction bounding, regulatory gap analysis, policy authoring, authority boundaries |

Need a custom domain (finance, sales, branding, media buying)?  
Use the companion [`building-gtd-domain-packs`](skills/building-gtd-domain-packs/) skill to create a pack without forking the core contract.

See [docs/domain-packs.md](docs/domain-packs.md) for authoring guidance.

---

## Execution Brief

Substantial work is represented as a portable **Execution Brief** — a durable interface between thinking, execution, verification, and handoff.

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

The brief is intentionally useful even when the next agent does not have the original conversation history.

- **Schema:** [`skills/get-things-done/references/execution-brief.schema.json`](skills/get-things-done/references/execution-brief.schema.json)
- **Examples:** [`examples/software-brief.json`](examples/software-brief.json) · [`examples/marketing-brief.json`](examples/marketing-brief.json)
- **Full reference:** [docs/execution-brief.md](docs/execution-brief.md)

---

## CLI reference

### GTD core

```bash
python scripts/gtd.py doctor                                    # repository health check
python scripts/gtd.py list-domains                              # list registered domain packs
python scripts/gtd.py new-brief --title "…" --domain software \
  --out brief.json                                              # create a new brief
python scripts/gtd.py validate-brief brief.json --root .        # schema validation
python scripts/gtd.py assess-brief brief.json                   # Ready/Done gate assessment
python scripts/gtd.py render-brief brief.json --out brief.md    # backward-compatible Markdown render
python scripts/gtd.py export-brief brief.json --format all \
  --out dist/brief                                              # MD, JSON, TOON, Mermaid, graph JSON
python scripts/gtd.py package --out dist                        # build distribution package
```

### Adapter CLI

```bash
# Status and discovery
python scripts/adapters.py status                               # ecosystem status across all 19 targets
python scripts/adapters.py list                                 # list adapter registry entries
python scripts/adapters.py capabilities                         # capability matrix
python scripts/adapters.py query --capability skills            # filter by capability
python scripts/adapters.py info cursor                          # single adapter detail
python scripts/adapters.py validate                             # validate all contracts

# Companion interoperability
python scripts/adapters.py companions                           # list all companion profiles
python scripts/adapters.py interop context7                     # inspect specific companion boundary

# Single-target export
python scripts/adapters.py export cursor --out dist/adapters
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package
python scripts/adapters.py export homebrew --out dist/adapters
python scripts/adapters.py export shell --out dist/adapters

# Export everything (18 non-conditional targets + machine-readable report)
python scripts/adapters.py export-all \
  --out dist/adapters --package --report dist/export-report.json
```

### Release artifact verification

```bash
python scripts/release_checksums.py dist/adapters \
  --verify dist/adapters/SHA256SUMS
```

---

## Supported surfaces

GTD tracks **20 adapter contracts**. The label describes the package/export contract GTD verifies — not a claim that every vendor has approved the package in its public marketplace.

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
| Antigravity / Gemini CLI | First-class adapter | `.gemini/config/skills` |
| Homebrew | First-class distribution | HEAD Formula + packaged canonical skills |
| Shell Installer | First-class distribution | Multi-host `install.sh` with named roots |
| Vercel skills.sh | First-class distribution metadata | `skills.sh.json` |
| Contentful Skill Kit | Authoring bridge | typed workflow compilation |
| Glama | Conditional | enabled only when GTD ships a real `mcp.json` |

Glama is not marked native today because GTD does not currently ship an MCP server. The adapter CLI fails closed rather than manufacturing registry support that does not exist.

See [docs/adapters.md](docs/adapters.md) for full adapter documentation.

---

## Companion tools

GTD tracks 5 companion tools in [`adapters/companions.json`](adapters/companions.json) with strict separation of concerns. Companions participate in the engineering workflow without becoming GTD hosts or runtime dependencies.

| Companion | Role | GTD boundary |
|---|---|---|
| **Plugin Autopilot** | agent orchestration | Autopilot schedules agent runs; GTD owns work state, brief, and done contract |
| **Plugin Eval** | plugin and skill evaluation | Eval findings enter GTD as verification evidence; cannot bypass exit gates |
| **Superpowers** | development methodology | Superpowers guides TDD and review disciplines; GTD wraps high-level brief |
| **ArmorCodex** | security review | Security findings enter GTD as blockers/evidence; severity is never rewritten |
| **Context7** | documentation retrieval over MCP | Context7 provides external docs context; local code and repo governance win |

Inspect companion boundaries:

```bash
python scripts/adapters.py companions
python scripts/adapters.py interop context7
```

---

## Architecture

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

The `skills/` tree is the **single source of truth**. Adapters own only discovery paths, manifests, packaging, and compatibility checks — they cannot fork the GTD decision model or create a parallel version of the workflow.

GTD deliberately separates two layers:

| Layer | What it covers |
|---|---|
| **Deterministic** | JSON schema validation, manifest integrity, SemVer alignment, domain collision checks, Ready/Done structural assessment, adapter export, SHA-256 checksum generation |
| **Model-driven** | interpreting messy intent, choosing the active blocker mode, evaluating trade-offs, field-specific review |

The CLI does not replace contextual judgment, and the skill does not pretend model judgment is deterministic.

See [docs/architecture.md](docs/architecture.md) for the full runtime model, state machine, and adapter tier descriptions.

---

## Repository map

```text
plugin.json                         Agent Plugins 1.0.0 manifest
.codex-plugin/                      ChatGPT / Codex plugin manifest
.claude-plugin/                     Claude plugin + marketplace catalog
kimi.plugin.json                    Kimi Code plugin manifest
skills.sh.json                      skills.sh discovery metadata
Formula/
  get-things-done.rb                Homebrew HEAD Formula
install.sh                          Portable multi-host shell installer
adapters/
  registry.json                     GTD adapter compatibility registry
  registry.schema.json              Adapter registry JSON schema
  companions.json                   Companion interoperability registry
  companions.schema.json            Companion registry JSON schema
skills/
  get-things-done/                  Core GTD skill
    SKILL.md
    domains/                        Built-in domain packs (software, marketing, product, research, advisory)
    references/                     Schemas and core contract
    templates/                      Brief templates
  building-gtd-domain-packs/        Companion skill for authoring custom packs
scripts/
  gtd.py                            GTD core CLI
  adapters.py                       Adapter CLI
  package_skills.py                 Skill packaging
  release_checksums.py              Deterministic SHA-256 release checksums
  catalog_stylist.py                Catalog metadata tooling
docs/                               Extended documentation
evals/                              Behavioral model evaluations
examples/                           Example Execution Briefs
tests/                              Deterministic test suite (24 modules)
```

---

## Verification

CI verifies deterministic repository behavior across **Python 3.10, 3.11, 3.12, and 3.13**:

- Python bytecode compilation (`python -m compileall scripts tests`)
- GTD core tests and CLI wrapper behavior
- Execution Brief validation and Ready/Done assessment
- Domain pack contracts and collision rules
- Skill catalog assets and OpenAI skill metadata
- Adapter registry and manifest validation
- Companion contract schema conformance and boundary checks
- Host export and packaging smoke tests
- Deterministic SHA-256 release checksum generation and verification
- Installer syntax and Bash 3.2 compatibility
- Homebrew formula syntax validation
- Cross-manifest SemVer and canonical identity alignment

Behavioral model evals remain separate from deterministic tests — see [docs/evaluation.md](docs/evaluation.md).

Run the full suite locally:

```bash
pip install -e ".[dev]"
pytest
```

---

## Documentation

| Document | Contents |
|---|---|
| [docs/README.md](docs/README.md) | Docs index |
| [docs/quickstart.md](docs/quickstart.md) | First brief in five steps |
| [docs/architecture.md](docs/architecture.md) | Runtime model, state machine, adapter tiers |
| [docs/adapters.md](docs/adapters.md) | Full host adapter and companion documentation |
| [docs/execution-brief.md](docs/execution-brief.md) | Brief schema, lifecycle, and handoff contract |
| [docs/domain-packs.md](docs/domain-packs.md) | Built-in packs and authoring guide |
| [docs/installation.md](docs/installation.md) | Per-host installation and export commands |
| [docs/evaluation.md](docs/evaluation.md) | Behavioral evaluation approach |
| [docs/changelog-v1.3.md](docs/changelog-v1.3.md) | v1.3 release notes |

---

## Contributing

Issues and pull requests are welcome. Before opening a PR:

1. Run `python scripts/gtd.py doctor` and `python scripts/adapters.py validate` to confirm the registry is healthy.
2. Run `pytest` to confirm all deterministic tests pass.
3. If adding a host adapter, update `adapters/registry.json` and add a corresponding export test in `tests/`.
4. If authoring a new domain pack, use the [`building-gtd-domain-packs`](skills/building-gtd-domain-packs/) skill — do not modify the core contract.

---

## Design principle

> Never confuse thinking with progress

A useful agent should make uncertainty visible, move the smallest consequential thing forward, and prove what changed.

---

## License

MIT — see [LICENSE](LICENSE)

Maintained by [Mamdouh Aboammar](https://github.com/imMamdouhaboammar)
