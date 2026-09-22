import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS_DIR = ROOT / "skills/get-things-done/domains"
ROUTING_CASES = ROOT / "evals/domain-routing-cases.jsonl"

EXPECTED_DOMAINS = {
    "software",
    "marketing",
    "product",
    "research",
    "advisory",
    "data-ai",
    "design-ux",
    "operations",
    "legal-compliance",
}


def read_cases():
    return [
        json.loads(line)
        for line in ROUTING_CASES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_all_nine_domain_packs_have_explicit_non_selection_signal():
    existing = {path.stem for path in DOMAINS_DIR.glob("*.md")}
    assert existing == EXPECTED_DOMAINS
    for domain in sorted(EXPECTED_DOMAINS):
        text = (DOMAINS_DIR / f"{domain}.md").read_text(encoding="utf-8").lower()
        selection = text.split("## selection signals", 1)[1].split("##", 1)[0]
        assert "non-selection" in selection, domain


def test_routing_corpus_has_selection_case_for_every_domain():
    cases = read_cases()
    selected = {
        case["metadata"]["expected_pack"]
        for case in cases
        if case["metadata"]["case_type"] == "selection"
    }
    assert selected == EXPECTED_DOMAINS


def test_routing_corpus_has_non_selection_evidence_for_every_domain():
    cases = read_cases()
    rejected = {
        domain
        for case in cases
        if case["metadata"]["case_type"] in {"non-selection", "wrong-pack"}
        for domain in case["metadata"]["forbidden_packs"]
    }
    assert EXPECTED_DOMAINS <= rejected


def test_zero_pack_path_forbids_every_specialist_pack():
    cases = read_cases()
    zero = [case for case in cases if case["metadata"]["case_type"] == "zero-pack"]
    assert len(zero) == 1
    assert zero[0]["metadata"]["expected_pack"] is None
    assert set(zero[0]["metadata"]["forbidden_packs"]) == EXPECTED_DOMAINS
    expected_ids = {item["id"] for item in zero[0]["expected"]}
    assert "select-core-only" in expected_ids
    assert "zero-or-one-pack" in expected_ids


def test_wrong_pack_path_is_explicit_and_falsifiable():
    cases = read_cases()
    wrong = [case for case in cases if case["metadata"]["case_type"] == "wrong-pack"]
    assert wrong
    assert any(
        case["metadata"]["expected_pack"] == "software"
        and "marketing" in case["metadata"]["forbidden_packs"]
        for case in wrong
    )


def test_every_routing_case_preserves_zero_or_one_pack_rule():
    for case in read_cases():
        expected_ids = {item["id"] for item in case["expected"]}
        forbidden_ids = {item["id"] for item in case["forbidden"]}
        assert "zero-or-one-pack" in expected_ids
        assert "select-multiple-packs" in forbidden_ids


def test_domain_packs_cannot_override_core_readiness_or_done_contracts():
    for path in DOMAINS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8").lower()
        assert "extends: gtd-core-v1" in text
        assert "override definition of ready" not in text
        assert "override definition of done" not in text


def test_domain_docs_describe_honest_capability_degradation_and_core_authority():
    text = (ROOT / "docs/domain-packs.md").read_text(encoding="utf-8").lower()
    assert "zero or one" in text
    assert "core remains authoritative" in text
    assert "do not simulate" in text
    assert "unavailable" in text


def test_root_planning_files_are_marked_as_historical_snapshots():
    for name in ["task_plan.md", "progress.md"]:
        text = (ROOT / name).read_text(encoding="utf-8").lower()
        assert "historical planning snapshot" in text
        assert "not the current implementation status" in text
