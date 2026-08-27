# Get Things Done Docs

Use these docs based on what you are trying to do

| Guide | Use it for |
|---|---|
| [Quickstart](quickstart.md) | Start from a messy idea and produce a usable Execution Brief |
| [Execution Brief](execution-brief.md) | Understand the durable work artifact and its Ready and Done relationship |
| [Architecture](architecture.md) | Understand the core contract, state model, domain packs, and deterministic boundaries |
| [Host adapters](adapters.md) | Understand multi-host packaging, install paths, support levels, and adapter exports |
| [Domain packs](domain-packs.md) | Adapt GTD to a new field without copying or weakening the core |
| [Evaluation](evaluation.md) | Run repository checks and design behavioral agent evaluations |
| [v1.1 change notes](changelog-v1.1.md) | Review the behavior and documentation changes in this release candidate |

## Reference contracts

The runtime-facing contracts live next to the main skill

- [`core-contract.md`](../skills/get-things-done/references/core-contract.md)
- [`execution-brief.schema.json`](../skills/get-things-done/references/execution-brief.schema.json)
- [`domain-pack-spec.md`](../skills/get-things-done/references/domain-pack-spec.md)
- [`adapters/registry.json`](../adapters/registry.json)

The files under `docs/superpowers/` preserve design and implementation history. They are project records rather than end-user documentation
