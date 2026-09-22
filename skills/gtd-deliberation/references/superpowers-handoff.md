# Planning Handoff Contract

After the Direction Gate is approved, planning may use Superpowers or another compatible engineering methodology.

The methodology owns planning technique. GTD owns authority, evidence, Ready/Done, and handoff semantics.

## Required handoff into planning

Provide:

- approved direction
- Problem Model reference
- relevant current-date evidence
- constraints
- rejected directions that must not silently re-enter scope
- open but non-blocking uncertainty
- success criteria
- risk and rollback expectations
- user Decisions already settled

## Planning requirements

Planning should produce bounded work that is:

- testable
- dependency-aware
- ordered by risk and information value
- explicit about interfaces and failure paths
- small enough to execute and verify incrementally

For software work, prefer implementation steps with tests or observable verification attached to each meaningful unit.

## Backlog conversion

The final planning output should be converted into `backlog.schema.json`.

Do not copy brainstorming residue into the backlog.

Only approved or explicitly provisional direction belongs in implementation work.

## Boundary

A methodology or planner cannot:

- override the approved direction without reopening the Direction Gate
- turn an unapproved alternative into implementation scope
- treat its own plan as evidence that implementation is correct
- bypass current-date evidence requirements when external assumptions change
