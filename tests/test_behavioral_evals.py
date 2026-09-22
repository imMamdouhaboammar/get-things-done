import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/behavioral_evals.py"
CORE_SUITE = ROOT / "evals/cases.jsonl"
DOMAIN_SUITE = ROOT / "evals/domain-routing-cases.jsonl"

spec = importlib.util.spec_from_file_location("gtd_behavioral_evals", SCRIPT)
evals = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(evals)


def complete_run(template: dict, tmp_path: Path, *, fail_case: str | None = None) -> dict:
    response = tmp_path / "response.txt"
    response.write_text("recorded response", encoding="utf-8")
    for result in template["results"]:
        met = list(result["expected_ids"])
        seen: list[str] = []
        if result["case_id"] == fail_case:
            met = met[:-1]
        evals.grade_case(
            template,
            case_id=result["case_id"],
            response_path=response,
            expected_met=met,
            forbidden_seen=seen,
            grader_kind="human",
            grader_name="test-reviewer",
            notes=None,
        )
    evals.validate_run(template, require_complete=True)
    return template


def test_core_and_domain_suites_have_valid_machine_readable_contracts():
    core = evals.load_suite(CORE_SUITE)
    domains = evals.load_suite(DOMAIN_SUITE)
    assert len(core) >= 10
    assert len(domains) >= 20


def test_core_suite_covers_documented_failure_classes():
    cases = evals.load_suite(CORE_SUITE)
    failure_classes = {
        failure
        for case in cases
        for failure in case["metadata"].get("failure_classes", [])
    }
    expected = {
        "question-dumping",
        "assumption-as-fact",
        "channel-first",
        "plan-instead-of-execute",
        "fake-completion",
        "wrong-domain-routing",
        "ceremony-inflation",
        "unsafe-autonomy",
        "state-drift",
        "tool-honesty",
    }
    assert expected <= failure_classes


def test_run_template_records_reproducibility_metadata_and_is_deterministic():
    kwargs = dict(
        label="baseline",
        provider="example-provider",
        model="example-model",
        host="example-host",
        source_sha="a" * 40,
        skill_mode="without_skill",
        settings={"temperature": 0},
    )
    first = evals.build_run_template(CORE_SUITE, **kwargs)
    second = evals.build_run_template(CORE_SUITE, **kwargs)
    assert first == second
    assert first["suite"]["sha256"] == evals.sha256_file(CORE_SUITE)
    assert first["environment"]["settings"] == {"temperature": 0}
    assert all(item["passed"] is None for item in first["results"])


def test_complete_run_derives_pass_from_expected_and_forbidden_evidence(tmp_path):
    template = evals.build_run_template(
        CORE_SUITE,
        label="candidate",
        provider="provider",
        model="model",
        host="host",
        source_sha="b" * 40,
        skill_mode="with_skill",
        settings={},
    )
    run = complete_run(template, tmp_path, fail_case=template["results"][0]["case_id"])
    failed = run["results"][0]
    assert failed["passed"] is False
    assert len(failed["response_sha256"]) == 64
    assert failed["grader"] == {"kind": "human", "name": "test-reviewer"}


def test_compare_requires_controlled_environment_and_reports_regressions(tmp_path):
    common = dict(provider="provider", model="model", host="host", settings={"temperature": 0})
    baseline = evals.build_run_template(
        CORE_SUITE,
        label="baseline",
        source_sha="c" * 40,
        skill_mode="without_skill",
        **common,
    )
    candidate = evals.build_run_template(
        CORE_SUITE,
        label="candidate",
        source_sha="d" * 40,
        skill_mode="with_skill",
        **common,
    )
    first_case = baseline["results"][0]["case_id"]
    complete_run(baseline, tmp_path, fail_case=first_case)
    complete_run(candidate, tmp_path)
    comparison = evals.compare_runs(baseline, candidate)
    assert comparison["summary"]["improved"] == 1
    assert comparison["summary"]["regressed"] == 0
    assert comparison["candidate"]["passed"] == comparison["candidate"]["total"]


def test_compare_rejects_environment_drift(tmp_path):
    baseline = evals.build_run_template(
        CORE_SUITE,
        label="baseline",
        provider="provider",
        model="model-a",
        host="host",
        source_sha="e" * 40,
        skill_mode="without_skill",
        settings={},
    )
    candidate = evals.build_run_template(
        CORE_SUITE,
        label="candidate",
        provider="provider",
        model="model-b",
        host="host",
        source_sha="f" * 40,
        skill_mode="with_skill",
        settings={},
    )
    complete_run(baseline, tmp_path)
    complete_run(candidate, tmp_path)
    with pytest.raises(evals.EvalError, match="environment metadata differ"):
        evals.compare_runs(baseline, candidate)


def test_ungraded_template_cannot_masquerade_as_completed_run():
    template = evals.build_run_template(
        CORE_SUITE,
        label="baseline",
        provider="provider",
        model="model",
        host="host",
        source_sha="1" * 40,
        skill_mode="without_skill",
        settings={},
    )
    with pytest.raises(evals.EvalError, match="response_sha256"):
        evals.validate_run(template, require_complete=True)
    evals.validate_run(template, require_complete=False)


def test_unknown_behavior_ids_cannot_be_recorded(tmp_path):
    template = evals.build_run_template(
        CORE_SUITE,
        label="candidate",
        provider="provider",
        model="model",
        host="host",
        source_sha="2" * 40,
        skill_mode="with_skill",
        settings={},
    )
    response = tmp_path / "response.txt"
    response.write_text("response", encoding="utf-8")
    case_id = template["results"][0]["case_id"]
    with pytest.raises(evals.EvalError, match="unknown expected IDs"):
        evals.grade_case(
            template,
            case_id=case_id,
            response_path=response,
            expected_met=["invented-behavior-id"],
            forbidden_seen=[],
            grader_kind="human",
            grader_name="reviewer",
            notes=None,
        )


def test_suite_files_do_not_claim_executed_benchmark_results():
    results_dir = ROOT / "evals/results"
    if results_dir.exists():
        result_files = [path for path in results_dir.glob("*.json") if path.is_file()]
        assert not result_files, "Repository should not ship invented behavioral run results"
