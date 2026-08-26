from pathlib import Path
import xml.etree.ElementTree as ET
import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


@pytest.mark.parametrize("skill_name,expected_color,expected_display", [
    ("get-things-done", "#2563EB", "Get Things Done"),
    ("building-gtd-domain-packs", "#059669", "GTD Domain Pack Builder"),
])
def test_skill_brand_assets_and_manifests_exist_and_conform(skill_name, expected_color, expected_display):
    skill_dir = SKILLS_DIR / skill_name
    assert skill_dir.is_dir(), f"Skill directory {skill_dir} missing"

    small_logo = skill_dir / "assets" / "small-logo.svg"
    large_logo = skill_dir / "assets" / "large-logo.svg"
    manifest = skill_dir / "agents" / "openai.yaml"
    skill_md = skill_dir / "SKILL.md"

    assert small_logo.exists(), f"small-logo.svg missing for {skill_name}"
    assert large_logo.exists(), f"large-logo.svg missing for {skill_name}"
    assert manifest.exists(), f"agents/openai.yaml missing for {skill_name}"
    assert skill_md.exists(), f"SKILL.md missing for {skill_name}"

    # Verify SVG geometries
    for svg_path, size in [(small_logo, 128), (large_logo, 512)]:
        content = svg_path.read_text(encoding="utf-8")
        assert "<svg" in content and "</svg>" in content
        tree = ET.fromstring(content)
        assert int(tree.attrib.get("width", 0)) == size
        assert int(tree.attrib.get("height", 0)) == size
        assert tree.attrib.get("viewBox") == "0 0 512 512"

    # Verify openai.yaml compliance
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data.get("name") == skill_name
    assert data.get("display_name") == expected_display
    assert len(data.get("display_name", "")) <= 40
    assert len(data.get("short_description", "")) <= 80
    prompt = data.get("default_prompt", "")
    assert len(prompt) <= 128
    assert "\n" not in prompt
    assert data.get("brand_color", "").upper() == expected_color.upper()

    # Verify SKILL.md frontmatter
    skill_text = skill_md.read_text(encoding="utf-8")
    assert skill_text.startswith("---\n")
    parts = skill_text.split("---", 2)
    fm = yaml.safe_load(parts[1])
    assert fm.get("name") == skill_name
    assert fm.get("description", "").startswith("Use when")
