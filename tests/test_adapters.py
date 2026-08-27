import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "adapters.py"
spec = importlib.util.spec_from_file_location("gtd_adapters", MODULE_PATH)
adapters = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(adapters)


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for rel in ["adapters", ".codex-plugin", ".claude-plugin", "skills/get-things-done/assets", "skills/building-gtd-domain-packs"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "adapters/registry.json").write_text((Path(__file__).resolve().parents[1] / "adapters/registry.json").read_text())
    for name in adapters.SKILL_NAMES:
        p = root / "skills" / name / "SKILL.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"---\nname: {name}\ndescription: test\n---\nbody\n")
    for name in ["small-logo.svg", "large-logo.svg"]:
        (root / "skills/get-things-done/assets" / name).write_text("<svg></svg>")
    for rel in ["plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "kimi.plugin.json", "skills.sh.json"]:
        src = Path(__file__).resolve().parents[1] / rel
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text())
    return root


def test_registry_covers_requested_hosts():
    ids = set(adapters.adapters_by_id().keys())
    expected = {"claude-ai", "claude-code", "claude-marketplace", "claude-cowork", "chatgpt-web", "chatgpt-work", "chatgpt-plugin", "codex", "cursor", "kimi", "grok", "deepseek", "skills-sh", "skill-kit", "glama", "agent-skills", "agent-plugins"}
    assert expected <= ids


def test_repository_contracts_validate():
    assert adapters.validate() == []


def test_cursor_export_uses_native_project_path(tmp_path):
    root = make_repo(tmp_path)
    target = adapters.export_adapter("cursor", tmp_path / "dist", root)
    assert (target / ".cursor/skills/get-things-done/SKILL.md").is_file()
    assert (target / ".cursor/skills/building-gtd-domain-packs/SKILL.md").is_file()


def test_kimi_export_contains_native_plugin(tmp_path):
    root = make_repo(tmp_path)
    target = adapters.export_adapter("kimi", tmp_path / "dist", root)
    manifest = json.loads((target / "kimi.plugin.json").read_text())
    assert manifest["skills"] == "./skills/"
    assert (target / "skills/get-things-done/SKILL.md").is_file()


def test_openai_family_exports_same_canonical_skills(tmp_path):
    root = make_repo(tmp_path)
    for adapter_id in ("chatgpt-web", "chatgpt-work", "chatgpt-plugin", "codex"):
        target = adapters.export_adapter(adapter_id, tmp_path / "dist", root)
        assert (target / ".codex-plugin/plugin.json").is_file()
        assert (target / "skills/get-things-done/SKILL.md").is_file()


def test_claude_marketplace_export_contains_marketplace(tmp_path):
    root = make_repo(tmp_path)
    target = adapters.export_adapter("claude-marketplace", tmp_path / "dist", root)
    assert (target / ".claude-plugin/plugin.json").is_file()
    assert (target / ".claude-plugin/marketplace.json").is_file()


def test_deepseek_and_grok_use_documented_native_paths(tmp_path):
    root = make_repo(tmp_path)
    deep = adapters.export_adapter("deepseek", tmp_path / "dist", root)
    grok = adapters.export_adapter("grok", tmp_path / "dist", root)
    assert (deep / ".deepcode/skills/get-things-done/SKILL.md").is_file()
    assert (grok / ".grok/skills/get-things-done/SKILL.md").is_file()


def test_glama_fails_closed_without_mcp(tmp_path):
    root = make_repo(tmp_path)
    try:
        adapters.export_adapter("glama", tmp_path / "dist", root)
    except RuntimeError as exc:
        assert "refusing to generate fake support" in str(exc)
    else:
        raise AssertionError("Glama must be conditional until an MCP package exists")


def test_skill_kit_is_authoring_bridge_not_fake_runtime(tmp_path):
    root = make_repo(tmp_path)
    target = adapters.export_adapter("skill-kit", tmp_path / "dist", root)
    text = (target / "README.md").read_text()
    assert adapters.adapters_by_id(root)["skill-kit"]["support"] == "authoring-bridge"
    assert "typed workflow" in text
