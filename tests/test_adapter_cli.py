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


def test_list_json_is_machine_readable():
    result = run("list", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 20
    assert any(item["id"] == "homebrew" for item in payload)
    assert any(item["id"] == "shell" for item in payload)
    assert any(item["id"] == "antigravity" for item in payload)


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


def test_companions_json_is_machine_readable():
    result = run("companions", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 5
    assert {item["id"] for item in payload} == {"plugin-autopilot", "plugin-eval", "superpowers", "armorcodex", "context7"}


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
    assert "20 adapter contracts" in result.stdout
    assert "5 companion profiles" in result.stdout


def test_export_all_package_builds_reproducible_archives(tmp_path):
    out = tmp_path / "adapters"
    result = run("export-all", "--out", str(out), "--package")
    assert result.returncode == 0, result.stderr
    assert (out / "homebrew.zip").is_file()
    assert (out / "shell.zip").is_file()
    assert (out / "codex.zip").is_file()
    assert not (out / "glama.zip").exists()


def test_status_command_reports_summary_and_breakdown():
    result = run("status")
    assert result.returncode == 0, result.stderr
    assert "Adapters: 20" in result.stdout
    assert "Companions: 5" in result.stdout
    assert "first-class" in result.stdout


def test_status_json_command_returns_structured_metrics():
    result = run("status", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["adapters_total"] == 20
    assert payload["companions_total"] == 5
    assert payload["support_counts"]["first-class"] >= 10
    assert payload["version"] == "1.4.0"


def test_capabilities_command_lists_all_capabilities():
    result = run("capabilities")
    assert result.returncode == 0, result.stderr
    assert "skills" in result.stdout
    assert "cli-install" in result.stdout


def test_capabilities_json_returns_machine_readable_mapping():
    result = run("capabilities", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "skills" in payload
    assert "homebrew" in payload["cli-install"]


def test_query_command_filters_adapters_by_capability():
    result = run("query", "--capability", "cli-install", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["id"] == "homebrew"


def test_query_command_filters_adapters_by_support():
    result = run("query", "--support", "conditional", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["id"] == "glama"


def test_export_all_writes_structured_report(tmp_path):
    out = tmp_path / "adapters"
    report_file = tmp_path / "report.json"
    result = run("export-all", "--out", str(out), "--package", "--report", str(report_file))
    assert result.returncode == 0, result.stderr
    assert report_file.is_file()
    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert payload["exported"] == 19
    assert payload["packaged"] == 19
    assert "glama" in payload["skipped_conditional"]
    assert len(payload["artifacts"]) == 19

