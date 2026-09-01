---
domain: data-ai
version: 1
extends: gtd-core-v1
---
# GTD Domain Pack: Data & AI
## Selection signals
ML model training or fine-tuning, dataset creation or cleaning, feature engineering, data pipeline design, model evaluation, experiment tracking, LLM prompting or evaluation, AI system design, analytics dashboards, data quality audits. Non-selection: general software without data or ML focus, static code refactoring, pure UI work.
## Domain vocabulary
Keep distinct: dataset vs model (different versioning, rollback, and validation semantics), training vs inference (different cost, latency, and failure modes), metric vs loss (metric answers the business question; loss guides optimization — conflating them produces wrong evaluation), experiment vs deployment (experiment is reversible exploration; deployment is a production commitment with reliability expectations), offline evaluation vs online evaluation (offline checks held-out data; online checks live behavior — claiming done from offline alone is the most common production failure in this domain).
## Diagnostic questions
Ask only when blocking: Is this a research experiment or a production deployment? What is the target metric and how will it be measured? Which dataset split and version will be used? What constitutes a regression? How will the model be monitored post-deployment?
## Extra brief fields
`dataset_version`, `model_version`, `target_metric`, `baseline`, `eval_harness`, `train_test_split`, `reproducibility_seed`, `deployment_target`, `monitoring_plan`
## Readiness additions
- target metric is defined and measurable before training starts
- dataset version and splits are fixed and documented
- baseline exists or is explicitly acknowledged as unknown
- evaluation harness exists or is defined as a deliverable in scope
- reproducibility requirements are explicit (seed, environment, dependency lock)
## Workstream patterns
- experiment: hypothesis → dataset prep → training run → offline eval → gap analysis → decision
- deployment: offline eval → staging integration → online eval → rollout gate → monitoring → incident plan
- data pipeline: source contract → schema validation → transformation → quality check → downstream contract
- fine-tuning: base model selection → dataset curation → tuning run → task eval vs base → regression check → versioning
## Review additions
Check metric-loss alignment, held-out set contamination, offline-vs-online evaluation gap, training-inference skew, reproducibility (seed and environment locked), monitoring coverage, and that research claims are bounded to the evaluation population and not generalized beyond it.
## Completion checks
Target metric measured on held-out set, eval harness committed to version control, model artifact versioned and retrievable, monitoring or alerting defined when deploying to production, limitations bounded to evaluation conditions, and the next experiment or deployment decision is explicit.
## Common traps
Tuning on the test set, claiming production readiness from offline evaluation alone, treating accuracy as the only metric, skipping a baseline comparison, and deploying without a monitoring plan.
