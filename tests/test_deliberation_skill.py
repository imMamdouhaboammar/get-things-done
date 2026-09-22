import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/gtd-deliberation"
CLI = SKILL / "scripts/deliberation.py"


def test_deliberation_skill_is_self_contained():
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "agents/roles.yaml",
        "assets/small-logo.svg",
        "assets/large-logo.svg",
        "scripts/deliberation.py",
        "references/activation-router.yaml",
        "references/freshness-search.md",
        "references/deliberation-contract.md",
        "references/truth-contract.md",
        "references/problem-model.schema.json",
        "references/backlog.schema.json",
        "references/superpowers-handoff.md",
    ]
    missing = [path for path in required if not (SKILL / path).is_file()]
    assert not missing, missing


def test_activation_router_requires_runtime_freshness_when_active():
    data = yaml.safe_load((SKILL / "references/activation-router.yaml").read_text())
    assert data["freshness"]["required_when_deliberation_activates"] is True
    assert data["freshness"]["resolve_date_at_runtime"] is True
    assert data["freshness"]["search_must_use_current_date_scope"] is True
    assert data["freshness"]["remembered_knowledge_is_not_current_evidence"] is True


def test_problem_model_requires_freshness_context_and_direction_gate():
    schema = json.loads((SKILL / "references/problem-model.schema.json").read_text())
    required = set(schema["required"])
    assert "freshness_context" in required
    assert "direction_gate" in required
    freshness_required = set(schema["properties"]["freshness_context"]["required"])
    for field in ["searched_at", "queries", "sources", "freshness_findings", "stale_or_changed_claims", "freshness_gaps"]:
        assert field in freshness_required


def test_logical_roles_separate_truth_research_decision_and_backlog():
    roles = yaml.safe_load((SKILL / "agents/roles.yaml").read_text())["roles"]
    for role in ["contemplator", "freshness_researcher", "skeptic", "reframer", "ideator", "critic", "synthesizer", "decision_steward", "backlog_architect"]:
        assert role in roles
    assert "approve_on_user_behalf" in roles["decision_steward"]["forbidden"]
    assert "claim_current_evidence_from_memory" in roles["contemplator"]["forbidden"]


def test_eval_corpus_covers_freshness_truth_approval_and_sufficiency():
    cases = [json.loads(line) for line in (ROOT / "evals/gtd-deliberation-cases.jsonl").read_text().splitlines() if line.strip()]
    assert len(cases) >= 16
    joined = json.dumps(cases).lower()
    for phrase in ["today's date", "flatter", "direction approval", "stop further contemplation", "freshness blocked", "private chain-of-thought"]:
        assert phrase in joined


def test_cli_scaffolds_and_validates_problem_model(tmp_path):
    out = tmp_path / "problem.json"
    result = subprocess.run([
        sys.executable, str(CLI), "new-problem-model",
        "--title", "Engagement diagnosis",
        "--request", "Add AI because engagement is low",
        "--proposed-solution", "Add AI assistant",
        "--out", str(out),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(out.read_text())
    assert payload["freshness_context"]["status"] == "blocked"
    assert payload["direction_gate"]["status"] == "pending"

    result = subprocess.run([sys.executable, str(CLI), "validate-problem-model", str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_scaffolds_and_validates_backlog(tmp_path):
    out = tmp_path / "backlog.json"
    result = subprocess.run([
        sys.executable, str(CLI), "new-backlog",
        "--title", "Approved direction",
        "--direction", "Run activation experiment",
        "--problem-model", "problem.json",
        "--next-action", "Create experiment brief",
        "--out", str(out),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    result = subprocess.run([sys.executable, str(CLI), "validate-backlog", str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
