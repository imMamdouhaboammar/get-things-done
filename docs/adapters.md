# Host adapters and distribution

Get Things Done keeps one canonical `skills/` tree and adapts packaging, discovery, and install paths around it

The core workflow must not fork by host

## Support levels

| Level | Meaning |
|---|---|
| `native-standard` | The repository already matches an open standard consumed directly by compatible hosts |
| `first-class` | GTD ships and tests a host-specific manifest or project layout |
| `portable` | The host consumes the canonical Agent Skill without a GTD-specific runtime wrapper |
| `authoring-bridge` | The integration helps compile or author skills but is not itself a runtime host |
| `conditional` | Support is only claimed when an additional required component exists |

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
| skills.sh | first-class | root `skills.sh.json` over canonical skills |
| Contentful Skill Kit | authoring-bridge | canonical skills stay source of truth; Skill Kit is used only when a typed compiled workflow is desired |
| Glama | conditional | requires an actual `mcp.json`; GTD refuses to manufacture registry metadata without an MCP server |

## CLI

```bash
python scripts/adapters.py list
python scripts/adapters.py info cursor
python scripts/adapters.py validate
python scripts/adapters.py export cursor --out dist/adapters
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package
python scripts/adapters.py export-all --out dist/adapters
```

`export-all` intentionally reports conditional adapters separately

## Why adapters are thin

Host packaging changes faster than the GTD reasoning contract

The adapter layer owns only discovery location, manifest shape, installation/package layout, host-specific metadata, and conformance checks

It must not duplicate the Execution Brief contract, domain packs, readiness rules, or completion semantics

## Adding another host

1. Verify the host's current official skill/plugin contract
2. Add one registry entry
3. Reuse the canonical `skills/` tree
4. Add an export strategy only if the host needs a distinct layout
5. Add at least one positive path test and one limitation/negative test
6. Run `python scripts/adapters.py validate`
7. Run `python scripts/adapters.py export-all --out <temp>`

Do not mark a host first-class because it can read Markdown manually
