from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIRS = [
    ROOT / "skills" / "get-things-done",
    ROOT / "skills" / "building-gtd-domain-packs",
]


@pytest.mark.parametrize("skill_dir", SKILL_DIRS)
def test_skill_md_frontmatter_is_valid_yaml_and_conforms(skill_dir: Path):
    skill_file = skill_dir / "SKILL.md"
    assert skill_file.is_file()
    content = skill_file.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    parts = content.split("---\n", 2)
    assert len(parts) >= 3
    frontmatter_raw = parts[1]
    data = yaml.safe_load(frontmatter_raw)
    assert isinstance(data, dict)
    assert data["name"] == skill_dir.name
    assert isinstance(data.get("description"), str)
    assert data["description"].startswith("Use when")
    assert len(data["description"]) >= 40


@pytest.mark.parametrize("skill_dir", SKILL_DIRS)
def test_skill_md_body_contains_sections_and_guidance(skill_dir: Path):
    skill_file = skill_dir / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    parts = content.split("---\n", 2)
    body = parts[2]
    assert len(body.splitlines()) > 20
    assert "# " in body
    assert "## " in body
