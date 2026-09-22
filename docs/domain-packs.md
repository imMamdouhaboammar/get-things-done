# Building Domain Packs

A domain pack is justified when a field needs materially different vocabulary, diagnosis, readiness, review, or completion evidence

Do not create a pack only because a field has different nouns

## Pack contract

Every pack inherits the GTD core and adds nine sections

1. Selection signals
2. Domain vocabulary
3. Diagnostic questions
4. Extra brief fields
5. Readiness additions
6. Workstream patterns
7. Review additions
8. Completion checks
9. Common traps

See [`domain-pack-spec.md`](../skills/get-things-done/references/domain-pack-spec.md) for the exact contract

## Selection is about intent

Bad selection rule

```text
If the prompt contains campaign, use marketing
```

Better selection rule

```text
Use marketing when the requested outcome concerns audience response, offer, channel activity, campaign economics, or measurement
Do not select marketing when campaign only names a software object or dataset
```

Each domain should include non-selection signals to reduce collisions with adjacent packs

## Test before publishing

Use four cases

### Messy in-domain

The task is clearly in the field but arrives with weak structure

Expected result: the pack is selected and improves diagnosis

### Well-formed in-domain

The task already has a clear outcome and constraints

Expected result: the pack adds specialist checks without forcing unnecessary questions

### Deceptive near-complete

The deliverable looks plausible but lacks field-specific evidence

Expected result: Done is rejected

### Adjacent out-of-domain

The task shares vocabulary with the field but has a different outcome

Expected result: the pack is not selected

## Scaffold

```bash
python scripts/gtd.py new-domain media-buying \
  --name "Media Buying" \
  --output skills/get-things-done/domains/media-buying.md
```

Then replace the scaffold guidance with field-specific rules and verify domain pack invariants:

```bash
# Validate domain pack contracts and prevent naming collisions
pytest tests/test_pack.py -v

# Create and validate a sample brief using the new domain
python scripts/gtd.py new-brief --title "Campaign budget review" --domain media-buying --out brief.json
python scripts/gtd.py validate-brief brief.json --root .
```



## Runtime selection contract

Start from the universal GTD core.

Load **zero or one** specialist domain pack for the active task. Select a pack only when its vocabulary, diagnostic questions, readiness additions, review rules, or completion evidence materially changes how the current outcome should be handled.

A noun match is not enough. The routing corpus under [`evals/domain-routing-cases.jsonl`](../evals/domain-routing-cases.jsonl) includes positive selection, non-selection, zero-pack, and wrong-pack cases for all nine built-in packs.

The **core remains authoritative**. A domain pack can add stricter field-specific checks, but it cannot weaken core authority, evidence, readiness, Done, handoff, or tool-honesty rules.

## Capability degradation

Domain packs describe specialist reasoning and evidence requirements; they do not prove that a host has every tool needed to satisfy those requirements.

When a useful capability is unavailable:

- keep the affected fact or verification state explicit
- degrade to the strongest available evidence
- hand off the missing executable check when necessary
- do not simulate a tool, external source, deployment, approval, or verification result
- do not claim Done merely because the domain pack describes the desired check

Host capability routing remains separate from domain selection. The optional capability router can select an available implementation path without changing which domain semantics are authoritative.

## Auditing selection behavior

Validate the routing corpus contract:

```bash
python scripts/behavioral_evals.py validate-suite evals/domain-routing-cases.jsonl
pytest -q tests/test_domain_pack_audit.py
```

A live behavioral run should record the actual response or routing trace, grade the named expected/forbidden behavior IDs, and preserve provider/model/host metadata. See [evaluation.md](evaluation.md).
