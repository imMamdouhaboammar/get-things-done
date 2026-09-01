import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "1.4.0"


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def get_pyproject_version() -> str:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.strip().startswith("version ="):
            return line.split("=")[1].strip().strip('"').strip("'")
    raise ValueError("version not found in pyproject.toml")


def test_manifest_versions_match_expected_release_candidate():
    assert get_pyproject_version() == EXPECTED_VERSION
    assert load_json("plugin.json")["version"] == EXPECTED_VERSION
    assert load_json(".claude-plugin/plugin.json")["version"] == EXPECTED_VERSION
    assert load_json(".codex-plugin/plugin.json")["version"] == EXPECTED_VERSION
    assert load_json("kimi.plugin.json")["version"] == EXPECTED_VERSION
    assert load_json("package.json")["version"] == EXPECTED_VERSION


def test_all_distribution_manifests_share_identical_version():
    versions = {
        "pyproject.toml": get_pyproject_version(),
        "plugin.json": load_json("plugin.json")["version"],
        ".claude-plugin/plugin.json": load_json(".claude-plugin/plugin.json")["version"],
        ".codex-plugin/plugin.json": load_json(".codex-plugin/plugin.json")["version"],
        "kimi.plugin.json": load_json("kimi.plugin.json")["version"],
        "package.json": load_json("package.json")["version"],
    }
    distinct = set(versions.values())
    assert len(distinct) == 1, f"Version mismatch detected: {versions}"
