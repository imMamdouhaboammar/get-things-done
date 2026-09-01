# Task Plan: Evolve the GTD Working Method

## Goal
Evolve GTD into a focused, portable operating contract that makes human-agent work faster, more autonomous, evidence-driven, and resumable without turning it into a generic project manager or orchestration engine.

## Next Step
Validate this roadmap against the canonical GTD contract, schema, CLI, evaluations, and repository boundaries.

## Current Phase
Phase 1

## Planning Status
- **Plan maturity:** Draft under repository validation
- **Implementation status:** Not started
- **Primary artifact:** This file
- **Supporting evidence:** `findings.md`
- **Activity log:** `progress.md`

## Target Operating Model

### Core promise
For every request, GTD should establish the outcome, maintain trustworthy state, route only the current blocker, act within explicit authority, and claim completion only with evidence.

### Interaction modes
| Mode | Trigger | Required process | User burden |
|------|---------|------------------|-------------|
| Fast path | Small, local, reversible, low-risk work with an obvious verification | Infer outcome, state assumptions only if material, execute, verify, report evidence | None unless a consequential choice appears |
| Standard path | Multi-step work with known boundaries | Lightweight Execution Brief, one active frontier, phase-level verification | Approve only consequential decisions |
| High-assurance path | Irreversible, security-sensitive, external side effects, migration, release, or unclear success criteria | Full brief, explicit authority gates, risk/rollback plan, independent or stronger verification | Approve high-impact decisions and actions |

### Non-negotiable invariants
1. Maintain a Fact / Assumption / Decision / Unknown ledger.
2. Expose one active blocker or frontier at a time.
3. Ask the user only when the missing information changes outcome, risk, cost, or authority.
4. Prefer bounded reversible action over conversational delay.
5. Map every completion claim to fresh evidence.
6. Preserve honest state across agents, sessions, and hosts.
7. Keep specialist reasoning in domain packs; keep orchestration and advisory personas outside GTD core.

## Workstreams

### WS1 — Request intake and outcome contract
Define the minimum information GTD derives or requests before work begins.

**Outputs**
- A compact outcome contract: desired result, scope boundary, acceptance signal, constraints, authority, and urgency.
- Deterministic classification into fast, standard, or high-assurance mode.
- Question-worthiness rule that suppresses low-value clarification.
- Examples for vague, precise, low-risk, and high-risk requests.

**Acceptance criteria**
- Small obvious tasks proceed without mandatory planning ceremony.
- Consequential ambiguity produces one decision-ready question, not an interview.
- The inferred outcome and scope are inspectable in the Execution Brief.

### WS2 — Decision authority and autonomy policy
Separate what the agent may decide from what belongs to the user.

**Outputs**
- Authority matrix covering reversible assumptions, destructive actions, external communications, spending, credentials, releases, policy, and scope expansion.
- Escalation packet format: decision, options, recommendation, impact, and default if deferred.
- Rules for time-boxed assumptions and reversible probes.

**Acceptance criteria**
- The agent can continue through low-risk uncertainty without asking permission.
- High-impact actions cannot be silently inferred.
- Every escalation is answerable in one turn.

### WS3 — Active-frontier and blocker routing
Make progress legible by routing only the obstacle currently preventing the next useful action.

**Outputs**
- Explicit blocker taxonomy: clarify, research, decompose, decide, validate, model, execute, verify.
- Router contract defining entry evidence, action, exit evidence, and fallback for each blocker type.
- Rules preventing premature execution, endless research, and parallel attention fragmentation.

**Acceptance criteria**
- Exactly one active frontier is represented in normal execution.
- Background parallelism is allowed only for independent work and does not create multiple user-facing blockers.
- Every router transition has a machine-checkable reason or recorded evidence.

### WS4 — Execution Brief v2 lifecycle
Upgrade the brief from a static handoff document into a proportional state contract.

**Outputs**
- Versioned schema changes for operating mode, outcome contract, authority, active frontier, acceptance-to-evidence mapping, risk, rollback, and handoff state.
- Lifecycle states and legal transitions from intake through verified completion.
- Backward compatibility and migration behavior for v1 briefs.
- Concise human rendering and deterministic machine validation.

