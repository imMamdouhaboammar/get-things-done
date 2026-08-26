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

## Behavioral evals

The cases under [`evals/cases.jsonl`](../evals/cases.jsonl) test model behavior that cannot be proven by Python alone

Important pressure classes include

- messy software idea
- messy marketing idea
- wrong-domain routing
- best effort with no questions
- fake-done pressure

A useful behavioral evaluation records

1. model and host
2. clean context or prior context state
3. exact skill version
4. input case
5. expected invariants
6. observed output
7. pass, partial, or fail
8. failure reason

## Release rule

Do not collapse deterministic CI and behavioral evals into one green badge

A passing CI run means the repository mechanics pass their checks

It does not prove every model-host combination follows the skill correctly under every pressure case
