#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

CASE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
GRADER_KINDS = {"human", "model", "hybrid"}
SKILL_MODES = {"without_skill", "with_skill", "custom"}


class EvalError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvalError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise EvalError(f"{path}: top-level value must be an object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_suite(path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EvalError(f"cannot read suite {path}: {exc}") from exc

    cases: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(case, dict):
            raise EvalError(f"{path}:{line_number}: case must be an object")
        cases.append(case)
    if not cases:
        raise EvalError(f"{path}: suite is empty")
    validate_suite_cases(cases, path)
    return cases


def _behavior_ids(case: dict[str, Any], field: str) -> list[str]:
    entries = case.get(field)
    if not isinstance(entries, list) or not entries:
        raise EvalError(f"{case.get('id', '<unknown>')}: {field} must be a non-empty array")
    ids: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise EvalError(f"{case.get('id', '<unknown>')}: {field}[{index}] must be an object")
        behavior_id = entry.get("id")
        description = entry.get("description")
        if not isinstance(behavior_id, str) or CASE_ID_PATTERN.fullmatch(behavior_id) is None:
            raise EvalError(f"{case.get('id', '<unknown>')}: invalid {field}[{index}].id")
        if not isinstance(description, str) or not description.strip():
            raise EvalError(f"{case.get('id', '<unknown>')}: {field}[{index}].description must be non-empty")
        ids.append(behavior_id)
    if len(ids) != len(set(ids)):
        raise EvalError(f"{case.get('id', '<unknown>')}: duplicate IDs in {field}")
    return ids


def validate_suite_cases(cases: list[dict[str, Any]], path: Path | None = None) -> None:
    seen: set[str] = set()
    for index, case in enumerate(cases):
        case_id = case.get("id")
        prefix = f"{path or 'suite'}:{index + 1}"
        if case.get("schema_version") != 1:
            raise EvalError(f"{prefix}: schema_version must be 1")
        if not isinstance(case_id, str) or CASE_ID_PATTERN.fullmatch(case_id) is None:
            raise EvalError(f"{prefix}: invalid case id")
        if case_id in seen:
            raise EvalError(f"{prefix}: duplicate case id {case_id}")
        seen.add(case_id)
        for field in ("category", "prompt"):
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                raise EvalError(f"{case_id}: {field} must be a non-empty string")
        expected = _behavior_ids(case, "expected")
        forbidden = _behavior_ids(case, "forbidden")
        overlap = sorted(set(expected) & set(forbidden))
        if overlap:
            raise EvalError(f"{case_id}: behavior IDs cannot be both expected and forbidden: {', '.join(overlap)}")
        evidence = case.get("evidence_required")
        if not isinstance(evidence, list) or not evidence or not all(isinstance(item, str) and item.strip() for item in evidence):
            raise EvalError(f"{case_id}: evidence_required must be a non-empty string array")
        metadata = case.get("metadata")
        if not isinstance(metadata, dict):
            raise EvalError(f"{case_id}: metadata must be an object")


def suite_identity(path: Path, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "sha256": sha256_file(path),
        "case_count": len(cases),
    }


def build_run_template(
    suite_path: Path,
    *,
    label: str,
    provider: str,
    model: str,
    host: str,
    source_sha: str,
    skill_mode: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    cases = load_suite(suite_path)
    source_sha = source_sha.lower()
    if SHA_PATTERN.fullmatch(source_sha) is None:
        raise EvalError("source_sha must be a full 40-character commit SHA")
    for name, value in (("label", label), ("provider", provider), ("model", model), ("host", host)):
        if not isinstance(value, str) or not value.strip():
            raise EvalError(f"{name} must be non-empty")
    if skill_mode not in SKILL_MODES:
        raise EvalError(f"skill_mode must be one of: {', '.join(sorted(SKILL_MODES))}")
    if not isinstance(settings, dict):
        raise EvalError("settings must be an object")

    results = []
    for case in cases:
        results.append(
            {
                "case_id": case["id"],
                "expected_ids": _behavior_ids(case, "expected"),
                "forbidden_ids": _behavior_ids(case, "forbidden"),
                "response_sha256": None,
                "expected_met": [],
                "forbidden_seen": [],
                "grader": {"kind": "ungraded", "name": None},
                "notes": None,
                "passed": None,
            }
        )
    return {
        "schema_version": 1,
        "suite": suite_identity(suite_path, cases),
        "environment": {
            "label": label,
            "provider": provider,
            "model": model,
            "host": host,
            "source_sha": source_sha,
            "skill_mode": skill_mode,
            "settings": settings,
        },
        "results": results,
    }


def _result_by_case(run: dict[str, Any], case_id: str) -> dict[str, Any]:
    results = run.get("results")
    if not isinstance(results, list):
        raise EvalError("run.results must be an array")
    matches = [item for item in results if isinstance(item, dict) and item.get("case_id") == case_id]
    if len(matches) != 1:
        raise EvalError(f"run must contain exactly one result for case {case_id}")
    return matches[0]


def grade_case(
    run: dict[str, Any],
    *,
    case_id: str,
    response_path: Path,
    expected_met: list[str],
    forbidden_seen: list[str],
    grader_kind: str,
    grader_name: str,
    notes: str | None,
) -> None:
    result = _result_by_case(run, case_id)
    if grader_kind not in GRADER_KINDS:
        raise EvalError(f"grader_kind must be one of: {', '.join(sorted(GRADER_KINDS))}")
    if not grader_name.strip():
        raise EvalError("grader_name must be non-empty")
    if not response_path.is_file():
        raise EvalError(f"response file not found: {response_path}")

    expected_ids = set(result.get("expected_ids", []))
    forbidden_ids = set(result.get("forbidden_ids", []))
    met = set(expected_met)
    seen = set(forbidden_seen)
    unknown_met = sorted(met - expected_ids)
    unknown_seen = sorted(seen - forbidden_ids)
    if unknown_met:
        raise EvalError(f"{case_id}: unknown expected IDs: {', '.join(unknown_met)}")
    if unknown_seen:
        raise EvalError(f"{case_id}: unknown forbidden IDs: {', '.join(unknown_seen)}")

    result["response_sha256"] = sha256_file(response_path)
    result["expected_met"] = sorted(met)
    result["forbidden_seen"] = sorted(seen)
    result["grader"] = {"kind": grader_kind, "name": grader_name}
    result["notes"] = notes
    result["passed"] = met == expected_ids and not seen


def validate_run(run: dict[str, Any], *, require_complete: bool = True) -> None:
    if run.get("schema_version") != 1:
        raise EvalError("run.schema_version must be 1")
    suite = run.get("suite")
    environment = run.get("environment")
    results = run.get("results")
    if not isinstance(suite, dict):
        raise EvalError("run.suite must be an object")
    if not isinstance(suite.get("path"), str) or not suite["path"]:
        raise EvalError("run.suite.path must be non-empty")
    if not isinstance(suite.get("sha256"), str) or HASH_PATTERN.fullmatch(suite["sha256"]) is None:
        raise EvalError("run.suite.sha256 must be a SHA-256 hex digest")
    if not isinstance(suite.get("case_count"), int) or suite["case_count"] < 1:
        raise EvalError("run.suite.case_count must be positive")

    if not isinstance(environment, dict):
        raise EvalError("run.environment must be an object")
    for key in ("label", "provider", "model", "host"):
        if not isinstance(environment.get(key), str) or not environment[key].strip():
            raise EvalError(f"run.environment.{key} must be non-empty")
    source_sha = environment.get("source_sha")
    if not isinstance(source_sha, str) or SHA_PATTERN.fullmatch(source_sha) is None:
        raise EvalError("run.environment.source_sha must be a full commit SHA")
    if environment.get("skill_mode") not in SKILL_MODES:
        raise EvalError("run.environment.skill_mode is invalid")
    if not isinstance(environment.get("settings"), dict):
        raise EvalError("run.environment.settings must be an object")

    if not isinstance(results, list) or len(results) != suite["case_count"]:
        raise EvalError("run.results count must equal suite.case_count")
    case_ids: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            raise EvalError("run result must be an object")
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or CASE_ID_PATTERN.fullmatch(case_id) is None:
            raise EvalError("run result has invalid case_id")
        case_ids.append(case_id)

        expected_ids = item.get("expected_ids")
        forbidden_ids = item.get("forbidden_ids")
        expected_met = item.get("expected_met")
        forbidden_seen = item.get("forbidden_seen")
        if not all(isinstance(value, list) for value in (expected_ids, forbidden_ids, expected_met, forbidden_seen)):
            raise EvalError(f"{case_id}: behavior ID fields must be arrays")
        if len(expected_ids) != len(set(expected_ids)) or len(forbidden_ids) != len(set(forbidden_ids)):
            raise EvalError(f"{case_id}: duplicate behavior IDs in run result")
        if not set(expected_met) <= set(expected_ids):
            raise EvalError(f"{case_id}: expected_met contains unknown IDs")
        if not set(forbidden_seen) <= set(forbidden_ids):
            raise EvalError(f"{case_id}: forbidden_seen contains unknown IDs")

        response_hash = item.get("response_sha256")
        grader = item.get("grader")
        passed = item.get("passed")
        if require_complete:
            if not isinstance(response_hash, str) or HASH_PATTERN.fullmatch(response_hash) is None:
                raise EvalError(f"{case_id}: response_sha256 is required for a complete run")
            if not isinstance(grader, dict) or grader.get("kind") not in GRADER_KINDS:
                raise EvalError(f"{case_id}: complete run requires a human/model/hybrid grader")
            if not isinstance(grader.get("name"), str) or not grader["name"].strip():
                raise EvalError(f"{case_id}: grader.name must be non-empty")
            derived = set(expected_met) == set(expected_ids) and not forbidden_seen
            if passed is not derived:
                raise EvalError(f"{case_id}: passed does not match recorded behavior evidence")
        else:
            if passed not in {None, True, False}:
                raise EvalError(f"{case_id}: passed must be true, false, or null")

    if len(case_ids) != len(set(case_ids)):
        raise EvalError("run contains duplicate case IDs")


def _comparison_environment(environment: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": environment["provider"],
        "model": environment["model"],
        "host": environment["host"],
        "settings": environment["settings"],
    }


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    validate_run(baseline, require_complete=True)
    validate_run(candidate, require_complete=True)
    if baseline["suite"]["sha256"] != candidate["suite"]["sha256"]:
        raise EvalError("baseline and candidate use different suite revisions")
    if _comparison_environment(baseline["environment"]) != _comparison_environment(candidate["environment"]):
        raise EvalError("baseline and candidate environment metadata differ; comparison would not be controlled")

    baseline_results = {item["case_id"]: item for item in baseline["results"]}
    candidate_results = {item["case_id"]: item for item in candidate["results"]}
    if set(baseline_results) != set(candidate_results):
        raise EvalError("baseline and candidate case IDs differ")

    deltas = []
    counts = {"improved": 0, "regressed": 0, "unchanged_pass": 0, "unchanged_fail": 0}
    for case_id in sorted(baseline_results):
        before = bool(baseline_results[case_id]["passed"])
        after = bool(candidate_results[case_id]["passed"])
        if not before and after:
            outcome = "improved"
        elif before and not after:
            outcome = "regressed"
        elif before and after:
            outcome = "unchanged_pass"
        else:
            outcome = "unchanged_fail"
        counts[outcome] += 1
        deltas.append(
            {
                "case_id": case_id,
                "baseline_passed": before,
                "candidate_passed": after,
                "outcome": outcome,
                "baseline_forbidden_seen": baseline_results[case_id]["forbidden_seen"],
                "candidate_forbidden_seen": candidate_results[case_id]["forbidden_seen"],
                "baseline_missing_expected": sorted(
                    set(baseline_results[case_id]["expected_ids"]) - set(baseline_results[case_id]["expected_met"])
                ),
                "candidate_missing_expected": sorted(
                    set(candidate_results[case_id]["expected_ids"]) - set(candidate_results[case_id]["expected_met"])
                ),
            }
        )

    total = len(deltas)
    baseline_passed = sum(bool(item["passed"]) for item in baseline_results.values())
    candidate_passed = sum(bool(item["passed"]) for item in candidate_results.values())
    return {
        "schema_version": 1,
        "suite": baseline["suite"],
        "controlled_environment": _comparison_environment(baseline["environment"]),
        "baseline": {
            "label": baseline["environment"]["label"],
            "source_sha": baseline["environment"]["source_sha"],
            "skill_mode": baseline["environment"]["skill_mode"],
            "passed": baseline_passed,
            "total": total,
        },
        "candidate": {
            "label": candidate["environment"]["label"],
            "source_sha": candidate["environment"]["source_sha"],
            "skill_mode": candidate["environment"]["skill_mode"],
            "passed": candidate_passed,
            "total": total,
        },
        "summary": counts,
        "cases": deltas,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and compare GTD behavioral evaluation runs")
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("validate-suite")
    command.add_argument("suite", type=Path)

    command = sub.add_parser("new-run")
    command.add_argument("--suite", type=Path, required=True)
    command.add_argument("--label", required=True)
    command.add_argument("--provider", required=True)
    command.add_argument("--model", required=True)
    command.add_argument("--host", required=True)
    command.add_argument("--source-sha", required=True)
    command.add_argument("--skill-mode", choices=sorted(SKILL_MODES), required=True)
    command.add_argument("--settings-json", default="{}")
    command.add_argument("--out", type=Path, required=True)

    command = sub.add_parser("grade")
    command.add_argument("run", type=Path)
    command.add_argument("--case", required=True)
    command.add_argument("--response-file", type=Path, required=True)
    command.add_argument("--met", action="append", default=[])
    command.add_argument("--seen", action="append", default=[])
    command.add_argument("--grader-kind", choices=sorted(GRADER_KINDS), required=True)
    command.add_argument("--grader-name", required=True)
    command.add_argument("--notes")

    command = sub.add_parser("validate-run")
    command.add_argument("run", type=Path)
    command.add_argument("--allow-ungraded", action="store_true")

    command = sub.add_parser("compare")
    command.add_argument("baseline", type=Path)
    command.add_argument("candidate", type=Path)
    command.add_argument("--out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate-suite":
            cases = load_suite(args.suite)
            print(f"VALID: {len(cases)} cases")
            return 0

        if args.command == "new-run":
            try:
                settings = json.loads(args.settings_json)
            except json.JSONDecodeError as exc:
                raise EvalError(f"invalid --settings-json: {exc}") from exc
            if not isinstance(settings, dict):
                raise EvalError("--settings-json must decode to an object")
            payload = build_run_template(
                args.suite,
                label=args.label,
                provider=args.provider,
                model=args.model,
                host=args.host,
                source_sha=args.source_sha,
                skill_mode=args.skill_mode,
                settings=settings,
            )
            write_json(args.out, payload)
            print(args.out)
            return 0

        if args.command == "grade":
            payload = read_json(args.run)
            validate_run(payload, require_complete=False)
            grade_case(
                payload,
                case_id=args.case,
                response_path=args.response_file,
                expected_met=args.met,
                forbidden_seen=args.seen,
                grader_kind=args.grader_kind,
                grader_name=args.grader_name,
                notes=args.notes,
            )
            validate_run(payload, require_complete=False)
            write_json(args.run, payload)
            result = _result_by_case(payload, args.case)
            print(f"{args.case}: {'PASS' if result['passed'] else 'FAIL'}")
            return 0

        if args.command == "validate-run":
            payload = read_json(args.run)
            validate_run(payload, require_complete=not args.allow_ungraded)
            print("VALID")
            return 0

        baseline = read_json(args.baseline)
        candidate = read_json(args.candidate)
        comparison = compare_runs(baseline, candidate)
        write_json(args.out, comparison)
        print(args.out)
        return 0
    except EvalError as exc:
        print(f"EVAL ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
