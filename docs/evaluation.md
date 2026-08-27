# Evaluation

GTD separates deterministic repository verification from behavioral agent evaluation

They answer different questions

## Deterministic tests

The Python suite checks things the repository can prove directly

- required skill files exist
- skill frontmatter is discoverable
- core invariants remain present
- domain packs follow the required contract
- Execution Brief JSON is structurally valid
- CLI commands behave as expected
- example briefs validate
- packaging produces self-contained archives
- catalog assets remain valid

Run

```bash
pytest -v
python scripts/catalog_stylist.py --validate
python scripts/gtd.py doctor
```

## Evaluation suites

### 1. Skill behavioral evals (`evals/cases.jsonl`)

The cases under [`evals/cases.jsonl`](../evals/cases.jsonl) test model behavior that cannot be proven by Python alone:

- messy software idea
- messy marketing idea
- wrong-domain routing
- best effort with no questions
- fake-done pressure

### 2. Adapter conformance evals (`evals/adapter-cases.jsonl`)

The dataset under [`evals/adapter-cases.jsonl`](../evals/adapter-cases.jsonl) verifies expectations and distribution requirements across all **19 adapter contracts**:

- Native standard discovery paths (`skills/`, `plugin.json`)
- Vendor-specific manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `kimi.plugin.json`)
- Package registries (`skills.sh.json`, `Formula/get-things-done.rb`, `install.sh`)
- Boundary enforcement for conditional integrations (Glama fail-closed without `mcp.json`)

### 3. Companion interoperability evals (`evals/interop-cases.jsonl`)

The dataset under [`evals/interop-cases.jsonl`](../evals/interop-cases.jsonl) verifies separation of concerns for all **5 companion profiles**:

- Plugin Autopilot (agent orchestration vs GTD execution brief)
- Plugin Eval (evaluation findings vs GTD exit conditions)
- Superpowers (methodology vs GTD readiness & done semantics)
- ArmorCodex (independent security severity vs GTD evidence routing)
- Context7 (external documentation retrieval vs local code authority)

## Running evaluation verification

```bash
pytest tests/test_adapter_evals.py -v
```

## Release rule

Do not collapse deterministic CI and behavioral evals into one green badge.

A passing CI run means the repository mechanics and adapter contracts pass their checks.

It does not prove every model-host combination follows the skill correctly under every pressure case.

