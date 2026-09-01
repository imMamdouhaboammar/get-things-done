# Changelog — v1.4.0

## Skills

### `get-things-done` — maturity upgrade
- Upgraded description with 5 trigger phrasings and explicit negatives (skill-conductor Principle #2)
- Domain quick-select table in body — all 9 packs navigable without loading each domain file
- Core contract load directive made imperative — runs at the start of every cycle
- Output profiles extracted to `references/output-profiles.md` — keeps SKILL.md lean

### `building-gtd-domain-packs` — maturity upgrade
- Upgraded description with 5 trigger phrasings and explicit negatives
- Self-validation checklist added inline — authors can self-grade without loading references
- Load directive for `domain-pack-spec.md` and `core-contract.md` made imperative

## Domain packs (new)

| Pack | Domain |
|---|---|
| `domains/data-ai.md` | Data pipelines, ML experiments, model training, AI system design, LLMs |
| `domains/design-ux.md` | UX research, interaction design, visual design systems, accessibility |
| `domains/operations.md` | Incident response, runbooks, SLO management, postmortems |
| `domains/legal-compliance.md` | Contracts, compliance gap analysis, regulatory mapping, policy authoring |

## Distribution

### npm / npx
- Added `package.json` — enables `npx skills add imMamdouhaboammar/get-things-done`
- Added `.npmignore` — published package contains only skills and manifests

### Antigravity / Gemini CLI
- Added `antigravity`/`gemini-cli` named targets in `install.sh` → `~/.gemini/config/skills`
- Added `antigravity` adapter entry in `adapters/registry.json`

### Claude Marketplace
- Added `.claude-plugin/plugin.json` — Claude Code and Claude Cowork plugin manifest
- Added `.claude-plugin/marketplace.json` — Claude Marketplace bundle

### Codex / OpenAI
- Updated `.codex-plugin/plugin.json` to v1.4.0 with extended domain description

## Eval scaffolding
- Added `evals/evals.json` — skill-conductor–format trigger eval set (6 entries)
- Added `evals/domain-pack-evals.json` — trigger eval set for `building-gtd-domain-packs`

## Registry
- `adapters/registry.json` schema_version bumped to 1.3 (new antigravity adapter)
- Version bumped to 1.4.0 across all manifests
