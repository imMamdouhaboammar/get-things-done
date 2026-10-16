import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "get-things-done" / "scripts"))
from chatgpt_bridge import ChatgptBridge
import gtd


def test_bridge_binary_discovery():
    bridge = ChatgptBridge(pack_root=ROOT)
    assert bridge.is_available()
    bin_path = bridge.find_binary()
    assert bin_path is not None
    assert bin_path.is_file()


def test_route_intent_extracts_domain_and_packet():
    bridge = ChatgptBridge(pack_root=ROOT)
    res = bridge.route_intent("refactor auth token verification")
    assert res["success"] is True
    assert res["domain"] in ["SecurityAudit", "FeatureImplementation", "BugDebugging"]
    assert "mission" in res["packet"]
    assert "ownership" in res["packet"]
    assert "flowchart TD" in res["dag"]


def test_bot_gate_inspect_extracts_dispositions():
    bridge = ChatgptBridge(pack_root=ROOT)
    res = bridge.inspect_bot_gate()
    assert res["success"] is True
    assert isinstance(res["comments"], list)
    assert len(res["comments"]) > 0
    assert any(c["disposition"] == "CURRENT_ACTIONABLE" for c in res["comments"])
    assert res["actionable_count"] >= 1


def test_evidence_trust_ladder_classification():
    bridge = ChatgptBridge(pack_root=ROOT)
    cases = [
        ("pytest tests/test_pack.py passed with 15 passed", "LEVEL A: MACHINE PROOF"),
        ("Live API endpoint curl returns 200 OK", "LEVEL B: INTEGRATION PROOF"),
        ("CLI command output observed on stdout", "LEVEL C: OBSERVED RUNTIME"),
        ("Inspected schema definition in JSON file", "LEVEL D: STATIC INSPECTION"),
        ("Everything looks good to ship", "LEVEL E: CONTEXT / ASSERTION"),
    ]
    for text, expected in cases:
        assert bridge.classify_evidence_level(text) == expected

    eval_result = bridge.evaluate_evidence([c[0] for c in cases])
    assert eval_result["highest_level"] == "LEVEL A: MACHINE PROOF"
    assert eval_result["is_sufficient_for_done"] is True


def test_enrich_brief_with_route_workflow(tmp_path):
    bridge = ChatgptBridge(pack_root=ROOT)
    brief = gtd.blank_brief("Auth Refactor", "software")
    enriched = bridge.enrich_brief_with_route(brief, "refactor auth token verification")

    assert enriched["title"] == "Auth Refactor"
    assert len(enriched["knowledge"]["facts"]) >= 2
    assert len(enriched["workstreams"]) >= 1
    assert len(enriched["deliverables"]) >= 1
    assert len(enriched["verification"]["success_criteria"]) >= 1
    assert "chatgpt_routing" in enriched["domain_data"]

    errors = gtd.validate_brief(enriched)
    assert not errors, errors

    # Test empty title hydration
    blank_b = gtd.blank_brief("", "software")
    hydrated_b = bridge.enrich_brief_with_route(blank_b, "refactor auth token verification")
    assert hydrated_b["title"] == "refactor auth token verification"


def test_enrich_brief_with_bot_gate_injects_blockers(tmp_path):
    bridge = ChatgptBridge(pack_root=ROOT)
    brief = gtd.blank_brief("Auth Refactor", "software")
    enriched = bridge.enrich_brief_with_bot_gate(brief)

    assert len(enriched["blockers"]) >= 1
    assert any("coderabbitai" in b for b in enriched["blockers"])
    assert any("Stale review skipped" in f for f in enriched["knowledge"]["facts"])
    assert "bot_gate" in enriched["domain_data"]

    errors = gtd.validate_brief(enriched)
    assert not errors, errors


def test_cli_chatgpt_route_into_brief_and_validate(tmp_path):
    brief_out = tmp_path / "hydrated_brief.json"
    cli_path = ROOT / "scripts" / "gtd.py"

    cmd = [
        sys.executable,
        str(cli_path),
        "chatgpt-route",
        "fix critical memory leak in worker",
        "--into-brief",
        str(brief_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert res.returncode == 0, res.stderr
    assert brief_out.is_file()

    # Validate brief
    val_cmd = [sys.executable, str(cli_path), "validate-brief", str(brief_out)]
    val_res = subprocess.run(val_cmd, capture_output=True, text=True, check=False)
    assert val_res.returncode == 0
    assert "VALID" in val_res.stdout


def test_cli_bot_gate_into_brief(tmp_path):
    brief_out = tmp_path / "bot_brief.json"
    cli_path = ROOT / "scripts" / "gtd.py"

    # Create blank brief first
    gtd.cmd_new_brief(
        type("Args", (), {"out": str(brief_out), "title": "PR Task", "domain": "software", "force": True})
    )

    cmd = [
        sys.executable,
        str(cli_path),
        "bot-gate",
        "--into-brief",
        str(brief_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert res.returncode == 0, res.stderr
    assert "INGESTED" in res.stdout

    payload = json.loads(brief_out.read_text(encoding="utf-8"))
    assert len(payload["blockers"]) >= 1


def test_cli_evidence_ladder(tmp_path):
    brief_out = tmp_path / "evidence_brief.json"
    cli_path = ROOT / "scripts" / "gtd.py"

    payload = gtd.blank_brief("Evidence Test", "software")
    payload["verification"]["evidence"] = [
        "pytest run verified 150 passed",
        "inspected log traces manually",
    ]
    brief_out.write_text(json.dumps(payload), encoding="utf-8")

    cmd = [
        sys.executable,
        str(cli_path),
        "evidence-ladder",
        str(brief_out),
        "--into-brief",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert res.returncode == 0, res.stderr
    assert "GRADED" in res.stdout

    updated = json.loads(brief_out.read_text(encoding="utf-8"))
    assert updated["domain_data"]["evidence_grade"]["highest_level"] == "LEVEL A: MACHINE PROOF"
    assert updated["domain_data"]["evidence_grade"]["is_sufficient_for_done"] is True


def test_macos_clipboard_roundtrip():
    bridge = ChatgptBridge(pack_root=ROOT)
    if sys.platform != "darwin":
        pytest.skip("macOS specific test")
    unique_text = "GTD-ChatGPT-Bridge-Token-987123"
    assert bridge.macos_copy(unique_text) is True
    pasted = bridge.macos_paste().strip()
    assert pasted == unique_text
