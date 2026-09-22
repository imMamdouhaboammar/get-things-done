# Get Things Done Docs

Use these docs based on what you are trying to do.

| Guide | Use it for |
|---|---|
| [Quickstart](quickstart.md) | Start from a messy idea and produce a usable Execution Brief |
| [Installation](installation.md) | Install GTD across universal Agent Skills, Claude, ChatGPT, Codex, Cursor, Kimi, Grok, DeepSeek, Homebrew, shell, skills.sh, Skill Kit, and conditional Glama paths |
| [Updating](updating.md) | Refresh installed GTD Skills safely from the latest release or current main commit |
| [Execution Brief](execution-brief.md) | Understand the durable work artifact and its Ready and Done relationship |
| [Validation](validation.md) | Understand schema ownership, version routing, migration safety, and assessment exit codes |
| [Deliberation](deliberation.md) | Challenge messy framing, refresh current evidence, pass the Direction Gate, and create backlog work |
| [Architecture](architecture.md) | Understand the core contract, state model, domain packs, and deterministic boundaries |
| [Host adapters](adapters.md) | Understand multi-host packaging, install paths, support levels, adapter exports, and companion interoperability |
| [Domain packs](domain-packs.md) | Adapt GTD to a new field without copying or weakening the core |
| [Evaluation](evaluation.md) | Run repository checks and design behavioral agent evaluations |
| [CI quality](ci.md) | Understand runtime support, package smoke, lint, coverage policy, permissions, and time bounds |
| [v1.3 change notes](changelog-v1.3.md) | Review multi-host adapter interoperability, companion contracts, and packaging updates |
| [v1.1 change notes](changelog-v1.1.md) | Review core contract, Execution Brief, and domain pack foundations |

## Reference contracts

The runtime-facing contracts live next to the main skill or in the adapter registry.

- [`core-contract.md`](../skills/get-things-done/references/core-contract.md)
- [`execution-brief.schema.json`](../skills/get-things-done/references/execution-brief.schema.json)
- [`domain-pack-spec.md`](../skills/get-things-done/references/domain-pack-spec.md)
- [`problem-model.schema.json`](../skills/gtd-deliberation/references/problem-model.schema.json)
- [`backlog.schema.json`](../skills/gtd-deliberation/references/backlog.schema.json)
- [`adapters/registry.json`](../adapters/registry.json)
- [`adapters/registry.schema.json`](../adapters/registry.schema.json)
- [`adapters/companions.json`](../adapters/companions.json)
- [`adapters/companions.schema.json`](../adapters/companions.schema.json)

The files under `docs/superpowers/` preserve design and implementation history. They are project records rather than end-user documentation.
