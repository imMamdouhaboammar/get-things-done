import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gtd.py"
EXAMPLE_PLAN = ROOT / "skills" / "improve" / "examples" / "001-extract-shadow-config-resolution.md"

sys.path.insert(0, str(ROOT / "skills" / "get-things-done" / "scripts"))
from improve_bridge import ImproveBridge
from gtd import validate_brief


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, capture_output=True, text=True)


def test_improve_bridge_parses_example_plan():
    bridge = ImproveBridge(ROOT)
    text = EXAMPLE_PLAN.read_text(encoding="utf-8")
    data = bridge.parse_plan(text)

    assert data["number"] == "001"
    assert "shadow-config resolution" in data["title"].lower()
    assert data["status"]["priority"] == "P2"
    assert data["status"]["effort"] == "M"
    assert data["status"]["risk"] == "MED"
    assert len(data["why_this_matters"]) > 20
    assert len(data["current_state"]) > 10
    assert len(data["commands"]) >= 2
    assert any("config.ts" in f for f in data["scope_in"])
    assert len(data["steps"]) >= 2
    assert len(data["done_criteria"]) >= 3
    assert len(data["stop_conditions"]) >= 1


def test_improve_bridge_validates_plan_correctness_and_invariants():
    bridge = ImproveBridge(ROOT)
    text = EXAMPLE_PLAN.read_text(encoding="utf-8")
    errors = bridge.validate_plan(text)
    assert not errors, f"expected no errors on example plan: {errors}"

    # Missing title
    bad_plan = text.replace("# Plan 001: Extract shared shadow-config resolution used by search and view", "")
    assert any("title" in err.lower() for err in bridge.validate_plan(bad_plan))

    # Secret leakage rejection
    leaky_plan = text + "\n- Stripe key: sk-live-1234567890abcdef1234567890\n"
    errors = bridge.validate_plan(leaky_plan)
    assert any("security invariant" in err.lower() for err in errors)

    # Dangling reference rejection
    relative_plan = text + "\nFollow the refactor as discussed above in previous message.\n"
    errors = bridge.validate_plan(relative_plan)
    assert any("self-containment" in err.lower() for err in errors)


def test_improve_bridge_converts_to_v1_brief_and_validates():
    bridge = ImproveBridge(ROOT)
    text = EXAMPLE_PLAN.read_text(encoding="utf-8")
    parsed = bridge.parse_plan(text)
    brief = bridge.plan_to_brief(parsed, version="1.0", domain="software")

    assert brief["version"] == "1.0"
    assert brief["title"] == parsed["title"]
    assert brief["domain"] == "software"
    assert len(brief["workstreams"]) >= 2
    assert len(brief["verification"]["success_criteria"]) >= 3

    errors = validate_brief(brief, root=ROOT)
    assert not errors, f"v1 brief validation failed: {errors}"


def test_improve_bridge_converts_to_v2_brief_and_validates():
    bridge = ImproveBridge(ROOT)
    text = EXAMPLE_PLAN.read_text(encoding="utf-8")
    parsed = bridge.parse_plan(text)
    brief = bridge.plan_to_brief(parsed, version="2.0", domain="software")

    assert brief["version"] == "2.0"
    assert brief["title"] == parsed["title"]
    assert brief["domain"] == "software"
    assert len(brief["workstreams"]) >= 2
    assert len(brief["verification"]["criteria"]) >= 3

    errors = validate_brief(brief, root=ROOT)
    assert not errors, f"v2 brief validation failed: {errors}"


def test_cli_improve_ingest(tmp_path: Path):
    out_v1 = tmp_path / "brief-v1.json"
    res = run_cli("improve-ingest", str(EXAMPLE_PLAN), "--out", str(out_v1), "--version", "1.0")
    assert res.returncode == 0, res.stdout + res.stderr
    assert out_v1.is_file()
    payload = json.loads(out_v1.read_text())
    assert payload["version"] == "1.0"
    assert payload["domain"] == "software"

    out_v2 = tmp_path / "brief-v2.json"
    res = run_cli("improve-ingest", str(EXAMPLE_PLAN), "--out", str(out_v2), "--version", "2.0")
    assert res.returncode == 0, res.stdout + res.stderr
    assert out_v2.is_file()
    payload2 = json.loads(out_v2.read_text())
    assert payload2["version"] == "2.0"


def test_cli_improve_validate():
    res = run_cli("improve-validate", str(EXAMPLE_PLAN))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "PASS" in res.stdout


def test_cli_improve_plan_scaffold(tmp_path: Path):
    plan_out = tmp_path / "002-scaffold.md"
    res = run_cli(
        "improve-plan",
        "--title", "Refactor session state store",
        "--category", "tech-debt",
        "--priority", "P1",
        "--out", str(plan_out),
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert plan_out.is_file()

    validate_res = run_cli("improve-validate", str(plan_out))
    assert validate_res.returncode == 0, validate_res.stdout + validate_res.stderr
    assert "PASS" in validate_res.stdout
