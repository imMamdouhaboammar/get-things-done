"""Verification tests for the REA skill package and bridge utility."""
from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "rea"


def test_rea_skill_files_exist():
    required = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "skill-spec.json",
        SKILL_DIR / "agents/openai.yaml",
        SKILL_DIR / "agents/roles.yaml",
        SKILL_DIR / "assets/small-logo.svg",
        SKILL_DIR / "assets/large-logo.svg",
        SKILL_DIR / "evals/evals.json",
        SKILL_DIR / "references/target-routing.md",
        SKILL_DIR / "references/cli-recipes.md",
        SKILL_DIR / "references/evidence-contract.md",
        SKILL_DIR / "references/host-notes.md",
        SKILL_DIR / "examples/electron-feature-reconstruction.md",
        SKILL_DIR / "examples/native-binary-evidence.md",
        SKILL_DIR / "scripts/rea_bridge.py",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    assert not missing, f"Missing REA files: {missing}"


def test_rea_skill_frontmatter_and_body_conform():
    skill_file = SKILL_DIR / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    parts = content.split("---\n", 2)
    assert len(parts) >= 3

    fm = yaml.safe_load(parts[1])
    assert isinstance(fm, dict)
    assert fm["name"] == "rea"
    assert isinstance(fm["description"], str)
    assert "Use when" in fm["description"]
    assert len(fm["description"]) >= 40

    body = parts[2]
    assert len(body.splitlines()) > 20
    assert "# " in body
    assert "## " in body
    assert "Evidence-First" in body


def test_rea_brand_assets_conform():
    small_logo = SKILL_DIR / "assets/small-logo.svg"
    large_logo = SKILL_DIR / "assets/large-logo.svg"

    for path, expected_size in [(small_logo, 128), (large_logo, 512)]:
        content = path.read_text(encoding="utf-8")
        assert "<svg" in content and "</svg>" in content
        tree = ET.fromstring(content)
        assert int(tree.attrib.get("width", 0)) == expected_size
        assert int(tree.attrib.get("height", 0)) == expected_size
        assert tree.attrib.get("viewBox") == "0 0 512 512"


def test_rea_agent_manifest_conforms():
    manifest_path = SKILL_DIR / "agents/openai.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert data.get("name") == "rea"
    assert data.get("display_name") == "REA Reverse Engineering"
    assert len(data.get("display_name", "")) <= 40
    assert len(data.get("short_description", "")) <= 80
    assert len(data.get("default_prompt", "")) <= 128
    assert "\n" not in data.get("default_prompt", "")
    assert data.get("brand_color", "").upper() == "#E11D48"

    interface = data.get("interface")
    assert isinstance(interface, dict)
    assert 25 <= len(interface["short_description"]) <= 64
    assert interface["default_prompt"].startswith("Use $rea")
    for key in ("icon_small", "icon_large"):
        val = interface[key]
        assert val.startswith("./assets/")
        assert (SKILL_DIR / val[2:]).is_file()

    assert data.get("policy") == {"allow_implicit_invocation": True}


def test_rea_roles_manifest_conforms():
    roles_path = SKILL_DIR / "agents/roles.yaml"
    data = yaml.safe_load(roles_path.read_text(encoding="utf-8"))
    assert "roles" in data
    assert "reverse_engineer" in data["roles"]
    role = data["roles"]["reverse_engineer"]
    assert role["writes"] == "conditional"
    assert "binary_inspection" in role["primary_surfaces"]


def test_rea_evals_and_spec_conform():
    spec = json.loads((SKILL_DIR / "skill-spec.json").read_text(encoding="utf-8"))
    assert spec["name"] == "rea"
    assert "triggers" in spec
    assert "/rea" in spec["triggers"]["positive"]

    evals = json.loads((SKILL_DIR / "evals/evals.json").read_text(encoding="utf-8"))
    assert isinstance(evals, list) and len(evals) >= 3
    for case in evals:
        assert "name" in case
        assert "query" in case
        assert "should_trigger" in case
        assert isinstance(case["expected"], list)


def test_rea_bridge_doctor_runs_cleanly():
    bridge_script = SKILL_DIR / "scripts/rea_bridge.py"
    res = subprocess.run([sys.executable, str(bridge_script), "doctor"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "REA Tool & Engine Status:" in res.stdout


def test_rea_bridge_evidence_validation(tmp_path):
    bridge_script = SKILL_DIR / "scripts/rea_bridge.py"

    # Valid evidence
    valid_evidence = {
        "target": "app.asar",
        "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "locations": ["index.js:L10"],
        "symbols": ["verifySignature"]
    }
    valid_file = tmp_path / "valid.json"
    valid_file.write_text(json.dumps(valid_evidence))

    res = subprocess.run([sys.executable, str(bridge_script), "validate-evidence", str(valid_file)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "VALID" in res.stdout

    # Invalid evidence (missing locations)
    invalid_evidence = {
        "target": "app.asar",
        "digest": "not-a-valid-sha256",
        "locations": []
    }
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text(json.dumps(invalid_evidence))

    res = subprocess.run([sys.executable, str(bridge_script), "validate-evidence", str(invalid_file)], capture_output=True, text=True)
    assert res.returncode == 1
    assert "INVALID" in res.stdout
