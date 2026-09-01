---
domain: legal-compliance
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Legal & Compliance
## Selection signals
Contract review, compliance audit, regulatory gap analysis, privacy policy, terms of service, data processing agreement, GDPR/CCPA/HIPAA/SOC 2 mapping, risk register, policy authoring, data governance. Non-selection: pure software implementation of compliance controls (software domain), general business strategy, security architecture without regulatory mapping.
## Domain vocabulary
Keep distinct: legal opinion vs legal analysis (opinion is a professional judgment with liability; analysis is structured research without binding legal force — the agent produces analysis, not opinion, and must not present output as legally conclusive), compliance vs conformance (compliance is formal adherence to a legally enforceable requirement; conformance is alignment with a voluntary standard — requirements differ in enforceability and consequence), regulation vs standard (regulation is legally binding; standard is voluntary unless incorporated by regulation — conflating them misstates enforcement risk), risk vs violation (risk is potential non-compliance; violation is confirmed breach — treating risk as violation causes unnecessary escalation), jurisdiction vs applicability (jurisdiction determines which law governs; applicability determines whether a specific requirement applies to this entity or activity — both must be confirmed before gap analysis begins).
## Diagnostic questions
Ask only when blocking: Which jurisdiction(s) apply? What regulation or standard is in scope? What is the effective date of the requirement? Is qualified legal counsel involved or required for binding decisions? What is the consequence of non-compliance?
## Extra brief fields
`jurisdiction`, `regulation_standard`, `effective_date`, `risk_classification`, `counsel_involved`, `gap_list`, `remediation_plan`, `review_deadline`
## Readiness additions
- jurisdiction confirmed or explicitly recorded as a blocking unknown
- regulation or standard and effective date are specified before gap analysis starts
- scope is bounded to reviewable artifacts or stated requirements
- professional authority boundary is acknowledged when legal conclusions would be required
## Workstream patterns
- gap analysis: scope → regulation mapping → current-state review → gap identification → risk classification → remediation plan
- contract review: obligation extraction → risk flagging → jurisdiction check → redline or summary → escalation criteria
- policy authoring: regulatory requirements → existing policy audit → gap identification → draft → stakeholder review → approval → versioning
- privacy impact: data flow mapping → data type classification → regulation applicability → risk assessment → control mapping → documentation
## Review additions
Check jurisdiction confirmation, regulation version and effective date, that agent output is framed as analysis not legal opinion, that risk classification is explicit and severity-differentiated, that remediation items have owners and timelines, and that escalation to qualified counsel is recommended wherever binding decisions are required.
## Completion checks
Jurisdiction and regulation version confirmed, gap list is specific and traceable to named requirements, risk classification is explicit with severity and timeline, remediation plan has owners and deadlines, and professional authority boundary is documented where legal conclusions would be required.
## Common traps
Assuming jurisdiction without confirmation, citing outdated regulation versions, treating risk as a confirmed violation, presenting structured analysis as a legal opinion, and delivering a gap analysis without a remediation plan.
