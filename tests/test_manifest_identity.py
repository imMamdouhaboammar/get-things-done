import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/imMamdouhaboammar/get-things-done"
STALE_REPO = "get-things-done-skillpack"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_openai_manifest_points_to_current_repository():
    manifest = load(".codex-plugin/plugin.json")
    assert manifest["homepage"] == REPO_URL
    assert manifest["repository"] == REPO_URL
    assert manifest["interface"]["websiteURL"] == REPO_URL


def test_claude_plugin_points_to_current_repository():
    manifest = load(".claude-plugin/plugin.json")
    assert manifest["homepage"] == REPO_URL
    assert manifest["repository"] == REPO_URL


def test_claude_marketplace_points_to_current_repository():
    manifest = load(".claude-plugin/marketplace.json")
    assert manifest["plugins"][0]["homepage"] == REPO_URL


def test_kimi_manifest_points_to_current_repository():
    manifest = load("kimi.plugin.json")
    assert manifest["homepage"] == REPO_URL
    assert manifest["interface"]["websiteURL"] == REPO_URL


def test_distribution_manifests_do_not_reference_retired_repository_name():
    for path in [
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        "kimi.plugin.json",
    ]:
        assert STALE_REPO not in (ROOT / path).read_text(encoding="utf-8")