**Acceptance criteria**
- v1 briefs remain readable or receive actionable migration output.
- Readiness is based on meaningful fields, not presence alone.
- A fresh agent can resume from the brief without relying on chat history.
- Fast-path tasks do not require irrelevant fields.

### WS5 — Evidence-backed readiness and completion
Replace presence-based gates with criterion-linked proof.

**Outputs**
- Acceptance criterion identifiers.
- Evidence records containing criterion link, method, source/artifact, freshness, result, and limitations.
- Verification strength levels proportional to risk.
- Honest terminal states: verified complete, partially complete, blocked, failed, or unverified.

**Acceptance criteria**
- Every required criterion is covered by valid evidence before `verified complete`.
- Stale, missing, or contradictory evidence is rejected or surfaced.
- Rendered reports distinguish execution from verification.
- Manual claims cannot masquerade as tool evidence.

### WS6 — CLI and validator alignment
Make the Python implementation enforce the evolved contract consistently.

**Outputs**
- Schema-backed validation or one canonical validation engine to eliminate schema/manual drift.
- Updated scaffold, validate, assess, render, doctor, and package behavior.
- Stable exit codes and actionable diagnostics.
- Wrapper compatibility in `scripts/gtd.py`.

**Acceptance criteria**
- CLI behavior and JSON Schema agree on all tested constraints.
- Diagnostics point to the exact field, invariant, and repair.
- No duplicated rules can silently diverge.
- Existing supported Python versions remain green.

### WS7 — Behavioral evaluation system
Turn pressure scenarios into executable behavior checks rather than a passive dataset.

**Outputs**
- Scenario format with expected decisions, forbidden behaviors, and evidence requirements.
- Deterministic checks where possible and model-graded checks only where necessary.
- Baseline results for the current contract and target thresholds for the evolved contract.
- Regression categories: unnecessary questions, unsafe autonomy, fake completion, state drift, ceremony inflation, and scope creep.

**Acceptance criteria**
- Each core invariant has positive, negative, and pressure tests.
- Results are reproducible with model/provider metadata.
- A release cannot claim behavioral improvement without baseline comparison.
- Deterministic CI remains clearly separated from probabilistic evaluation.

### WS8 — Domain packs and host portability
Keep the core small while allowing specialist rigor and host-specific capability mapping.

**Outputs**
- Clear inheritance rules for domain packs.
- Capability negotiation for tools, subagents, background work, approvals, and persistent state.
- Host adapter conformance tests focused on behavior, not generated file count.
- Updated software domain pack as the reference implementation.

**Acceptance criteria**
- Domain packs cannot weaken core invariants.
- Unsupported host capabilities degrade honestly rather than being simulated.
- Core semantics are identical across exported adapters.
- Optional companions remain metadata boundaries, not hidden runtime dependencies.

### WS9 — Documentation, rollout, and measurement
Introduce the new method safely and prove that it improves collaboration.

**Outputs**
- Updated canonical skill contract, core reference, schema guide, CLI docs, and examples.
- Migration guide from current behavior and briefs.
- Pilot protocol using representative real tasks.
- Metrics dashboard/report definition.

**Acceptance criteria**
- Documentation has one canonical source for each rule.
- Migration and rollback are documented before default behavior changes.
- Pilot results meet agreed thresholds without increasing safety failures.
- Generated adapter projections are rebuilt only after canonical sources stabilize.

## Phases

### Phase 1: Baseline and contract gap map
- [ ] Trace each current invariant from `SKILL.md` to reference, schema, CLI, tests, and evals.
- [ ] Record mismatches, especially schema/manual validation and presence-only Ready/Done checks.
- [ ] Establish current behavioral and interaction baselines.
- [ ] Freeze scope exclusions, including `consult-dad`, generic project management, and orchestration engines.
- **Deliverables:** traceability matrix, baseline report, scope boundary.
- **Exit gate:** every proposed change maps to a demonstrated current gap.
- **Status:** in_progress

### Phase 2: Decision-complete method specification
- [ ] Specify fast, standard, and high-assurance modes.
- [ ] Define outcome contract, question-worthiness, authority matrix, and escalation packets.
- [ ] Formalize the active-frontier router and legal state transitions.
- [ ] Define acceptance-to-evidence semantics and terminal states.
- **Deliverables:** method specification and decision log.
- **Exit gate:** no unresolved decision blocks schema or evaluation design.
- **Status:** pending

