# Agent Skill and Agent Plugin Engineering Playbook

Use this playbook when creating, modifying, packaging, evaluating, or preparing distribution for Agent Skills or Agent Plugins.

## Contract sources

For contract-sensitive work, inspect the current specification before implementation:

- Agent Skills specification: https://agentskills.io/specification
- Agent Plugins specification: https://agent-plugins.org/specification

Repository-local manifests and tests remain authoritative for how this project currently implements those contracts.

## Portable Skill shape

Keep the portable capability under skills/<skill-name>/SKILL.md.

Use progressive disclosure:

1. frontmatter provides discovery metadata
2. SKILL.md provides the operating contract
3. focused files under references/, scripts/, assets/, or agents/ load only when needed

Do not turn SKILL.md into a copy of a long handbook when focused references can preserve detail.

## Evaluation labels

Keep these states separate: eval corpus exists, deterministic validation passed, behavioral eval executed, baseline/candidate comparison executed, marketplace material prepared, submitted, approved, published.

A routing corpus is not an executed benchmark.
A valid local package is not marketplace approval.

## Capability snapshots

Tool availability is ephemeral. Keep stable capability roles in the Skill and resolve current availability at runtime. When a named tool is unavailable, preserve its nominal role when useful, choose a safe callable fallback only when authority remains valid, record any evidence gap, and never simulate its output.
