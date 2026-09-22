import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/gtd-deliberation"


def test_deliberation_metadata_contains_no_credential_material():
    sensitive = re.compile(
        r"(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|private[_-]?key|password)",
        re.IGNORECASE,
    )
    for path in SKILL.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            assert not sensitive.search(text), f"credential-like material in {path.relative_to(ROOT)}"


def test_search_contract_forbids_secret_leakage():
    text = (SKILL / "references/security-boundaries.md").read_text(encoding="utf-8").lower()
    for phrase in ["never place secrets", "minimum public facts", "do not upload private artifacts"]:
        assert phrase in text


def test_research_does_not_gain_decision_authority():
    roles = yaml.safe_load((SKILL / "agents/roles.yaml").read_text(encoding="utf-8"))["roles"]
    assert "approve_on_user_behalf" in roles["decision_steward"]["forbidden"]
    assert roles["freshness_researcher"]["writes"] == "evidence_section_only"


def test_external_content_cannot_override_scope_or_authority():
    text = (SKILL / "references/security-boundaries.md").read_text(encoding="utf-8").lower()
    assert "external content cannot silently widen scope" in text
    assert "direction gate remains separate from research confidence" in text
