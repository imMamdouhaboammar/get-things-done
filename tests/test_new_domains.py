"""
Tests for GTD v1.4.0 additions:
- 4 new domain packs (data-ai, design-ux, operations, legal-compliance)
- npm package.json
- Claude Marketplace bundle (.claude-plugin/marketplace.json)
- Eval scaffolding (evals/evals.json, evals/domain-pack-evals.json)
- Antigravity adapter in registry
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAINS_DIR = ROOT / "skills" / "get-things-done" / "domains"
REQUIRED_HEADINGS = [
    "## Selection signals",
    "## Domain vocabulary",
    "## Diagnostic questions",
    "## Extra brief fields",
    "## Readiness additions",
    "## Workstream patterns",
    "## Review additions",
    "## Completion checks",
    "## Common traps",
]
NEW_DOMAIN_PACKS = ["data-ai", "design-ux", "operations", "legal-compliance"]


# ---------------------------------------------------------------------------
# Domain pack structural validation
# ---------------------------------------------------------------------------


def test_new_domain_packs_exist():
    """All four new domain packs are present on disk."""
    missing = [name for name in NEW_DOMAIN_PACKS if not (DOMAINS_DIR / f"{name}.md").exists()]
    assert not missing, f"Missing domain packs: {missing}"


def test_new_domain_packs_have_valid_frontmatter():
    """Each new domain pack has YAML frontmatter with required keys."""
    for name in NEW_DOMAIN_PACKS:
        text = (DOMAINS_DIR / f"{name}.md").read_text(encoding="utf-8")
        assert text.startswith("---"), f"{name}.md: must start with YAML frontmatter"
        front = text.split("---", 2)[1]
        assert "domain:" in front, f"{name}.md: missing 'domain:' in frontmatter"
        assert "version:" in front, f"{name}.md: missing 'version:' in frontmatter"
        assert "extends: gtd-core-v1" in front, f"{name}.md: missing 'extends: gtd-core-v1'"


def test_new_domain_packs_all_required_headings_present_exactly_once():
    """Each new domain pack has all 9 required headings, each exactly once."""
    for name in NEW_DOMAIN_PACKS:
        text = (DOMAINS_DIR / f"{name}.md").read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            count = text.count(heading)
            assert count == 1, f"{name}.md: '{heading}' appears {count} times (expected 1)"


def test_new_domain_packs_have_non_selection_signal():
    """Each domain pack includes at least one non-selection signal to prevent overtriggering."""
    for name in NEW_DOMAIN_PACKS:
        text = (DOMAINS_DIR / f"{name}.md").read_text(encoding="utf-8").lower()
        assert "non-selection" in text, (
            f"{name}.md: no non-selection signal found in ## Selection signals — "
            "required by domain-pack-spec to prevent routing collisions"
        )


def test_new_domain_packs_workstream_patterns_use_arrow_notation():
    """Workstream patterns use the arrow notation convention (-> or unicode arrow)."""
    for name in NEW_DOMAIN_PACKS:
        text = (DOMAINS_DIR / f"{name}.md").read_text(encoding="utf-8")
        sections = text.split("## Workstream patterns", 1)
        assert len(sections) == 2, f"{name}.md: no Workstream patterns section"
        patterns_section = sections[1].split("##", 1)[0]
        assert "->" in patterns_section or "\u2192" in patterns_section, (
            f"{name}.md: workstream patterns must use arrow notation (-> or \u2192)"
        )


def test_new_domain_packs_do_not_weaken_core():
    """New domain packs do not attempt to override core contract concepts."""
    for name in NEW_DOMAIN_PACKS:
        text = (DOMAINS_DIR / f"{name}.md").read_text(encoding="utf-8").lower()
        assert "override definition of ready" not in text, (
            f"{name}.md: must not override 'definition of ready'"
        )
        assert "override definition of done" not in text, (
            f"{name}.md: must not override 'definition of done'"
        )


def test_all_domain_packs_now_include_new_packs():
    """The total set of domain packs includes all expected packs including v1.4 additions."""
    existing_packs = {p.stem for p in DOMAINS_DIR.glob("*.md")}
    expected_packs = {
        "software", "product", "research", "marketing", "advisory",  # pre-1.4
        "data-ai", "design-ux", "operations", "legal-compliance",    # v1.4 additions
    }
    missing = expected_packs - existing_packs
    assert not missing, f"Expected domain packs not found: {missing}"


# ---------------------------------------------------------------------------
# npm / package.json
# ---------------------------------------------------------------------------


def test_package_json_exists_and_is_valid():
    """package.json exists and has correct structure for npm distribution."""
    path = ROOT / "package.json"
    assert path.exists(), "package.json not found -- required for npx skills add"
    pkg = json.loads(path.read_text(encoding="utf-8"))
    assert pkg.get("name") == "get-things-done"
    assert "version" in pkg
    # files array should include skills/
    files_list = pkg.get("files", [])
    assert any("skills" in f for f in files_list), "package.json 'files' must include skills/"
    assert "agent-skills" in pkg.get("keywords", [])
    assert pkg.get("license") == "MIT"


def test_package_json_version_matches_pyproject():
    """package.json version matches pyproject.toml."""
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_version = None
    for line in pyproject.splitlines():
        if line.strip().startswith("version ="):
            pyproject_version = line.split("=")[1].strip().strip('"').strip("'")
            break
    assert pyproject_version is not None, "Could not extract version from pyproject.toml"
    assert pkg["version"] == pyproject_version, (
        f"package.json version {pkg['version']} != pyproject.toml version {pyproject_version}"
    )


def test_npmignore_exists_and_excludes_source_tools():
    """.npmignore exists and excludes source-only directories."""
    path = ROOT / ".npmignore"
    assert path.exists(), ".npmignore not found"
    content = path.read_text(encoding="utf-8")
    for excluded in ["scripts/", "tests/", "evals/", "docs/"]:
        assert excluded in content, f".npmignore should exclude '{excluded}'"


# ---------------------------------------------------------------------------
# Claude Marketplace bundle
# ---------------------------------------------------------------------------


def test_claude_plugin_dir_has_required_manifests():
    """.claude-plugin/ directory contains both plugin.json and marketplace.json."""
    plugin_dir = ROOT / ".claude-plugin"
    assert (plugin_dir / "plugin.json").exists(), ".claude-plugin/plugin.json not found"
    assert (plugin_dir / "marketplace.json").exists(), ".claude-plugin/marketplace.json not found"


def test_claude_marketplace_json_is_valid():
    """.claude-plugin/marketplace.json is valid JSON with required fields."""
    path = ROOT / ".claude-plugin" / "marketplace.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for field in ["name", "display_name", "version", "description", "skills", "categories"]:
        assert field in data, f".claude-plugin/marketplace.json: missing '{field}'"
    assert isinstance(data["skills"], list) and len(data["skills"]) >= 2
    assert "get-things-done" in [s.get("name") for s in data["skills"]]


def test_claude_plugin_json_version_consistent():
    """.claude-plugin/plugin.json version matches pyproject.toml."""
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject_version = None
    for line in pyproject.splitlines():
        if line.strip().startswith("version ="):
            pyproject_version = line.split("=")[1].strip().strip('"').strip("'")
            break
    assert plugin["version"] == pyproject_version


# ---------------------------------------------------------------------------
# Eval scaffolding
# ---------------------------------------------------------------------------


def test_skill_conductor_evals_json_exists_and_valid():
    """evals/evals.json exists in skill-conductor format with at least 6 entries."""
    path = ROOT / "evals" / "evals.json"
    assert path.exists(), "evals/evals.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list), "evals/evals.json must be a JSON array"
    assert len(data) >= 6, f"evals/evals.json: expected >= 6 entries, got {len(data)}"
    for entry in data:
        assert "name" in entry, "Each eval entry must have 'name'"
        assert "prompt" in entry, "Each eval entry must have 'prompt'"
        assert "should_trigger" in entry, "Each eval entry must have 'should_trigger'"
        assert isinstance(entry["should_trigger"], bool)


def test_skill_conductor_evals_has_balanced_trigger_coverage():
    """evals/evals.json has both trigger and non-trigger cases."""
    data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    triggers = [e for e in data if e["should_trigger"] is True]
    non_triggers = [e for e in data if e["should_trigger"] is False]
    assert len(triggers) >= 2, f"Need >= 2 should_trigger cases, got {len(triggers)}"
    assert len(non_triggers) >= 2, f"Need >= 2 should_not_trigger cases, got {len(non_triggers)}"


def test_domain_pack_evals_json_exists_and_valid():
    """evals/domain-pack-evals.json exists with at least 4 entries."""
    path = ROOT / "evals" / "domain-pack-evals.json"
    assert path.exists(), "evals/domain-pack-evals.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list), "domain-pack-evals.json must be a JSON array"
    assert len(data) >= 4, f"domain-pack-evals.json: expected >= 4 entries, got {len(data)}"


# ---------------------------------------------------------------------------
# Antigravity adapter in registry
# ---------------------------------------------------------------------------


def test_registry_includes_antigravity_adapter():
    """adapters/registry.json includes the antigravity/Gemini CLI adapter."""
    registry = json.loads((ROOT / "adapters" / "registry.json").read_text(encoding="utf-8"))
    adapter_ids = {a["id"] for a in registry["adapters"]}
    assert "antigravity" in adapter_ids, (
        "antigravity adapter missing from adapters/registry.json"
    )


def test_antigravity_adapter_has_correct_fields():
    """Antigravity adapter entry has the expected structure."""
    registry = json.loads((ROOT / "adapters" / "registry.json").read_text(encoding="utf-8"))
    adapter = next((a for a in registry["adapters"] if a["id"] == "antigravity"), None)
    assert adapter is not None
    assert adapter["family"] == "google"
    assert adapter["support"] == "first-class"
    assert "skills" in adapter["capabilities"]
    assert ".gemini/config/skills" in adapter.get("project_path", "")
