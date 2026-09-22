# Execution Brief Validation Architecture

GTD uses the published JSON Schemas as the structural source of truth for Execution Briefs.

## Runtime decision

The canonical CLI uses a small dependency-free local validator that implements only the JSON Schema keywords used by GTD's shipped schemas.

This is intentional.

### Why not require `jsonschema` at runtime

GTD is distributed in several ways:

- Python package / Homebrew
- copied Agent Skills directories
- shell installer
- host-specific exported bundles

A copied Skill directory must remain usable offline without assuming that a Python dependency resolver has run.

Making `jsonschema` a mandatory runtime dependency would make schema correctness depend on how the Skill was installed.

### Why not keep the old manual validator

The old validator duplicated a small subset of the schema contract and already drifted from it:

- additional properties could pass
- nested record shapes were only partially checked
- v2 and v1 had separate assumptions

That approach is retired.

### Chosen model

The repository ships:

- `execution-brief.schema.json`
- `execution-brief-v2.schema.json`
- `scripts/schema_validation.py`

The local validator supports the exact keyword set currently used by those schemas:

- `type`
- `const`
- `enum`
- `required`
- `properties`
- `additionalProperties`
- `items`
- `minItems`
- `uniqueItems`
- `minLength`
- `pattern`
- `minimum`
- `exclusiveMinimum`
- `format: date-time`
- local `$ref` under `#/$defs/`
- `anyOf`

Remote schema references are deliberately unsupported.

Tests compare representative local-validator results against the development-time `jsonschema` implementation so the lightweight runtime does not become an undocumented parallel contract.

## Version dispatch

The CLI inspects only `version` before full validation.

- `1.0` routes to the v1 schema
- `2.0` routes to the v2 schema plus v2 semantic checks
- missing or unknown versions fail closed
- validation never performs implicit migration

## Semantic v2 validation

JSON Schema handles structure. GTD adds semantic checks for relationships the schema cannot express safely.

v2 uses one global record-ID namespace across referenceable records. Duplicate IDs fail validation before planning or assessment.

Semantic checks also validate selected typed references such as:

- attempt → workstream
- deliverable → workstream
- evidence → criterion
- plan change → checkpoint
- review waiver → decision

Authority state also fails closed when approval and execution state contradict each other.

## v1 completion policy

v1 remains readable, renderable, and assessable for readiness.

v1 evidence is an unlinked list of strings, so it cannot prove individual success criteria. GTD therefore no longer reports v1 as verified Done merely because the evidence list is non-empty.

For evidence-backed completion, migrate explicitly to v2 and relink/re-verify evidence.

## Assessment exit contract

`assess-brief` preserves the historical default:

```bash
gtd assess-brief brief.json
```

A structurally valid brief exits `0` even when it is not Ready or Done.

Automation can request a gate explicitly:

```bash
gtd assess-brief brief.json --require ready
gtd assess-brief brief.json --require done
```

Exit codes:

- `0`: the requested requirement is met
- `1`: the brief cannot be read or is invalid
- `2`: the brief is valid, but the requested Ready/Done requirement is not met

`--json` returns `requirement` and `requirement_met` with the same semantics.

## v1 to v2 migration

Migration is explicit:

```bash
gtd migrate-brief legacy-v1.json --out migrated-v2.json
```

The source file is not modified.

Conservative migration rules:

- legacy unknowns become blocking
- workstreams do not inherit top-level Done
- deliverables do not inherit top-level Done
- migrated workstreams default to `parallel_safe: false`
- legacy evidence becomes unlinked, inconclusive claim-level evidence
- legacy Done becomes `terminal_state: unverified`
- source v1 status and conservative downgrade are recorded in `plan_changes`
- no execution attempt or review record is fabricated

## Experimental pre-contract v2 files

Early experimental v2 files using:

```json
{
  "authority": {
    "autonomous_actions": [],
    "approval_required": [],
    "approved_actions": []
  }
}
```

do not satisfy the published v2 schema.

Convert each action to the canonical `authority.actions[]` representation before validation. GTD does not silently infer approvals because authority is a safety boundary.