### Phase 3: Evaluation-first contract
- [ ] Convert existing pressure cases into explicit expected/forbidden behavior assertions.
- [ ] Add cases for small-task over-planning, autonomous reversible action, consequential ambiguity, evidence mismatch, stale evidence, interrupted handoff, and unavailable tools.
- [ ] Capture baseline behavior before modifying the canonical skill.
- [ ] Define release thresholds and acceptable variance.
- **Deliverables:** evaluation specification, baseline results, release thresholds.
- **Exit gate:** every new normative rule has at least one failing baseline case or a justified preventive case.
- **Status:** pending

### Phase 4: Execution Brief v2 and validator design
- [ ] Draft the v2 schema and migration rules.
- [ ] Select a single validation source of truth.
- [ ] Specify proportional field requirements by operating mode and risk.
- [ ] Define evidence linkage, freshness, contradiction handling, and render format.
- **Deliverables:** schema proposal, validation architecture, compatibility matrix.
- **Exit gate:** schema examples validate; invalid examples fail with expected diagnostics.
- **Status:** pending

### Phase 5: Incremental implementation
- [ ] Implement schema and canonical validation changes behind explicit version handling.
- [ ] Update scaffolding, readiness, completion, assessment, rendering, and doctor behavior.
- [ ] Update the canonical skill and core contract only after executable semantics exist.
- [ ] Update software domain pack and host export projections last.
- **Deliverables:** atomic code and documentation changes with tests.
- **Exit gate:** each increment passes focused tests and preserves v1 compatibility policy.
- **Status:** pending

### Phase 6: Verification and adversarial review
- [ ] Run unit, integration, schema, packaging, adapter, shell, and Ruby checks.
- [ ] Run behavioral evaluation against baseline and target thresholds.
- [ ] Test resume/handoff with a fresh agent and degraded-tool hosts.
- [ ] Review for scope creep, ceremony inflation, unsafe autonomy, and unverifiable claims.
- **Deliverables:** verification report, behavioral comparison, residual-risk register.
- **Exit gate:** deterministic suite is green and behavioral thresholds are met or deviations are explicitly accepted.
- **Status:** pending

### Phase 7: Pilot, migration, and release
- [ ] Pilot on a balanced task set across all three operating modes.
- [ ] Measure user questions, time to first action, rework, evidence coverage, resume success, and safety interventions.
- [ ] Adjust only from observed failure patterns.
- [ ] Publish migration guide, release notes, and rollback instructions.
- **Deliverables:** pilot report, final contract, migration/release package.
- **Exit gate:** pilot success criteria pass and rollback remains available.
- **Status:** pending

## Dependency Order
1. Baseline and traceability before normative redesign.
2. Method decisions before schema shape.
3. Evaluations before behavior-changing implementation.
4. Schema and validator before documentation projections.
5. Canonical core before domain packs and adapters.
6. Full verification before pilot and default rollout.

## Parallelization Plan
- Phase 1 can parallelize trace lanes for contract, implementation, and evaluation, with one owner integrating the matrix.
- Phase 3 scenario authoring can parallelize by invariant after the assertion format is frozen.
- Phase 5 may parallelize CLI tests, documentation examples, and adapter conformance only after schema and public semantics stabilize.
- Schema, canonical contract wording, and migration policy require single-owner integration to avoid semantic drift.

## Metrics and Targets
Final thresholds should be calibrated from Phase 1 baselines; initial targets are hypotheses, not release promises.

| Metric | Intended direction | Initial target hypothesis |
|--------|--------------------|---------------------------|
| Unnecessary clarification rate | Down | At least 50% lower on fast-path cases |
| Time/tool calls to first useful action | Down | At least 30% lower on fast-path cases |
| Consequential decisions explicitly surfaced | Up | 100% in high-assurance eval cases |
| Acceptance criteria with linked fresh evidence | Up | 100% for verified-complete claims |
| False completion claims | Down | 0 in release eval suite |
| Fresh-agent resume success | Up | At least 90% without chat history |
| Ceremony overhead on small tasks | Down | No mandatory full brief for fast-path cases |
| Deterministic regression rate | Stable | 0 new failures |

