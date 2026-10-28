import xml.etree.ElementTree as ET
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "improve"


def test_improve_skill_directory_is_self_contained():
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "agents/antigravity.md",
        "agents/claude.md",
        "agents/cursor.md",
        "agents/openai.md",
        "assets/small-logo.svg",
        "assets/large-logo.svg",
        "references/audit-playbook.md",
        "references/closing-the-loop.md",
        "references/plan-template.md",
        "references/core-contract.md",
        "references/gtd-plan-bridge.md",
        "scripts/improve_bridge.py",
        "scripts/validate_skill.sh",
        "templates/plan-template.md",
        "templates/plan-index-template.md",
        "templates/finding.schema.json",
        "templates/plan.schema.json",
        "evals/eval-suite.yaml",
        "examples/001-extract-shadow-config-resolution.md",
        "examples/002-gtd-brief-conversion-example.md",
    ]
    missing = [path for path in required if not (SKILL / path).is_file()]
    assert not missing, f"missing improve files: {missing}"


def test_improve_skill_frontmatter_conforms():
    skill_file = SKILL / "SKILL.md"
    assert skill_file.is_file()
    text = skill_file.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    parts = text.split("---\n", 2)
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])
    assert fm["name"] == "improve"
    assert fm["description"].startswith("Use when")
    assert len(fm["description"]) >= 40
    assert "senior advisor" in fm["description"].lower()


def test_improve_core_contract_invariants():
    contract = (SKILL / "references" / "core-contract.md").read_text(encoding="utf-8").lower()
    assert "strictly read-only" in contract
    assert "plans/" in contract
    assert "weakest plausible executor" in contract
    assert "machine-checkable verification" in contract
    assert "secret fencing" in contract
    assert "prompt-injection" in contract


def test_improve_brand_assets_and_manifest():
    small_logo = SKILL / "assets" / "small-logo.svg"
    large_logo = SKILL / "assets" / "large-logo.svg"
    manifest = SKILL / "agents" / "openai.yaml"

    assert small_logo.is_file()
    assert large_logo.is_file()
    assert manifest.is_file()

    for svg_path, size in [(small_logo, 128), (large_logo, 512)]:
        content = svg_path.read_text(encoding="utf-8")
        assert "<svg" in content and "</svg>" in content
        tree = ET.fromstring(content)
        assert int(tree.attrib.get("width", 0)) == size
        assert int(tree.attrib.get("height", 0)) == size
        assert tree.attrib.get("viewBox") == "0 0 512 512"

    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    assert data["name"] == "improve"
    assert data["display_name"] == "Codebase Improve Advisor"
    assert len(data["display_name"]) <= 40
    assert len(data["short_description"]) <= 80
    assert len(data["default_prompt"]) <= 128
    assert "\n" not in data["default_prompt"]
    assert data["brand_color"].upper() == "#0EA5E9"

    interface = data["interface"]
    assert 25 <= len(interface["short_description"]) <= 64
    assert interface["default_prompt"].startswith("Use $improve")
    assert interface["icon_small"] == "./assets/small-logo.svg"
    assert interface["icon_large"] == "./assets/large-logo.svg"
    assert data["policy"] == {"allow_implicit_invocation": True}
