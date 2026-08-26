from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gtd.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)


def test_assess_brief_rejects_structurally_unready_and_unverified_work(tmp_path):
    brief = tmp_path / "brief.json"
    created = run_cli(
        "new-brief",
        "--title",
        "Brand-aware generation",
        "--domain",
        "software",
        "--out",
        str(brief),
    )
    assert created.returncode == 0, created.stdout + created.stderr

    assessed = run_cli("assess-brief", str(brief))
    assert assessed.returncode == 0, assessed.stdout + assessed.stderr
    assert "READY: NO" in assessed.stdout
    assert "DONE: NO" in assessed.stdout
    assert "success criteria are empty" in assessed.stdout
    assert "verification evidence is empty" in assessed.stdout


def test_assess_brief_accepts_structurally_ready_and_evidenced_work(tmp_path):
    brief = tmp_path / "brief.json"
    payload = {
        "version": "1.0",
        "title": "Validated deliverable",
        "domain": "software",
        "intent": {
            "problem": "A behavior is missing",
            "desired_outcome": "The behavior exists and is verified",
            "actor": "Engineering",
        },
        "status": "verifying",
        "scope": {"in": ["target behavior"], "out": [], "constraints": []},
        "knowledge": {"facts": [], "assumptions": [], "unknowns": []},
        "decisions": [],
        "open_decisions": [],
        "workstreams": [],
        "deliverables": ["implementation"],
        "risks": [],
        "domain_data": {},
        "verification": {
            "success_criteria": ["target test passes"],
            "evidence": ["pytest target test: passed"],
        },
        "next_action": "publish handoff",
        "blockers": [],
    }
    brief.write_text(json.dumps(payload), encoding="utf-8")

    assessed = run_cli("assess-brief", str(brief), "--json")
    assert assessed.returncode == 0, assessed.stdout + assessed.stderr
    result = json.loads(assessed.stdout)
    assert result["ready"] is True
    assert result["done"] is True
    assert result["ready_gaps"] == []
    assert result["done_gaps"] == []


def test_professional_docs_are_linkable_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in [
        "docs/architecture.md",
        "docs/quickstart.md",
        "docs/domain-packs.md",
        "docs/evaluation.md",
    ]:
        assert (ROOT / path).exists(), path
        assert path in readme


def test_skill_and_builder_share_the_same_core_contract():
    main = ROOT / "skills/get-things-done/references/core-contract.md"
    builder = ROOT / "skills/building-gtd-domain-packs/references/core-contract.md"
    assert main.read_text(encoding="utf-8") == builder.read_text(encoding="utf-8")
