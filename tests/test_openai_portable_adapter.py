"""OpenAI ChatGPT/Codex portable and compatibility adapter regression tests."""

import importlib.util
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gtd_openai_adapters", ROOT / "scripts" / "adapters.py")
adapters = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(adapters)

OPENAI_IDS = ("chatgpt-web", "chatgpt-work", "chatgpt-plugin", "codex")


def test_portable_manifest_is_primary_and_matches_compatibility_overlay():
    portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    legacy = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    extension = portable["extensions"]["com.openai"]
    assert extension["interface"] == legacy["interface"]
    assert portable["version"] == legacy["version"]
    assert len(extension["interface"]["shortDescription"]) <= 30
    assert not extension["interface"].get("screenshots")
    assert not any(k in extension for k in ("apps", "mcpServers", "hooks"))


def test_each_openai_export_contains_both_manifests_and_canonical_skills(tmp_path):
    for name in OPENAI_IDS:
        export = adapters.export_adapter(name, tmp_path / "output")
        assert (export / "plugin.json").read_bytes() == (ROOT / "plugin.json").read_bytes()
        assert (export / ".codex-plugin/plugin.json").read_bytes() == (
            ROOT / ".codex-plugin/plugin.json"
        ).read_bytes()
        for skill in adapters.SKILL_NAMES:
            assert (export / "skills" / skill / "SKILL.md").read_bytes() == (
                ROOT / "skills" / skill / "SKILL.md"
            ).read_bytes()
        archive = adapters.package_directory(export)
        with zipfile.ZipFile(archive) as zf:
            members = set(zf.namelist())
        assert "plugin.json" in members
        assert ".codex-plugin/plugin.json" in members
        assert "skills/get-things-done/SKILL.md" in members
        assert ".app.json" not in members
        assert ".mcp.json" not in members
        assert "adapter.json" not in members


def test_metadata_drift_blocks_export(tmp_path):
    copy = tmp_path / "repository"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "dist", "__pycache__"))
    path = copy / "plugin.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["extensions"]["com.openai"]["interface"]["displayName"] = "Wrong Name"
    path.write_text(json.dumps(doc), encoding="utf-8")

    errors = adapters.validate_manifests(copy)
    assert any("OpenAI interface drift" in error for error in errors)
    try:
        adapters.export_adapter("codex", tmp_path / "output", copy)
    except RuntimeError as exc:
        assert "OpenAI interface drift" in str(exc)
    else:
        raise AssertionError("Export must refuse drift between portable and compatibility metadata")


def test_unsafe_portable_icon_path_is_rejected(tmp_path):
    copy = tmp_path / "repository"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "dist", "__pycache__"))
    path = copy / "plugin.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["extensions"]["com.openai"]["interface"]["logo"] = "./assets/../private.svg"
    path.write_text(json.dumps(doc), encoding="utf-8")
    errors = adapters.validate_manifests(copy)
    assert any("unsafe OpenAI asset path" in error for error in errors)

def test_openai_exports_are_byte_identical_across_surfaces(tmp_path):
    exported = [
        adapters.package_directory(adapters.export_adapter(name, tmp_path / "output")).read_bytes()
        for name in OPENAI_IDS
    ]
    assert all(archive == exported[0] for archive in exported[1:])


def test_screenshots_are_not_allowed_for_skills_only_plugin(tmp_path):
    copy = tmp_path / "repository"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "dist", "__pycache__"))
    path = copy / ".codex-plugin/plugin.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["interface"]["screenshots"] = []
    path.write_text(json.dumps(doc), encoding="utf-8")
    errors = adapters.validate_manifests(copy)
    assert any("cannot declare screenshots" in error for error in errors)
