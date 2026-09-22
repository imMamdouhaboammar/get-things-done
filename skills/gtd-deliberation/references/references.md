# References and Source Lineage

GTD Deliberation extends the existing Get Things Done core rather than replacing it.

Internal contracts:

- `../get-things-done/references/core-contract.md`
- `../get-things-done/references/execution-brief.schema.json`
- `../../adapters/companions.json` for the existing Superpowers methodology boundary

External portable-agent contracts:

- Agent Skills specification: https://agentskills.io/specification
- Agent Plugins specification: https://agent-plugins.org/specification

The Agent Plugins specification was rechecked during this change and was published as version 1.0.0 at the time of implementation.

## Design lineage

The deliberation layer formalizes these principles:

- proposed solutions are hypotheses, not automatically the problem definition
- current external knowledge requires current evidence
- disagreement should be evidence-backed rather than agreeable or performatively contrarian
- planning follows direction approval
- reversible tests can be better than continued analysis
- durable artifacts preserve conclusions and evidence without exposing private chain-of-thought
