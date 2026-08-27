# Host adapters and distribution

Get Things Done keeps one canonical `skills/` tree and adapts packaging, discovery, and install paths around it.

The core workflow must not fork by host.

## Support levels

| Level | Meaning |
|---|---|
| `native-standard` | The repository already matches an open standard consumed directly by compatible hosts |
| `first-class` | GTD ships and tests a host-specific manifest, installer, package-manager source, or project layout |
| `portable` | The host consumes the canonical Agent Skill without a GTD-specific runtime wrapper |
| `authoring-bridge` | The integration helps compile or author skills but is not itself a runtime host |
| `conditional` | Support is only claimed when an additional required component exists |

## Portability contract

Agent Skills is the canonical compatibility boundary. Any agent that consumes the Agent Skills standard can use GTD through the standard skills layout without requiring a dedicated behavior fork.

A named first-class adapter means GTD additionally verifies a host-specific path, manifest, or distribution surface. It does not mean unnamed agents are unsupported when they already consume the standard.

## Compatibility matrix

| Target | Support | GTD delivery |
|---|---|---|
| Agent Skills / compatible agents | native-standard | canonical `skills/<name>/SKILL.md` |
| Agent Plugins | native-standard | root `plugin.json` + `skills/` |
| Claude AI Skills | portable | Agent Skills bundle |
| Claude Code | first-class | `.claude-plugin/plugin.json` + canonical skills |
| Claude Marketplace | first-class | `.claude-plugin/marketplace.json` |
| Claude Cowork | first-class | Claude plugin/skill package |
| ChatGPT Web | first-class | `.codex-plugin/plugin.json` + canonical skills |
| ChatGPT Work | first-class | same OpenAI plugin package |
| ChatGPT Plugin | first-class | same OpenAI plugin package |
| Codex | first-class | OpenAI plugin + `.agents/skills` fallback |
| Cursor | first-class | `.cursor/skills` with `.agents/skills` portability fallback |
| Kimi Code | first-class | `kimi.plugin.json` and `.kimi-code/skills` |
| Grok Build | first-class | `.grok/skills` |
| DeepSeek DeepCode | first-class | `.deepcode/skills` |
| Homebrew | first-class | HEAD Formula + packaged canonical skills |
| Shell installer | first-class | named host roots + `--target-path` for compatible agents |
| skills.sh | first-class | root `skills.sh.json` over canonical skills |
| Contentful Skill Kit | authoring-bridge | canonical skills stay source of truth; Skill Kit is used only when a typed compiled workflow is desired |
| Glama | conditional | requires an actual `mcp.json`; GTD refuses to manufacture registry metadata without an MCP server |

## Companion interoperability

Plugin Autopilot, Plugin Eval, Superpowers, ArmorCodex, and Context7 are not host adapters. GTD records them in `adapters/companions.json` so role boundaries are testable without pretending GTD owns their runtime, prompts, evaluation logic, security semantics, or MCP implementation.

| Companion | Relationship | Companion role |
|---|---|---|
| Plugin Autopilot | complementary | agent orchestration |
| Plugin Eval | complementary | plugin and skill evaluation |
| Superpowers | complementary | development methodology |
| ArmorCodex | complementary | security review |
| Context7 | optional | documentation retrieval over MCP |

Companion output can become evidence, context, a blocker, or follow-up work. It does not override repository governance or GTD exit conditions.

## CLI

```bash
python scripts/adapters.py list
python scripts/adapters.py info cursor
python scripts/adapters.py companions
python scripts/adapters.py interop
python scripts/adapters.py interop context7
python scripts/adapters.py validate
python scripts/adapters.py export cursor --out dist/adapters
python scripts/adapters.py export homebrew --out dist/adapters
python scripts/adapters.py export shell --out dist/adapters
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package
python scripts/adapters.py export-all --out dist/adapters
```

`export-all` intentionally reports conditional adapters separately.

## Why adapters are thin

Host packaging changes faster than the GTD reasoning contract.

The adapter layer owns only discovery location, manifest shape, installation/package layout, host-specific metadata, and conformance checks.

It must not duplicate the Execution Brief contract, domain packs, readiness rules, or completion semantics.

## Why companions are separate

A tool can work with GTD without being a place where GTD is installed. Keeping companions separate prevents three common errors:

1. claiming runtime support for a tool that is actually an evaluator, orchestrator, security reviewer, or documentation source;
2. copying another project's behavior into GTD and creating two sources of truth;
3. turning optional tooling into a mandatory GTD dependency.

## Adding another host

1. Verify the host's current official skill/plugin contract.
2. Add one registry entry.
3. Reuse the canonical `skills/` tree.
4. Add an export strategy only if the host needs a distinct layout.
5. Add at least one positive path test and one limitation/negative test.
6. Run `python scripts/adapters.py validate`.
7. Run `python scripts/adapters.py export-all --out <temp>`.

Do not mark a host first-class because it can read Markdown manually.

## Adding another companion

1. Confirm the tool complements GTD but is not itself an installation host.
2. Define a narrow companion role and explicit ownership boundary.
3. Add guardrails that prevent authority or behavior from silently moving between systems.
4. Do not add host manifest, project path, or export fields.
5. Add conformance coverage and run `python scripts/adapters.py validate`.

See `docs/installation.md` for installation recipes.
