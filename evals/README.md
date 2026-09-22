# Evaluation datasets

This directory contains deterministic evaluation contracts and behavioral pressure suites.

## Suites

- **`cases.jsonl`**: core GTD behavioral pressure cases
- **`domain-routing-cases.jsonl`**: selection, non-selection, zero-pack, and wrong-pack cases for all nine built-in domain packs
- **`adapter-cases.jsonl`**: adapter conformance expectations
- **`interop-cases.jsonl`**: companion-tool boundary expectations
- **`gtd-capability-router-cases.jsonl`**: capability ownership and evidence-routing pressure cases
- **`gtd-deliberation-cases.jsonl`**: freshness, challenge, reframing, approval, and backlog pressure cases
- **`domain-pack-evals.json`**: legacy builder-skill trigger examples; not the runtime domain-routing corpus

A case corpus is **not** an executed benchmark.

## Behavioral case contract

Each executable JSONL case contains:

- `schema_version`
- stable `id`
- `category`
- `prompt`
- named `expected[]` behaviors
- named `forbidden[]` behaviors
- `evidence_required[]`
- machine-readable `metadata`

Named behavior IDs make grading falsifiable. A reviewer records which expected behaviors were observed and which forbidden behaviors occurred.

Validate the core and domain suites:

```bash
python scripts/behavioral_evals.py validate-suite evals/cases.jsonl
python scripts/behavioral_evals.py validate-suite evals/domain-routing-cases.jsonl
```

## Run contract

Create a baseline run template:

```bash
python scripts/behavioral_evals.py new-run \
  --suite evals/cases.jsonl \
  --label baseline \
  --provider PROVIDER \
  --model MODEL \
  --host HOST \
  --source-sha FULL_40_CHAR_COMMIT_SHA \
  --skill-mode without_skill \
  --settings-json '{"temperature":0}' \
  --out evals/work/baseline.json
```

Create a candidate with the same provider, model, host, and settings. The source SHA and skill mode may differ.

Run each prompt in a fresh context using the declared environment and preserve the raw response artifact.

Record a case judgment:

```bash
python scripts/behavioral_evals.py grade evals/work/baseline.json \
  --case messy-software \
  --response-file responses/messy-software.txt \
  --met separate-outcome \
  --met surface-unknowns \
  --met next-executable-action \
  --grader-kind human \
  --grader-name reviewer-name
```

Use `--seen <forbidden-id>` for every forbidden behavior observed.

The recorder stores the response SHA-256, not the response body. Keep the raw response artifact wherever the evaluation protocol permits; its hash binds the judgment to that exact response.

Validate a completed run:

```bash
python scripts/behavioral_evals.py validate-run evals/work/baseline.json
```

An ungraded template is not a completed result and fails normal validation. Use `--allow-ungraded` only while preparing a run.

## Baseline/candidate comparison

```bash
python scripts/behavioral_evals.py compare \
  evals/work/baseline.json \
  evals/work/candidate.json \
  --out evals/work/comparison.json
```

Comparison fails closed if the suite revision differs or provider/model/host/settings drift. It reports case-level improved, regressed, unchanged-pass, and unchanged-fail outcomes together with missing expected behaviors and observed forbidden behaviors.

## Release evidence policy

Do not claim behavioral improvement because:

- a corpus exists
- deterministic CI is green
- one anecdotal prompt looked better
- a model graded itself without a recorded run contract

A behavioral improvement claim should link to:

1. the exact suite revision
2. baseline and candidate run records
3. the comparison artifact
4. provider/model/host/settings metadata
5. the source SHAs being compared
6. retained response artifacts or equivalent evidence bound by the recorded hashes

The repository currently ships the harness and corpora, **not an invented baseline benchmark**. Commit real result artifacts under `evals/results/` only after an actual controlled run.

## Deterministic vs probabilistic evidence

Repository CI can deterministically validate:

- case structure
- unique IDs
- coverage of documented failure classes
- run-record consistency
- comparison rules
- domain-pack corpus coverage

CI does not prove that a live model follows the Skill. Live behavioral runs remain a separate qualification activity.

## Adapter and companion conformance

These datasets are validated deterministically:

```bash
pytest tests/test_adapter_evals.py -v
```
