---
name: gtd-deliberation
description: >
  Use when a GTD request is messy, high-impact, strategically important, assumption-heavy, contradictory, expensive to reverse, or framed around an unvalidated proposed solution and the agent should deeply examine the problem before planning or execution. Use to refresh external knowledge with a current-date search, challenge weak framing with evidence, research competing explanations, reframe the real problem, ideate alternatives, converge on a direction, obtain user approval when authority belongs to the user, and convert the approved direction into an executable backlog. Do not use for simple one-step tasks or fully specified low-risk execution where further contemplation has lower expected value than acting or testing.
---

# GTD Deliberation

A pre-execution reasoning layer for Get Things Done.

The purpose is not to think longer. The purpose is to reduce the chance of executing the wrong request well.

Load only what the current phase needs:

- `references/activation-router.yaml` to decide whether deliberation is justified
- `references/freshness-search.md` before trusting external or versioned knowledge
- `references/deliberation-contract.md` for the operating loop and exit conditions
- `references/truth-contract.md` when the user's framing may be wrong or weakly supported
- `references/problem-model.schema.json` for the durable Problem Model
- `references/superpowers-handoff.md` before implementation planning
- `references/backlog.schema.json` after direction approval
- `agents/roles.yaml` when multiple logical roles help

## Core flow

```text
Messy idea or proposed solution
        ↓
Contemplate
        ↓
Freshness search using today's date
        ↓
Research hypotheses
        ↓
Challenge the framing
        ↓
Reframe the problem
        ↓
Active ideation
        ↓
Critique and synthesis
        ↓
Converge on a direction
        ↓
Direction Gate
        ↓ approved / provisional test
Planning with Superpowers-style methodology
        ↓
Backlog documentation
        ↓
GTD execution and verification
```

## Operating rules

1. **Start from the outcome, not the proposed solution**
   Treat a proposed solution as a hypothesis until evidence or constraints justify it.

2. **Contemplate before researching**
   Identify hidden assumptions, missing objectives, contradictions, incentives, second-order effects, alternative interpretations, and what would need to be true.

3. **Refresh before trusting remembered knowledge**
   Resolve the current date from the runtime. Search relevant current sources using that date. Record what was searched, what changed, and what remains uncertain. Do not present remembered knowledge as current evidence.

4. **Research to test hypotheses**
   Research is not decoration. Use it to support, weaken, or falsify the current framing.

5. **Challenge the request, not the user**
   Say clearly when evidence does not support the proposed direction. Do not flatter a weak idea into a plan.

6. **Reframe from evidence**
   Preserve what survives scrutiny. Replace unsupported assumptions with Facts, explicit Assumptions, Decisions, or Unknowns.

7. **Ideate after the problem is stable enough**
   Generate alternatives, counterfactuals, simplifications, and no-build options. Do not brainstorm features before understanding the problem.

8. **Critique before convergence**
   Attack candidate directions for feasibility, opportunity cost, failure modes, reversibility, second-order effects, and evidence gaps.

9. **Preserve user authority**
   The agent may recommend a direction. The user owns high-impact, preference-heavy, public, financial, identity-sensitive, safety-sensitive, or hard-to-reverse Decisions.

10. **Pass the Direction Gate before implementation planning**
    Do not create an implementation backlog for a direction the user has not approved when approval is materially required.

11. **Use Superpowers-style planning after direction approval**
    Planning should decompose the approved direction into bounded, testable work. Methodology cannot override GTD evidence or authority rules.

12. **Create a backlog, not a vague plan**
    Backlog items must have outcomes, dependencies, acceptance criteria, evidence requirements, and actionable next steps.

13. **Stop contemplating when action has higher expected value**
    More analysis is not inherently safer. Use the sufficiency gate in the deliberation contract.

## Artifact chain

```text
Problem Model
   ↓
Approved Direction
   ↓
Execution Brief
   ↓
Backlog
   ↓
Execution evidence
```

The Problem Model explains why the direction exists. The Execution Brief explains what is executable now. The Backlog preserves approved future work.

## Output discipline

Do not expose private chain-of-thought. Return concise conclusions, evidence, assumptions, alternatives, trade-offs, decisions, and artifacts that another agent can inspect and continue.
