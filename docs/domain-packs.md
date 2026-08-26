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

Then replace the scaffold guidance with field-specific rules and add evaluation cases
