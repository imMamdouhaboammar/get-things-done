from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_workflow(name: str) -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"))


def step_run_commands(workflow: dict, job: str) -> str:
    steps = workflow["jobs"][job]["steps"]
    return "\n".join(str(step.get("run", "")) for step in steps)


def test_ci_validates_adapter_and_companion_contracts():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "python scripts/adapters.py validate" in commands
    assert "python scripts/adapters.py status" in commands
    assert "python scripts/adapters.py capabilities" in commands
    assert "python scripts/adapters.py companions" in commands
    assert "python scripts/adapters.py interop context7" in commands


def test_ci_compiles_scripts_and_tests():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "python -m compileall scripts tests" in commands


def test_ci_smokes_homebrew_and_shell_exports():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "dist/adapters/homebrew/Formula/get-things-done.rb" in commands
    assert "dist/adapters/shell/install.sh" in commands
    assert "ruby -c Formula/get-things-done.rb" in commands


def test_ci_smokes_checksum_generation_and_verification():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "python scripts/release_checksums.py ./dist/adapters --out ./dist/adapters/SHA256SUMS" in commands
    assert "python scripts/release_checksums.py ./dist/adapters --verify ./dist/adapters/SHA256SUMS" in commands


def test_release_validates_adapters_before_publishing():
    commands = step_run_commands(load_workflow("release.yml"), "release")
    assert "python scripts/adapters.py validate" in commands


def test_release_builds_multi_host_adapter_artifacts():
    commands = step_run_commands(load_workflow("release.yml"), "release")
    assert "python scripts/adapters.py export-all" in commands
    assert "--package" in commands
    assert "homebrew" in commands
    assert "shell" in commands


def test_release_generates_and_verifies_checksums():
    commands = step_run_commands(load_workflow("release.yml"), "release")
    assert "python scripts/release_checksums.py ./dist --out ./dist/SHA256SUMS" in commands
    assert "python scripts/release_checksums.py ./dist/adapters --out ./dist/adapters/SHA256SUMS" in commands
    assert "python scripts/release_checksums.py ./dist --verify ./dist/SHA256SUMS" in commands
    assert "python scripts/release_checksums.py ./dist/adapters --verify ./dist/adapters/SHA256SUMS" in commands

