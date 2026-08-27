from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = (ROOT / "docs" / "installation.md").read_text(encoding="utf-8")


def test_installation_guide_covers_named_runtime_hosts():
    for label in [
        "Claude AI Skills",
        "Claude Code",
        "Claude Cowork",
        "ChatGPT Web",
        "ChatGPT Work",
        "ChatGPT Plugins",
        "Codex",
        "Cursor",
        "Kimi Code",
        "Grok",
        "DeepSeek",
        "Homebrew",
        "skills.sh",
        "Skill Kit",
        "Glama",
    ]:
        assert label in GUIDE


def test_installation_guide_covers_requested_companions():
    for label in ["Plugin Autopilot", "Plugin Eval", "Superpowers", "ArmorCodex", "Context7"]:
        assert label in GUIDE


def test_installation_guide_documents_universal_custom_path():
    assert "--target-path" in GUIDE
    assert "Agent Skills" in GUIDE


def test_installation_guide_preserves_glama_boundary():
    assert "conditional" in GUIDE.lower()
    assert "mcp.json" in GUIDE
    assert "fails closed" in GUIDE


def test_installation_guide_preserves_homebrew_head_boundary():
    assert "HEAD-only" in GUIDE
    assert "brew install --HEAD" in GUIDE
