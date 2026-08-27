# Installation guide

Get Things Done ships one canonical Agent Skills tree and multiple thin adapters around it. Choose the installation path that matches the host you actually use.

## Fastest universal install

For agents that support the Agent Skills convention, install to the universal user root:

```bash
git clone https://github.com/imMamdouhaboammar/get-things-done.git
cd get-things-done
./install.sh --agents
```

This installs both canonical skills under `~/.agents/skills`.

For an agent with a different Agent Skills root:

```bash
./install.sh --target-path "$HOME/.my-agent/skills"
```

The custom path is the portability escape hatch for agents that consume Agent Skills but do not have a dedicated GTD adapter yet.

## All agents through skills.sh

The current `skills` CLI supports Claude Code, Codex, Cursor, Kimi Code CLI, and many other agents. To install both GTD skills to every agent detected by the CLI:

```bash
npx skills add imMamdouhaboammar/get-things-done --all
```

To install globally for one or more explicit agents:

```bash
npx skills add imMamdouhaboammar/get-things-done -g -a claude-code -a codex -a cursor -y
```

To refresh installed skills later:

```bash
npx skills update
```

This is the preferred broad compatibility path when the target agent is already supported by the open Agent Skills ecosystem. GTD's own `--target-path` remains available for agents with custom skill roots.

## Shell installer

Named targets are available for the user-level roots GTD verifies:

```bash
./install.sh --target codex
./install.sh --target claude
./install.sh --target cursor
./install.sh --target kimi
./install.sh --target grok
./install.sh --target deepseek
```

Install all distinct supported user roots known to GTD's shell installer:

```bash
./install.sh --all
```

Existing GTD skill directories are not overwritten unless you opt in:

```bash
./install.sh --all --force
```

## Claude AI Skills and Claude Code

Direct skill install:

```bash
./install.sh --target claude
```

This writes the canonical skills to `~/.claude/skills`.

For Claude Code plugin packaging or a Claude Marketplace-compatible bundle:

```bash
python scripts/adapters.py export claude-code --out dist/adapters --package
python scripts/adapters.py export claude-marketplace --out dist/adapters --package
```

The exported package includes the canonical skills and `.claude-plugin` metadata. Marketplace metadata is packaging support, not a claim that a marketplace has approved or listed the package.

## Claude Cowork

Export the Claude package:

```bash
python scripts/adapters.py export claude-cowork --out dist/adapters --package
```

GTD keeps the same skills and execution contract used by Claude Code. It does not maintain a separate Cowork behavior fork.

## ChatGPT Web, ChatGPT Work, and ChatGPT Plugins

Build the OpenAI plugin package for the required surface:

```bash
python scripts/adapters.py export chatgpt-web --out dist/adapters --package
python scripts/adapters.py export chatgpt-work --out dist/adapters --package
python scripts/adapters.py export chatgpt-plugin --out dist/adapters --package
```

Each package carries `.codex-plugin/plugin.json` plus the canonical skills.

## Codex

For the universal Agent Skills location:

```bash
./install.sh --target codex
```

For a portable plugin bundle:

```bash
python scripts/adapters.py export codex --out dist/adapters --package
```

## Cursor

```bash
./install.sh --target cursor
python scripts/adapters.py export cursor --out dist/adapters --package
```

The export uses `.cursor/skills`. GTD also keeps Agent Skills as the portability baseline.

## Kimi Code

```bash
./install.sh --target kimi
python scripts/adapters.py export kimi --out dist/adapters --package
```

Set `KIMI_CODE_HOME` before running the shell installer if your Kimi Code home is not `~/.kimi-code`.

## Grok

```bash
./install.sh --target grok
python scripts/adapters.py export grok --out dist/adapters --package
```

## DeepSeek

```bash
./install.sh --target deepseek
python scripts/adapters.py export deepseek --out dist/adapters --package
```

The named shell target uses the universal `~/.agents/skills` user root. The exported host bundle preserves the `.deepcode/skills` layout declared by the adapter contract.

## Homebrew

GTD currently ships a HEAD-only Formula. This is intentionally not presented as a stable Homebrew release until a versioned release artifact exists.

From a local checkout:

```bash
brew install --HEAD ./Formula/get-things-done.rb
```

The formula installs the GTD CLI wrapper and canonical skills into Homebrew's managed prefix. Run:

```bash
gtd doctor
```

Use the shell installer when you also want the skills copied into a host's user skill root.

## skills.sh

The repository ships `skills.sh.json` for skills.sh discovery and distribution. The CLI can install directly from the GitHub repository:

```bash
npx skills add imMamdouhaboammar/get-things-done
```

List the skills before installing:

```bash
npx skills add imMamdouhaboammar/get-things-done --list
```

Install all GTD skills to all supported agents without prompts:

```bash
npx skills add imMamdouhaboammar/get-things-done --all
```

Update installed skills later:

```bash
npx skills update
```

Validate the local distribution metadata before publishing or updating it:

```bash
python scripts/adapters.py validate
python scripts/adapters.py export skills-sh --out dist/adapters
```

## Skill Kit

Skill Kit is an authoring bridge, not another GTD runtime. Export the bridge when you want to feed the canonical skills into a typed authoring or compilation workflow:

```bash
python scripts/adapters.py export skill-kit --out dist/adapters
```

Do not maintain a separate Skill Kit copy of GTD behavior.

## Glama

Glama support is conditional because GTD does not currently ship an MCP server. The exporter fails closed unless a real `mcp.json` exists:

```bash
python scripts/adapters.py export glama --out dist/adapters
```

A failure here is expected until GTD has an MCP package worth registering. The adapter must not manufacture an MCP listing for a repository that has no MCP server.

## Companion tools

Plugin Autopilot, Plugin Eval, Superpowers, ArmorCodex, and Context7 are modeled as companion tools rather than host adapters. They may participate in the same workflow without owning GTD's execution contract.

Inspect the machine-readable profiles:

```bash
python scripts/adapters.py companions
python scripts/adapters.py interop
python scripts/adapters.py interop context7
```

Role boundaries:

| Companion | GTD owns | Companion owns |
|---|---|---|
| Plugin Autopilot | execution contract, evidence, exit conditions | agent orchestration |
| Plugin Eval | execution contract and acceptance evidence | plugin or skill evaluation |
| Superpowers | readiness, evidence, done semantics | development methodology |
| ArmorCodex | work state and evidence routing | security review semantics |
| Context7 | decisions and repository-grounded evidence | documentation retrieval over MCP |

Companion output is evidence or context, not automatic authority. Repository governance and the current code remain the source of truth.

## Validate every adapter

```bash
python scripts/adapters.py validate
python scripts/adapters.py export-all --out dist/adapters
```

`export-all` skips conditional adapters whose prerequisites are absent and reports them separately.
