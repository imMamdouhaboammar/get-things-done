from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "gtd-capability-router"


def test_router_metadata_contains_no_credential_material():
    sensitive = re.compile(
        r"(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|password)",
        re.IGNORECASE,
    )
    for path in SKILL.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            assert not sensitive.search(text), f"credential-like material in {path.relative_to(ROOT)}"


def test_unknown_or_unavailable_capabilities_never_gain_implicit_write_authority():
    router = yaml.safe_load((SKILL / "references/router.yaml").read_text(encoding="utf-8"))
    policy = router["availability_policy"]
    assert policy["runtime_requirement"] == "discover_current_availability_before_selection"
    assert policy["unresolved_name"] == "do_not_invent_capability"
    assert "evidence_gap" in policy["blocked_nominal_owner"]


def test_review_and_landing_authority_stay_separate():
    roles = yaml.safe_load((SKILL / "agents/roles.yaml").read_text(encoding="utf-8"))["roles"]
    assert roles["reviewer"]["writes"] == "false_by_default"
    assert roles["landing_steward"]["writes"] == "landing_state_only"
    assert "silent_gate_bypass" in roles["landing_steward"]["forbidden"]


def test_exactly_one_role_has_unqualified_true_write_authority():
    roles = yaml.safe_load((SKILL / "agents/roles.yaml").read_text(encoding="utf-8"))["roles"]
    true_writers = [name for name, role in roles.items() if role.get("writes") is True]
    assert true_writers == ["executor"]


def test_security_boundary_forbids_secret_storage_and_silent_bypass():
    text = (SKILL / "references/security-boundaries.md").read_text(encoding="utf-8").lower()
    assert "secrets" in text
    assert "silent admin" in text
    assert "fail-closed" in text
