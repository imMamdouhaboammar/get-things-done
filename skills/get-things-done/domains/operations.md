---
domain: operations
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Operations
## Selection signals
Active incidents, on-call runbooks, SLO management, deployment go/no-go decisions, capacity planning, postmortem writing, disaster recovery planning, operational procedure authoring, infrastructure change management. Non-selection: software feature development (software domain), data pipeline design (data-ai domain), monitoring dashboard setup without an associated operational procedure.
## Domain vocabulary
Keep distinct: incident vs event vs alert (alert is a signal; event is an observed anomaly; incident is confirmed impact on users or SLOs — escalating too early or too late changes the response and authority required), SLO vs SLA (SLO is an internal target; SLA is a contractual obligation — breaching them has different consequences and response authorities), mitigation vs resolution (mitigation stops the bleeding; resolution fixes the cause — claiming resolved when only mitigated restarts incidents), runbook vs playbook (runbook is step-by-step for a known failure mode; playbook is decision guidance for scenario types — using the wrong format wastes time under pressure), blast radius vs impact (blast radius is scope of potential harm; impact is observed harm — acting on blast radius before confirming impact leads to unnecessary changes).
## Diagnostic questions
Ask only when blocking: Is this an active incident or proactive operations work? What is the confirmed blast radius? Is there a rollback path? What SLO or SLA is at risk? Who has authority to approve the change?
## Extra brief fields
`incident_severity`, `blast_radius`, `affected_services`, `slo_at_risk`, `rollback_path`, `change_authority`, `mttd`, `mttr`, `postmortem_owner`
## Readiness additions
- blast radius assessed before any change is executed
- rollback path confirmed and documented, not assumed
- change authority identified before execution begins
- monitoring or alerting exists to confirm the change had the intended effect
## Workstream patterns
- incident response: detect → triage → blast-radius → mitigate → communicate → resolve → postmortem
- change management: intent → blast-radius → rollback plan → approval → execute → confirm → close
- postmortem: timeline → contributing factors → impact quantification → action items → owner assignment → follow-up tracking
- runbook: failure mode identification → step sequence → decision points → rollback steps → validation → review
## Review additions
Check that blast radius was assessed before action, that mitigation and resolution are distinguished in incident records, that postmortem actions have owners and deadlines, that SLO impact is quantified rather than described qualitatively, and that rollback paths are tested or explicitly marked as untested.
## Completion checks
For incidents: MTTD and MTTR recorded, impact quantified against SLO, postmortem scheduled or complete, action items have owners and timelines. For runbooks: steps are executable without domain expertise, decision points are explicit, rollback is included. For changes: confirmation monitoring is in place and has fired.
## Common traps
Acting on blast radius before confirming user impact, claiming resolved when only mitigated, writing postmortems without action items, executing changes without a rollback plan, and skipping change authority confirmation under time pressure.
