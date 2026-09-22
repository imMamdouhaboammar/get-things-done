import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gtd.py"
V1_SCHEMA = json.loads((ROOT / "skills/get-things-done/references/execution-brief.schema.json").read_text())
V2_SCHEMA = json.loads((ROOT / "skills/get-things-done/references/execution-brief-v2.schema.json").read_text())


def run_cli(*args: str):
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, capture_output=True, text=True)


def valid_v1() -> dict:
    return {
        "version": "1.0",
        "title": "Legacy brief",
        "domain": "software",
        "intent": {"problem": "p", "desired_outcome": "o", "actor": "a"},
        "status": "modeling",
        "scope": {"in": ["x"], "out": [], "constraints": []},
        "knowledge": {"facts": [], "assumptions": [], "unknowns": []},
        "decisions": [],
        "open_decisions": [],
        "workstreams": [],
        "deliverables": ["artifact"],
        "risks": [],
        "domain_data": {},
        "verification": {"success_criteria": ["criterion"], "evidence": ["legacy evidence"]},
        "next_action": "act",
        "blockers": [],
    }


def new_v2(tmp_path: Path) -> tuple[Path, dict]:
    path = tmp_path / "v2.json"
    result = run_cli(
        "new-brief",
        "--version", "2.0",
        "--title", "V2 brief",
        "--domain", "software",
        "--out", str(path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(path.read_text())
    return path, payload


def test_schema_backed_v1_rejects_extra_top_level_and_nested_properties(tmp_path):
    payload = valid_v1()
    payload["unexpected"] = True
    path = tmp_path / "extra-top.json"
    path.write_text(json.dumps(payload))
    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 1
    assert "$.unexpected" in result.stdout

    payload = valid_v1()
    payload["intent"]["unexpected"] = "x"
    path = tmp_path / "extra-nested.json"
    path.write_text(json.dumps(payload))
    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 1
    assert "$.intent.unexpected" in result.stdout


def test_schema_backed_v1_rejects_malformed_nested_records(tmp_path):
    payload = valid_v1()
    payload["decisions"] = [{"decision": "ship"}]
    payload["workstreams"] = [{"name": "x", "outcome": "y", "dependencies": "not-an-array"}]
    path = tmp_path / "bad-nested.json"
    path.write_text(json.dumps(payload))

    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 1
    assert "$.decisions[0].rationale" in result.stdout
    assert "$.decisions[0].reversible" in result.stdout
    assert "$.workstreams[0].dependencies" in result.stdout


def test_blank_v2_is_valid_against_published_schema_and_cli(tmp_path):
    path, payload = new_v2(tmp_path)
    jsonschema.Draft202012Validator(V2_SCHEMA, format_checker=jsonschema.FormatChecker()).validate(payload)

    assert payload["revision"] == 1
    assert payload["plan_changes"][0]["trigger"] == "initial"
    assert payload["authority"] == {"actions": []}
    assert payload["attempts"] == []
    assert payload["reviews"] == []

    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALID v2.0" in result.stdout


def test_migration_is_conservative_schema_valid_and_records_provenance(tmp_path):
    source = valid_v1()
    source["status"] = "done"
    source["knowledge"]["unknowns"] = ["unknown root cause"]
    source["workstreams"] = [
        {"name": "A", "outcome": "a", "dependencies": []},
        {"name": "B", "outcome": "b", "dependencies": ["A"]},
    ]
    source_path = tmp_path / "v1.json"
    target_path = tmp_path / "v2.json"
    source_path.write_text(json.dumps(source))

    result = run_cli("migrate-brief", str(source_path), "--out", str(target_path), "--root", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr

    migrated = json.loads(target_path.read_text())
    jsonschema.Draft202012Validator(V2_SCHEMA, format_checker=jsonschema.FormatChecker()).validate(migrated)
    assert migrated["plan_changes"][0]["trigger"] == "migration"
    assert "status=done" in migrated["plan_changes"][0]["summary"]
    assert migrated["knowledge"]["unknowns"][0]["blocking"] is True
    assert all(item["parallel_safe"] is False for item in migrated["workstreams"])
    assert all(item["status"] != "done" for item in migrated["workstreams"])
    assert all(item["status"] == "pending" for item in migrated["deliverables"])
    assert migrated["verification"]["evidence"][0]["result"] == "inconclusive"
    assert migrated["verification"]["evidence"][0]["criterion_id"] is None
    assert migrated["terminal_state"] == "unverified"


def test_future_evidence_never_covers_v2_criterion(tmp_path):
    path, payload = new_v2(tmp_path)
    payload["status"] = "verifying"
    payload["outcome"]["desired_result"] = "verified result"
    payload["scope"]["in"] = ["result"]
    payload["active_frontier"] = {"mode": "verify", "reason": "verify", "exit_condition": "criterion passes"}
    payload["next_action"]["description"] = "verify"
    payload["deliverables"] = [{"id": "deliverable-1", "name": "result", "status": "done", "workstream_id": None}]
    payload["verification"]["criteria"] = [{
        "id": "criterion-1",
        "description": "proof",
        "required": True,
        "evidence_level": "direct",
        "freshness_hours": 24,
    }]
    future = datetime.now(timezone.utc) + timedelta(hours=2)
    payload["verification"]["evidence"] = [{
        "id": "evidence-1",
        "criterion_id": "criterion-1",
        "method": "test",
        "source": "test output",
        "observed_at": future.isoformat(),
        "result": "passed",
        "level": "direct",
        "limitations": "",
    }]
    payload["terminal_state"] = "verified_complete"
    path.write_text(json.dumps(payload))

    result = run_cli("assess-brief", str(path), "--json", "--require", "done", "--root", str(ROOT))
    assert result.returncode == 2, result.stdout + result.stderr
    assessment = json.loads(result.stdout)
    assert assessment["done"] is False
    assert assessment["requirement_met"] is False
    assert any("future" in item["reason"] for item in assessment["evidence_coverage"])


def test_duplicate_ids_across_referenceable_v2_collections_fail_closed(tmp_path):
    path, payload = new_v2(tmp_path)
    payload["workstreams"] = [{
        "id": "shared-1",
        "kind": "internal",
        "name": "work",
        "outcome": "done",
        "dependencies": [],
        "status": "pending",
        "owner": None,
        "estimate": 1,
        "parallel_safe": False,
        "completion_criteria": [],
    }]
    payload["verification"]["criteria"] = [{
        "id": "shared-1",
        "description": "criterion",
        "required": True,
        "evidence_level": "direct",
        "freshness_hours": None,
    }]
    path.write_text(json.dumps(payload))

    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 1
    assert "duplicate v2 id 'shared-1'" in result.stdout


def test_high_assurance_authority_uses_schema_action_model(tmp_path):
    path, payload = new_v2(tmp_path)
    payload["mode"] = "high-assurance"
    payload["outcome"]["desired_result"] = "safe action"
    payload["scope"]["in"] = ["action"]
    payload["active_frontier"] = {"mode": "model", "reason": "approval boundary", "exit_condition": "approved"}
    payload["next_action"]["description"] = "act"
    payload["verification"]["criteria"] = [{
        "id": "criterion-1",
        "description": "safe",
        "required": True,
        "evidence_level": "direct",
        "freshness_hours": None,
    }]
    payload["authority"]["actions"] = [{
        "id": "action-1",
        "description": "publish",
        "target": "public",
        "side_effect": "public",
        "reversible": False,
        "approval": "required",
        "status": "proposed",
    }]
    path.write_text(json.dumps(payload))

    result = run_cli("assess-brief", str(path), "--json", "--root", str(ROOT))
    assert result.returncode == 0
    assessment = json.loads(result.stdout)
    assert any("required approvals are missing: action-1" in gap for gap in assessment["ready_gaps"])

    payload["authority"]["actions"][0]["approval"] = "approved"
    payload["authority"]["actions"][0]["status"] = "authorized"
    path.write_text(json.dumps(payload))
    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr


def test_version_dispatch_rejects_unknown_and_never_migrates_implicitly(tmp_path):
    payload = valid_v1()
    payload["version"] = "3.0"
    path = tmp_path / "future.json"
    path.write_text(json.dumps(payload))
    result = run_cli("validate-brief", str(path), "--root", str(ROOT))
    assert result.returncode == 1
    assert "unsupported brief version" in result.stdout
    assert json.loads(path.read_text())["version"] == "3.0"


def test_assessment_exit_contract_is_additive_and_machine_consumable(tmp_path):
    path = tmp_path / "brief.json"
    payload = valid_v1()
    payload["scope"]["in"] = []
    path.write_text(json.dumps(payload))

    default = run_cli("assess-brief", str(path), "--json", "--root", str(ROOT))
    assert default.returncode == 0
    assert json.loads(default.stdout)["requirement"] == "valid"

    ready = run_cli("assess-brief", str(path), "--json", "--require", "ready", "--root", str(ROOT))
    assert ready.returncode == 2
    assert json.loads(ready.stdout)["requirement_met"] is False


def test_v1_unlinked_evidence_cannot_claim_verified_done(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(valid_v1()))
    result = run_cli("assess-brief", str(path), "--json", "--require", "done", "--root", str(ROOT))
    assert result.returncode == 2
    assessment = json.loads(result.stdout)
    assert assessment["done"] is False
    assert any("unlinked" in gap and "migrate to v2" in gap for gap in assessment["done_gaps"])


def test_local_validator_matches_jsonschema_on_representative_contract_cases(tmp_path):
    sys.path.insert(0, str(ROOT / "skills/get-things-done/scripts"))
    try:
        from schema_validation import validate_instance
    finally:
        sys.path.pop(0)

    cases = []
    v1 = valid_v1()
    cases.append((v1, V1_SCHEMA))
    bad_v1 = valid_v1()
    bad_v1["intent"]["extra"] = True
    cases.append((bad_v1, V1_SCHEMA))

    _, v2 = new_v2(tmp_path)
    cases.append((v2, V2_SCHEMA))
    bad_v2 = json.loads(json.dumps(v2))
    bad_v2["revision"] = 0
    cases.append((bad_v2, V2_SCHEMA))

    for payload, schema in cases:
        local_valid = not validate_instance(payload, schema)
        official_valid = not list(
            jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(payload)
        )
        assert local_valid == official_valid
