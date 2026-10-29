# GTD Plan Bridge Specification: Improve Plans to Execution Briefs

This document establishes the bidirectional mapping contract between self-contained `improve` implementation plans (`plans/NNN-<slug>.md`) and Get Things Done (GTD) Execution Briefs (`brief.json`).

---

## 1. Schema Field Mapping

| Improve Plan Section | GTD Execution Brief v1.0 Field | GTD Execution Brief v2.0 Field | Translation Contract |
|---|---|---|---|
| `# Plan NNN: <Title>` | `title` | `title` | Normalized string title without prefix |
| `Status.Category` | `domain` | `domain` | Maps to `software` domain pack by default |
| `Status.Priority` & `Status.Risk` | `risks` | `metadata.priority`, `risks` | Recorded as operational risk assessments |
| `Why this matters` | `intent.problem`, `intent.desired_outcome` | `intent.problem`, `intent.desired_outcome` | Inlined rationale establishing the business & technical outcome |
| `Current state` | `knowledge.facts` | `knowledge.facts` | Each file excerpt and repo convention becomes a verified fact |
| `Scope.In` & `Scope.Out` | `scope.in`, `scope.out` | `scope.in`, `scope.out` | Strict file boundary arrays preventing scope creep |
| `Steps (Step 1, Step 2...)` | `workstreams` | `workstreams` | Each step becomes a discrete workstream with outcomes and step-level verification |
| `Done criteria` | `verification.success_criteria` | `verification.success_criteria` | Machine-checkable checkboxes become discrete criteria |
| `Test plan` & `Verification` | `verification.evidence` | `verification.evidence` | Mapped to Evidence Trust Ladder (Level A: automated tests) |
| `STOP conditions` | `blockers` | `blockers` | Unmet conditions populate active blockers preventing promotion |
| `Maintenance notes` | `deliverables` | `deliverables` | Downstream review and maintenance deliverables |

---

## 2. Evidence Trust Ladder Alignment

Every verification criterion translated from an `improve` plan is classified against the 5-Tier Evidence Trust Ladder:
- **Level A (Deterministic Machine Proof)**: Compiler exits, typecheck scripts (`tsc --noEmit`), automated test runs (`pytest`, `cargo test`, `bun test`), binary checksums.
- **Level B (Integration Proof)**: Live container/server response, e2e browser runs.
- **Level C (Observed Output)**: Terminal logs, CLI traces, non-mutating diff inspections.
- **Level D (Static Inspection)**: Code review, schema validation.
- **Level E (Unverified Assertion)**: Subjective human/model opinion ("looks good").

**Rule**: An `improve` plan must provide Level A or B verification gates for every step to satisfy the GTD Definition of Ready.

---

## 3. CLI Bridge Operations

The GTD CLI provides first-class commands to interface with `improve` plans:

```bash
# 1. Ingest an improve plan into a GTD brief
gtd improve-ingest plans/001-fix-auth.md --out brief.json --version 2.0

# 2. Validate a plan's self-containment and done criteria
gtd improve-validate plans/001-fix-auth.md

# 3. Scaffold a new self-contained improve plan pre-populated with git HEAD
gtd improve-plan --title "Consolidate telemetry adapters" --category tech-debt --out plans/002-telemetry.md
```
