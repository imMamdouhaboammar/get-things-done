# CI Quality Contract

A green GTD CI run should describe the repository that users can actually install and execute.

## Runtime support

CI tests every Python version advertised in project metadata:

- 3.10
- 3.11
- 3.12
- 3.13
- 3.14

Removing a version from the matrix requires changing the advertised support policy in the same change.

## Installation path

CI installs the project through its own package metadata:

```bash
python -m pip install -e ".[dev]"
```

It then invokes `gtd --help` from the installed console entrypoint before running repository/Skill-specific commands. `doctor` remains a separate repository/Skill distribution check because the Python console package intentionally contains the CLI package rather than duplicating the canonical Skill payload.

This catches packaging and console-entrypoint drift that a manual dependency install cannot detect.

## Static quality

Ruff is a blocking CI gate over:

- `scripts/`
- `tests/`
- `skills/get-things-done/scripts/`

The repository should fix or explicitly configure lint rules rather than silently skipping the configured tool.

## Coverage policy

GTD does **not** currently use a numeric line-coverage release gate.

This is intentional, not accidental. The core quality contract is dominated by:

- CLI subprocess behavior
- JSON/schema conformance
- adapter/export content equivalence
- installer/release failure paths
- security regressions
- behavioral evaluation corpora

A percentage threshold without a measured baseline would create a number before it creates evidence.

`pytest-cov` is therefore not a declared development dependency today. If numeric code coverage becomes a release criterion, introduce it with a measured baseline, scope definition, and explicit threshold in the same change.

## Workflow authority and time bounds

CI has read-only repository content permission:

```yaml
permissions:
  contents: read
```

Each matrix job has an explicit timeout. CI must not depend on repository-write permissions or production secrets.

## Distribution gates

The matrix also verifies:

- canonical CLI doctor
- schema and Skill invariants
- all non-conditional adapter exports
- Antigravity/Gemini export path
- release checksum generation and verification
- standalone Skill packages
- shell installer syntax
- Homebrew formula syntax
- focused security regressions

Conditional integrations remain fail-closed.
