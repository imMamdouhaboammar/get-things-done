# Behavioral evaluation results

This directory is reserved for **actual executed** behavioral run records and comparison artifacts.

No JSON result files are committed by default.

A corpus is not a benchmark, and a generated ungraded run template is not evidence of model performance.

Before committing a result:

- run the prompts in the declared provider/model/host environment
- preserve raw response artifacts or equivalent evidence
- record response hashes and grader identity
- validate the completed run with `scripts/behavioral_evals.py validate-run`
- for improvement claims, produce a controlled comparison with the same provider/model/host/settings

Do not commit fabricated baseline or candidate results merely to satisfy a release checklist.
