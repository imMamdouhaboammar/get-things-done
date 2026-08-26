# Behavioral evaluation cases

`cases.jsonl` contains cross-domain pressure scenarios for Get Things Done

Run each prompt in a fresh agent context with `get-things-done` available. A reviewer checks every item in `must`

Important failure classes:

- question dumping instead of resolving only blockers
- asking the user for discoverable facts
- hiding Assumptions as Facts
- channel-first or feature-first planning without clarifying the outcome
- producing a plan when execution was requested and tools are available
- claiming Done without verification evidence
- forcing a domain pack when the core alone is enough

For a true RED/GREEN behavior evaluation, run each case once without the skill and once with the skill in fresh contexts, then compare compliance. The package tests verify structure and deterministic tooling, not model behavior
