import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "adapters.py"
spec = importlib.util.spec_from_file_location("gtd_adapter_validation", MODULE_PATH)
adapters = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(adapters)


def repo_copy(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in ["adapters", "skills/get-things-done", "skills/building-gtd-domain-packs", "skills/gtd-capability-router", "skills/gtd-deliberation", ".codex-plugin", ".claude-plugin", "Formula"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel in [
        "adapters/registry.json",
        "adapters/registry.schema.json",
        "adapters/companions.json",
        "skills/get-things-done/scripts/schema_validation.py",
        "plugin.json",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        "kimi.plugin.json",
        "skills.sh.json",
        "install.sh",
        "Formula/get-things-done.rb",
    ]:
        src = ROOT / rel
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    for skill in adapters.SKILL_NAMES:
        (root / "skills" / skill / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: test\n---\n")
    for logo in ["small-logo.svg", "large-logo.svg"]:
        path = root / "skills/get-things-done/assets" / logo
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<svg></svg>")
    return root


def mutate_registry(root: Path, adapter_id: str, key: str, value):
    path = root / "adapters/registry.json"
    data = json.loads(path.read_text())
    target = next(item for item in data["adapters"] if item["id"] == adapter_id)
    target[key] = value
    path.write_text(json.dumps(data))


def test_absolute_project_path_is_rejected(tmp_path):
    root = repo_copy(tmp_path)
    mutate_registry(root, "cursor", "project_path", "/tmp/skills")
    assert any("unsafe project_path" in error for error in adapters.validate_registry(root))


def test_parent_traversal_manifest_is_rejected(tmp_path):
    root = repo_copy(tmp_path)
    mutate_registry(root, "homebrew", "manifest", "../Formula/get-things-done.rb")
    assert any("unsafe manifest" in error for error in adapters.validate_registry(root))


def test_parent_traversal_conditional_requirement_is_rejected(tmp_path):
    root = repo_copy(tmp_path)
    mutate_registry(root, "glama", "requires", "../mcp.json")
    assert any("unsafe requires" in error for error in adapters.validate_registry(root))


def test_duplicate_capabilities_are_rejected(tmp_path):
    root = repo_copy(tmp_path)
    mutate_registry(root, "shell", "capabilities", ["skills", "skills"])
    assert any("duplicate capabilities" in error for error in adapters.validate_registry(root))


def test_retired_repository_url_in_manifests_is_rejected(tmp_path):
    root = repo_copy(tmp_path)
    path = root / ".codex-plugin/plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["homepage"] = "https://github.com/imMamdouhaboammar/get-things-done-skillpack"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = adapters.validate_manifests(root)
    assert any("retired repository identity" in error or "stale repository" in error for error in errors)


def test_mismatched_manifest_versions_are_rejected(tmp_path):
    root = repo_copy(tmp_path)
    path = root / "kimi.plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "9.9.9"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = adapters.validate_manifests(root)
    assert any("version mismatch" in error for error in errors)


def test_invalid_semver_in_manifest_is_rejected(tmp_path):
    root = repo_copy(tmp_path)
    path = root / "plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "invalid-version"
    path.write_text(json.dumps(data), encoding="utf-8")
    errors = adapters.validate_manifests(root)
    assert any("invalid semver" in error for error in errors)



def test_antigravity_is_part_of_required_adapter_contract(tmp_path):
    root = repo_copy(tmp_path)
    path = root / "adapters/registry.json"
    data = json.loads(path.read_text())
    data["adapters"] = [item for item in data["adapters"] if item["id"] != "antigravity"]
    path.write_text(json.dumps(data))
    errors = adapters.validate_registry(root)
    assert any("missing required adapters: antigravity" in error for error in errors)


def test_registry_schema_rejects_undeclared_adapter_property(tmp_path):
    root = repo_copy(tmp_path)
    mutate_registry(root, "cursor", "invented_property", True)
    errors = adapters.validate_registry(root)
    assert any("additional property is not allowed" in error and "invented_property" in error for error in errors)


def test_normal_export_refuses_invalid_manifest_contract(tmp_path):
    root = repo_copy(tmp_path)
    path = root / "kimi.plugin.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "9.9.9"
    path.write_text(json.dumps(data), encoding="utf-8")

    try:
        adapters.export_adapter("cursor", tmp_path / "dist", root)
    except RuntimeError as exc:
        assert "invalid adapter distribution contract" in str(exc)
        assert "version mismatch" in str(exc)
    else:
        raise AssertionError("export must fail when repository manifests are invalid")


def test_required_adapter_ids_exactly_match_shipped_registry():
    ids = {item["id"] for item in adapters.load_registry()["adapters"]}
    assert ids == adapters.REQUIRED_ADAPTER_IDS
