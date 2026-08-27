# Evaluation datasets

This directory contains evaluation suites for skill behavior, host adapter compliance, and companion tool interoperability:

- **`cases.jsonl`**: Cross-domain behavioral pressure scenarios for Get Things Done.
- **`adapter-cases.jsonl`**: Conformance expectations across all 19 host adapter contracts.
- **`interop-cases.jsonl`**: Separation of concerns and boundary expectations for all 5 companion profiles.

## Behavioral pressure scenarios (`cases.jsonl`)

Run each prompt in a fresh agent context with `get-things-done` available. A reviewer checks every item in `must`.

Important failure classes:

- Question dumping instead of resolving only active blockers
- Asking the user for discoverable facts
- Hiding Assumptions as Facts
- Channel-first or feature-first planning without clarifying the outcome
- Producing a plan when execution was requested and tools are available
- Claiming Done without verification evidence
- Forcing a domain pack when the core alone is enough

For a true RED/GREEN behavior evaluation, run each case once without the skill and once with the skill in fresh contexts, then compare compliance.

## Adapter & companion conformance verification

Run automated validation across all evaluation cases:

```bash
pytest tests/test_adapter_evals.py -v
```

