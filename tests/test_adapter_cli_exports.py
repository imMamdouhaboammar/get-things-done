import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "adapters.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_single_export_package_returns_archive_path(tmp_path):
    out = tmp_path / "dist"
    result = run("export", "shell", "--out", str(out), "--package")
    assert result.returncode == 0, result.stderr
    archive = Path(result.stdout.strip())
    assert archive == out / "shell.zip"
    assert archive.is_file()


def test_unknown_export_returns_usage_error_without_output(tmp_path):
    out = tmp_path / "dist"
    result = run("export", "not-a-host", "--out", str(out))
    assert result.returncode == 2
    assert "unknown adapter" in result.stderr
    assert not out.exists()


def test_glama_export_returns_conditional_exit_code_without_fake_bundle(tmp_path):
    out = tmp_path / "dist"
    result = run("export", "glama", "--out", str(out))
    assert result.returncode == 3
    assert "CONDITIONAL" in result.stderr
    assert "refusing to generate fake support" in result.stderr
    assert not (out / "glama").exists()


def test_packaged_openai_export_contains_manifest_and_skill(tmp_path):
    out = tmp_path / "dist"
    result = run("export", "chatgpt-plugin", "--out", str(out), "--package")
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(out / "chatgpt-plugin.zip") as zf:
        names = set(zf.namelist())
    assert ".codex-plugin/plugin.json" in names
    assert "skills/get-things-done/SKILL.md" in names
