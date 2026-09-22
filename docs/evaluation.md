# Evaluation

GTD separates deterministic repository verification from behavioral agent evaluation. They answer different questions and must not be collapsed into one green badge.

## Deterministic verification

The Python/CLI suite can prove repository mechanics such as:

- required Skill files and frontmatter
- core and domain-pack structural invariants
- Execution Brief schema and semantic validation
- CLI behavior and exit contracts
- package/install/release failure paths
- adapter and companion conformance
- deterministic packaging and checksums
- behavioral suite and run-record structure

Run:

```bash
pytest -v
python scripts/catalog_stylist.py --validate
python scripts/gtd.py doctor
python scripts/behavioral_evals.py validate-suite evals/cases.jsonl
python scripts/behavioral_evals.py validate-suite evals/domain-routing-cases.jsonl
```

A green deterministic run does not prove live model behavior.

## Behavioral regression system

The canonical recorder/comparator is:

```bash
python scripts/behavioral_evals.py --help
```

It deliberately does not call a model provider itself. The response can come from ChatGPT, Claude, Codex, another agent host, or a controlled test harness. GTD records the evidence and comparison contract without pretending provider execution is deterministic.

Every run records:

- suite SHA-256 and case count
- label
- provider
- model
- host
- exact source commit SHA
- Skill mode
- provider/host settings
- per-case response SHA-256
- expected behaviors observed
- forbidden behaviors observed
- grader kind and identity
- derived pass/fail

The grader may be `human`, `model`, or `hybrid`. The record makes that choice explicit rather than treating model grading as ground truth.

## Core behavior suite

[`evals/cases.jsonl`](../evals/cases.jsonl) covers pressure classes including:

- unnecessary question dumping
- discoverable-fact delegation
- assumptions presented as facts
- solution/channel-first framing
- plan-only behavior when execution is authorized
- false completion claims
- ceremony inflation
- wrong-domain forcing
- unsafe autonomy
- stale-state continuation
- simulated unavailable tools

Each case has named expected and forbidden behaviors.

## Domain routing suite

[`evals/domain-routing-cases.jsonl`](../evals/domain-routing-cases.jsonl) gives every built-in domain pack:

- a positive selection case
- explicit non-selection evidence

It also includes:

- zero-pack routing
- wrong-pack routing
- the zero-or-one-pack invariant

The pack text and the corpus are checked together by `tests/test_domain_pack_audit.py`.

## Other pressure corpora

The repository also carries adapter, companion, capability-router, and deliberation corpora. Unless a run record and comparison artifact exist, describe them as corpora or pressure cases, not measured benchmarks.

## Running a controlled comparison

Create baseline and candidate templates with the same provider/model/host/settings:

```bash
python scripts/behavioral_evals.py new-run --suite evals/cases.jsonl \
  --label baseline --provider PROVIDER --model MODEL --host HOST \
  --source-sha BASELINE_SHA --skill-mode without_skill \
  --settings-json '{"temperature":0}' --out baseline.json

python scripts/behavioral_evals.py new-run --suite evals/cases.jsonl \
  --label candidate --provider PROVIDER --model MODEL --host HOST \
  --source-sha CANDIDATE_SHA --skill-mode with_skill \
  --settings-json '{"temperature":0}' --out candidate.json
```

Execute each case in a fresh context, preserve the response artifact, and record the judgment with `grade`.

Validate both runs, then compare:

```bash
python scripts/behavioral_evals.py validate-run baseline.json
python scripts/behavioral_evals.py validate-run candidate.json
python scripts/behavioral_evals.py compare baseline.json candidate.json --out comparison.json
```

The comparator rejects environment drift rather than producing a misleading score.

## Release rule

A release may claim deterministic repository checks passed when the deterministic checks passed.

A release must not claim behavioral improvement without recorded behavioral evidence. Such a claim should link to the baseline run, candidate run, comparison artifact, exact suite revision, environment metadata, and retained response evidence.

No percentage target should be invented before a controlled baseline exists.

See [`evals/README.md`](../evals/README.md) for the operational commands and result policy.
