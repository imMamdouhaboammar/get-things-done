import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install.sh"


def run_installer(tmp_path: Path, *args: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(INSTALLER), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_list_targets_reports_named_shell_hosts_without_installing(tmp_path):
    result = run_installer(tmp_path, "--list-targets")
    assert result.returncode == 0, result.stderr
    for target in ["agents", "codex", "claude", "cursor", "kimi", "grok", "deepseek"]:
        assert target in result.stdout
    assert not (tmp_path / "home").exists()


def test_dry_run_reports_destinations_without_writing(tmp_path):
    result = run_installer(tmp_path, "--target", "claude", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Would install get-things-done" in result.stdout
    assert ".claude/skills/get-things-done" in result.stdout
    assert not (tmp_path / "home").exists()


def test_target_flag_requires_a_value(tmp_path):
    result = run_installer(tmp_path, "--target")
    assert result.returncode == 2
    assert "--target requires a value" in result.stderr


def test_unknown_named_target_fails_without_writing(tmp_path):
    result = run_installer(tmp_path, "--target", "unknown-agent")
    assert result.returncode == 2
    assert "Unknown target: unknown-agent" in result.stderr
    assert not (tmp_path / "home").exists()


def test_kimi_home_override_controls_install_root(tmp_path):
    kimi_home = tmp_path / "kimi-home"
    result = run_installer(tmp_path, "--target", "kimi", env_overrides={"KIMI_CODE_HOME": str(kimi_home)})
    assert result.returncode == 0, result.stderr
    assert (kimi_home / "skills/get-things-done/SKILL.md").is_file()
    assert not (tmp_path / "home/.kimi-code").exists()


def test_default_install_uses_universal_agent_skills_root(tmp_path):
    result = run_installer(tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "home/.agents/skills/get-things-done/SKILL.md").is_file()
    assert (tmp_path / "home/.agents/skills/building-gtd-domain-packs/SKILL.md").is_file()


def test_custom_path_install_supports_any_agent_skill_root(tmp_path):
    custom = tmp_path / "custom-agent/skills"
    result = run_installer(tmp_path, "--target-path", str(custom))
    assert result.returncode == 0, result.stderr
    assert (custom / "get-things-done/SKILL.md").is_file()
    assert (custom / "building-gtd-domain-packs/SKILL.md").is_file()


def test_custom_path_with_spaces_is_supported(tmp_path):
    custom = tmp_path / "agent home/skill root"
    result = run_installer(tmp_path, "--target-path", str(custom))
    assert result.returncode == 0, result.stderr
    assert (custom / "get-things-done/SKILL.md").is_file()


def test_multiple_custom_paths_install_independently(tmp_path):
    first = tmp_path / "agent-a/skills"
    second = tmp_path / "agent-b/skills"
    result = run_installer(tmp_path, "--target-path", str(first), "--target-path", str(second))
    assert result.returncode == 0, result.stderr
    assert (first / "get-things-done/SKILL.md").is_file()
    assert (second / "get-things-done/SKILL.md").is_file()


def test_named_targets_sharing_a_root_are_deduplicated(tmp_path):
    result = run_installer(tmp_path, "--target", "agents", "--target", "codex")
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("Installed get-things-done ->") == 1
    assert result.stdout.count("Installed building-gtd-domain-packs ->") == 1


def test_installer_refuses_overwrite_without_force(tmp_path):
    first = run_installer(tmp_path)
    second = run_installer(tmp_path)
    assert first.returncode == 0
    assert second.returncode == 2
    assert "Use --force" in second.stderr


def test_force_replaces_existing_install(tmp_path):
    first = run_installer(tmp_path)
    marker = tmp_path / "home/.agents/skills/get-things-done/marker.txt"
    marker.write_text("old")
    second = run_installer(tmp_path, "--force")
    assert first.returncode == 0
    assert second.returncode == 0, second.stderr
    assert not marker.exists()


def test_all_installs_each_distinct_supported_skill_root(tmp_path):
    result = run_installer(tmp_path, "--all")
    assert result.returncode == 0, result.stderr
    expected = [
        tmp_path / "home/.agents/skills/get-things-done/SKILL.md",
        tmp_path / "home/.claude/skills/get-things-done/SKILL.md",
        tmp_path / "home/.cursor/skills/get-things-done/SKILL.md",
        tmp_path / "home/.kimi-code/skills/get-things-done/SKILL.md",
        tmp_path / "home/.grok/skills/get-things-done/SKILL.md",
    ]
    assert all(path.is_file() for path in expected)


def test_installer_both_flag_installs_agents_and_claude(tmp_path):
    result = run_installer(tmp_path, "--both")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "home/.agents/skills/get-things-done/SKILL.md").is_file()
    assert (tmp_path / "home/.claude/skills/get-things-done/SKILL.md").is_file()


def test_installer_claude_flag_installs_claude_skills(tmp_path):
    result = run_installer(tmp_path, "--claude")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "home/.claude/skills/get-things-done/SKILL.md").is_file()
    assert not (tmp_path / "home/.agents/skills").exists()


def test_installer_help_flag_displays_usage(tmp_path):
    for flag in ["-h", "--help"]:
        result = run_installer(tmp_path, flag)
        assert result.returncode == 0, result.stderr
        assert "Usage: ./install.sh" in result.stdout
        assert "--target-path" in result.stdout
        assert "--force" in result.stdout


def test_installer_empty_target_path_fails(tmp_path):
    result = run_installer(tmp_path, "--target-path", "")
    assert result.returncode == 2
    assert "cannot be empty" in result.stderr

