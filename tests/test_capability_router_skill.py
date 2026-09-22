import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "gtd-capability-router"


def test_capability_router_is_self_contained():
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "agents/roles.yaml",
        "assets/small-logo.svg",
        "assets/large-logo.svg",
        "references/core-contract.md",
        "references/router.yaml",
        "references/capability-registry.yaml",
        "references/repository-playbook.md",
        "references/plugin-skill-playbook.md",
        "references/source-lineage.md",
    ]
    missing = [path for path in required if not (SKILL / path).is_file()]
    assert not missing, f"missing: {missing}"


def test_router_frontmatter_is_discoverable():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---\n", 2)[1])
    assert frontmatter["name"] == "gtd-capability-router"
    assert frontmatter["description"].startswith("Use when")
    assert "smallest safe stack" in frontmatter["description"]


def test_router_contract_preserves_core_ownership_rules():
    data = yaml.safe_load((SKILL / "references/router.yaml").read_text(encoding="utf-8"))
    assert data["extends"] == "gtd-core-v1"
    principles = set(data["principles"])
    required = {
        "one_primary_owner",
        "one_write_owner_per_mutable_surface",
        "executable_verification_before_readiness_claim",
        "one_landing_owner",
        "refresh_after_mutation",
        "tool_honesty",
    }
    assert required <= principles
    assert data["availability_policy"]["runtime_requirement"] == "discover_current_availability_before_selection"


def test_capability_registry_never_freezes_runtime_availability():
    data = yaml.safe_load((SKILL / "references/capability-registry.yaml").read_text(encoding="utf-8"))
    capabilities = data["capabilities"]
    assert len(capabilities) >= 15
    for name, capability in capabilities.items():
        assert capability["availability"] == "discover_at_runtime", name
        assert capability["surface"], name
        assert capability["roles"], name


def test_logical_agent_roles_separate_execution_review_and_landing():
    data = yaml.safe_load((SKILL / "agents/roles.yaml").read_text(encoding="utf-8"))
    roles = data["roles"]
    for role in ["router", "source_scout", "executor", "verifier", "reviewer", "landing_steward"]:
        assert role in roles
    assert roles["executor"]["writes"] is True
    assert roles["reviewer"]["writes"] == "false_by_default"
    assert "reuse_stale_head_approval" in roles["landing_steward"]["forbidden"]


def test_router_eval_corpus_covers_high_risk_regressions():
    path = ROOT / "evals" / "gtd-capability-router-cases.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(cases) >= 15
    assert len({case["id"] for case in cases}) == len(cases)
    joined = json.dumps(cases).lower()
    for phrase in [
        "live repository state",
        "one write owner",
        "executable proof",
        "current head",
        "stale exact-head",
        "marketplace approval",
    ]:
        assert phrase in joined


def test_source_lineage_names_migration_sources_and_current_specs():
    text = (SKILL / "references/source-lineage.md").read_text(encoding="utf-8")
    for source in [
        "Use-ChatGPT.md",
        "Use-ChatGPT/capabilities.yaml",
        "Use-ChatGPT/routing-evals.yaml",
        "https://agentskills.io/specification",
        "https://agent-plugins.org/specification",
    ]:
        assert source in text


def test_router_and_core_share_exact_core_contract():
    canonical = ROOT / "skills/get-things-done/references/core-contract.md"
    copied = SKILL / "references/core-contract.md"
    assert copied.read_text(encoding="utf-8") == canonical.read_text(encoding="utf-8")
