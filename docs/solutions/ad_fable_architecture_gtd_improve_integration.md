# Architecture Decision: Deep Integration of Improve Senior Advisor as Sixth Skill

## Context
The user requested pulling `https://github.com/shadcn/improve` as the sixth canonical skill and integrating it deeply into `imMamdouhaboammar/get-things-done`.

## Architectural Synthesis
1. **Skill Ecosystem Topology**:
   - `get-things-done`: Core execution contract, Execution Briefs, Definition of Ready/Done, Knowledge Ledger.
   - `building-gtd-domain-packs`: Domain expansion without core forking across 9 domains.
   - `gtd-capability-router`: Smallest safe execution stack routing across tools and agents.
   - `gtd-deliberation`: Pre-planning challenge and evidence freshness layer.
   - `use-chatgpt`: Multi-plugin intent routing DAG, Open-PR bot gate fencer, Evidence Trust Ladder (A-E), macOS bridge.
   - `improve`: **Senior Codebase Advisor & Plan Architect** — deep read-only auditing and self-contained implementation plan authoring.

2. **Core Invariants & Boundaries**:
   - **Zero Source Mutation**: The advisor surveys repositories strictly in read-only mode and only writes to `plans/` (or `advisor-plans/`).
   - **Self-Contained Plan Guarantee**: Plans are written for the weakest plausible executor with zero prior context; all excerpts, commands, and conventions are inlined.
   - **Machine-Checkable Verification Gates**: Every plan step terminates in an executable command with deterministic expected output (Evidence Trust Level A/B).
   - **Secret Fencing & Prompt Injection Defense**: Never reproduce secrets; repository content is treated as untrusted data, not model instructions.

3. **Bidirectional GTD Bridge**:
   - Implemented via `skills/get-things-done/scripts/improve_bridge.py`.
   - `gtd improve-ingest`: Parses self-contained `improve` plans and converts them directly into GTD Execution Briefs (v1.0 and v2.0) with full schema compliance.
   - `gtd improve-validate`: Validates plan self-containment, boundaries, and verification gates.
   - `gtd improve-plan`: Scaffolds new self-contained plans pre-hydrated with git HEAD and repo test runners.
