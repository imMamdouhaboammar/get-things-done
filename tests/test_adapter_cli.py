import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "adapters.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_list_exposes_homebrew_shell_and_universal_support():
    result = run("list")
    assert result.returncode == 0, result.stderr
    assert "agent-skills" in result.stdout
    assert "homebrew" in result.stdout
    assert "shell" in result.stdout


def test_info_emits_machine_readable_adapter_contract():
    result = run("info", "homebrew")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["id"] == "homebrew"
    assert payload["export"] == "homebrew-formula"


def test_unknown_adapter_info_returns_usage_error_code():
    result = run("info", "does-not-exist")
    assert result.returncode == 2
    assert "unknown adapter" in result.stderr


def test_companions_lists_requested_interop_tools():
    result = run("companions")
    assert result.returncode == 0, result.stderr
    for companion in ["plugin-autopilot", "plugin-eval", "superpowers", "armorcodex", "context7"]:
        assert companion in result.stdout


def test_interop_single_companion_is_json():
    result = run("interop", "context7")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["companion_role"] == "documentation-retrieval"


def test_unknown_companion_returns_usage_error_code():
    result = run("interop", "does-not-exist")
    assert result.returncode == 2
    assert "unknown companion" in result.stderr


def test_validate_reports_adapter_and_companion_counts():
    result = run("validate")
    assert result.returncode == 0, result.stderr
    assert "19 adapter contracts" in result.stdout
    assert "5 companion profiles" in result.stdout
