import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_keeps_product_story_before_reference_material():
    text = readme_text()
    ordered = [
        "## Start with the request you actually have",
        "## Install",
        "## What changes when GTD is in the loop",
        "## How GTD works",
        "## Two kinds of proof",
        "## Agent behavior is a testable claim",
        "## Four Skills, one execution contract",
        "## Architecture",
        "## Documentation",
    ]
    positions = [text.index(section) for section in ordered]
    assert positions == sorted(positions)
    assert "## Table of contents" not in text
    assert len(text.splitlines()) <= 450


def test_readme_visual_assets_exist_and_have_alt_text():
    text = readme_text()
    tags = re.findall(r"<img\b[^>]*>", text)
    local_tags = [tag for tag in tags if "docs/assets/readme/" in tag]
    assert len(local_tags) == 2

    for tag in local_tags:
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]+)"', tag)
        assert src is not None
        assert alt is not None and alt.group(1).strip()
        assert (ROOT / src.group(1)).is_file()


def test_readme_badges_are_compact_dynamic_and_not_release_fiction():
    text = readme_text()
    shields = re.findall(r"https://img\.shields\.io/[^)\"\s]+", text)
    assert len(shields) == 4
    assert all("style=flat-square" in badge for badge in shields)
    assert "version-1.4.0" not in text
    assert "github/v/release" not in text


def test_readme_adapter_count_tracks_registry():
    registry = json.loads((ROOT / "adapters/registry.json").read_text(encoding="utf-8"))
    count = len(registry["adapters"])
    text = readme_text()
    assert f"Current adapter contracts cover **{count} targets**" in text


def test_readme_domain_pack_table_tracks_built_in_domains():
    domain_files = sorted((ROOT / "skills/get-things-done/domains").glob("*.md"))
    assert len(domain_files) == 9
    text = readme_text()
    labels = {
        "software": "| Software |",
        "marketing": "| Marketing |",
        "product": "| Product |",
        "research": "| Research |",
        "advisory": "| Advisory |",
        "data-ai": "| Data & AI |",
        "design-ux": "| Design & UX |",
        "operations": "| Operations |",
        "legal-compliance": "| Legal & Compliance |",
    }
    assert {path.stem for path in domain_files} == set(labels)
    for label in labels.values():
        assert label in text


def test_readme_python_claim_tracks_ci_matrix():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    match = re.search(r'python-version:\s*\[([^\]]+)\]', workflow)
    assert match is not None
    versions = re.findall(r'"([0-9]+\.[0-9]+)"', match.group(1))
    assert versions

    text = readme_text()
    support_line = (
        "Current deterministic CI runs on Python **"
        + ", ".join(versions[:-1])
        + f", and {versions[-1]}**"
    )
    assert support_line in text
    assert f"Python-{versions[0]}--{versions[-1]}" in text


def test_readme_relative_links_resolve():
    text = readme_text()
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    for link in links:
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = link.split("#", 1)[0]
        if not path:
            continue
        assert (ROOT / path).exists(), link


def test_readme_avoids_known_marketing_slop_phrases():
    text = readme_text().lower()
    banned = [
        "game changer",
        "cutting-edge",
        "revolutionary",
        "next-generation",
        "world-class",
        "seamless experience",
        "supercharge",
        "unlock the power",
    ]
    for phrase in banned:
        assert phrase not in text
