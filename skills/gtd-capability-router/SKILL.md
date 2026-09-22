---
name: gtd-capability-router
description: >
  Use when a GTD task can be executed through multiple tools, plugins, connected sources, reviewers, agents, or GitHub actors and the agent must choose the smallest safe stack with explicit ownership, live-state authority, verification, review, and landing boundaries. Also use for continuation work, repository/PR missions, and skill/plugin engineering where stale state or overlapping capabilities can cause duplicate or unsafe work. Do not use for simple one-step tasks with an obvious single tool, or to replace GTD's blocker router or domain-pack selection.
---

# GTD Capability Router

Route an already understood GTD work cycle to the smallest safe capability stack.

This skill extends the GTD core contract. It does not replace the GTD mode router, Definition of Ready, Definition of Done, domain packs, or Execution Brief.

Load references/core-contract.md first. Then load:

- references/router.yaml for routing invariants and route families
- references/capability-registry.yaml for stable capability roles
- agents/roles.yaml when the mission needs multiple logical roles
- references/repository-playbook.md for repository, Issue, Pull Request, CI, bot, or landing work
- references/plugin-skill-playbook.md for Agent Skill or Agent Plugin work
- references/security-boundaries.md when authority, credentials, destructive actions, or sensitive surfaces are in scope
- references/source-lineage.md when maintaining or extending this pack

## Routing loop

1. **Establish current GTD state**
   Read the current outcome, blocker, Ready/Done state, constraints, and requested action. Do not create a second planning system.

2. **Classify the execution surface**
   Distinguish skill or in-host capability, connected source, external authority, repository-native gate, GitHub app or bot, and local/runtime executor.

3. **Resolve live availability**
   Treat the registry as capability metadata, not proof that a named capability is callable now.
   Discover the current callable surface before selection.

4. **Choose the smallest useful stack**
   Assign only roles that materially change the work: primary owner, source of truth, write owner, verifier, independent reviewer, and landing owner.
   Omit roles that are not needed.

5. **Separate nominal from selected owner**
   The nominal owner is the best capability in principle.
   The selected owner is the callable capability actually used now.
   If the nominal owner is blocked, choose the smallest safe fallback or record an explicit evidence gap.

6. **Protect write ownership**
   Only one selected capability owns a mutable surface at a time unless writes are clearly independent.

7. **Execute before judging**
   When delivery was requested and tools exist, perform the action.
   Do not substitute planning, review, or readiness analysis for execution.

8. **Verify with executable evidence**
   Prefer tests, builds, type checks, lint, runtime checks, current-head CI, inspected artifacts, returned IDs, or other observable proof.
   Reviewer agreement is not executable proof.

9. **Review independently when risk justifies it**
   Use one primary independent reviewer by default.
   Add a second specialist lens only for a distinct material risk.

10. **Refresh after mutation**
    Any push, bot-authored commit, deployment, migration, or external mutation can stale previous evidence.
    Refresh live state before readiness or landing decisions.

11. **Land through one authority**
    Use exactly one active landing owner and bind landing evidence to the current head/state.
    Queue submission or approval intent is not merge completion.

12. **Report evidence status**
    Distinguish completed, verified, partially verified, blocked, and not started.

## Hard rules

- Current connected state outranks memory, handoff prose, and old screenshots
- Never invent a tool's capability, availability, command, bot trigger, or write authority
- Never invoke a blocked nominal owner merely to satisfy a recipe
- Never use a reviewer as proof that executable checks passed
- Never ask a readiness analyzer to discover live state it cannot access
- Never treat absence of findings from a blocked or rate-limited reviewer as a clean review
- Never reuse stale exact-head readiness after mutation
- Never trigger every reviewer because several are installed
- Never let a companion tool weaken GTD Ready, Done, authority, or evidence rules

## Output contract

For substantial routing decisions, preserve:

- current GTD state and active mode
- nominal owner and selected owner
- source of truth
- mutable surfaces and write owner per surface
- verification plan and evidence
- independent review path
- landing owner when applicable
- unavailable capabilities and resulting evidence gaps
- next executable action

Do not expose internal routing ceremony when a simple task only needs one obvious capability.