## Risks and Mitigations
| Risk | Mitigation |
|------|------------|
| GTD becomes a generic project manager | Keep scope at execution integrity, state, authority, evidence, and handoff |
| More structure slows small tasks | Make process proportional through explicit operating modes |
| Autonomy creates unsafe actions | Separate reversible assumptions from consequential authority gates |
| Schema and Python rules drift | Use one canonical validation source and conformance tests |
| Evidence fields become paperwork | Require evidence only for acceptance claims and scale strength by risk |
| Model evals become flaky or self-congratulatory | Preserve deterministic checks, pin metadata, use forbidden-behavior assertions, compare to baseline |
| Adapter work dominates core value | Stabilize canonical semantics first; regenerate projections last |
| User-authored deletion is reintroduced | Treat `consult-dad` removal as intentional scope evidence |

## Rollback Strategy
- Preserve explicit brief versioning and v1 fixtures.
- Keep v2 behavior opt-in until migration, deterministic validation, and behavioral thresholds pass.
- Allow renderer/assessor compatibility mode during transition.
- Revert canonical behavior independently from generated adapter projections.
- Never require users to rewrite valid historical briefs without a deterministic migration path.

## Release Definition of Done
- [ ] Canonical contract, schema, CLI, tests, evals, domain reference, and documentation agree.
- [ ] All acceptance criteria are linked to fresh verification evidence.
- [ ] Fast-path work demonstrates reduced ceremony without safety regression.
- [ ] High-assurance work demonstrates complete authority and evidence gates.
- [ ] Fresh-agent handoff succeeds without hidden chat context.
- [ ] Full repository verification passes on supported runtimes.
- [ ] Migration and rollback instructions are tested.
- [ ] No deleted out-of-scope capability is reintroduced.

## Key Questions
1. Should Execution Brief v2 remain one schema with conditional requirements, or use a shared core plus mode-specific profiles?
2. Which completion evidence types can be validated deterministically across hosts?
3. What exact behavior-evaluation runner is acceptable for CI versus manual release qualification?
4. How long should v1 compatibility remain supported?
5. Which pilot task corpus best represents the user's actual daily collaboration?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Improve the working method, not the adapter count | The user wants better collaboration; packaging breadth is not the core outcome |
| Preserve GTD as an execution-integrity protocol | This matches the canonical contract and prevents generic PM scope creep |
| Use proportional operating modes | Small tasks need speed; consequential work needs stronger gates |
| Design evaluations before implementation | Behavioral changes require a baseline and falsifiable success criteria |
| Treat `consult-dad` deletion as intentional | Advisory personas are outside GTD scope and must not be restored |
| Regenerate adapters only after core stabilization | Prevents generated surfaces from driving canonical semantics |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| Homebrew Python rejected global `pip install` under PEP 668 | 1 | Created `.code-review-graph-venv` and installed there |
| `pipx` unavailable | 1 | Used the repository-local virtual environment |
| `consult-dad` was mistakenly restored during investigation | 1 | Removed it again, removed stale generated copy, rebuilt graph, and preserved unstaged deletion |
| Cursor cloud orchestration preflight found no `CURSOR_API_KEY` | 1 | Await runtime choice: provide a user key or use available local DSH subagents |
| Hindsight knowledge-page listing returned HTTP 401 | 1 | Continue from repository files unless Hindsight authentication becomes available |
| Local Ruff invocation failed because Ruff is not installed for Python 3.14 | 1 | Did not repeat; recorded as an unverified lint gap while completing all remaining deterministic checks separately |

## Scope Boundary

### In scope
- Human-agent execution contract.
- Request intake, authority, blocker routing, readiness, execution state, verification, evidence, and handoff.
- Schema, CLI enforcement, tests, behavioral evals, documentation, and portable host projections.

### Out of scope
- Advisory personas such as `consult-dad`.
- Generic backlog, sprint, calendar, or project-management features.
- A proprietary multi-agent orchestration runtime.
- Hidden tool capabilities or simulated verification.
- Expanding adapter count without a core behavioral need.
