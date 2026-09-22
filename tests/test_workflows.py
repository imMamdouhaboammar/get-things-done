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



def test_ci_matrix_matches_advertised_python_support():
    workflow = load_workflow("ci.yml")
    versions = workflow["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    assert versions == ["3.10", "3.11", "3.12", "3.13", "3.14"]


def test_ci_installs_package_and_smokes_installed_entrypoint():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert 'python -m pip install -e ".[dev]"' in commands
    assert "gtd --help" in commands


def test_ci_enforces_ruff_and_has_explicit_security_bounds():
    workflow = load_workflow("ci.yml")
    commands = step_run_commands(workflow, "test")
    assert "python -m ruff check scripts tests skills/get-things-done/scripts" in commands
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["test"]["timeout-minutes"] == 20


def test_ci_explicitly_smokes_antigravity_export():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "dist/adapters/antigravity/.gemini/config/skills/get-things-done/SKILL.md" in commands


def test_release_installs_the_declared_package_and_runs_static_gate():
    workflow = load_workflow("release.yml")
    commands = step_run_commands(workflow, "release")
    assert 'python -m pip install -e ".[dev]"' in commands
    assert "gtd --help" in commands
    assert "python -m ruff check scripts tests skills/get-things-done/scripts" in commands
    assert workflow["jobs"]["release"]["timeout-minutes"] == 30


def test_release_writes_provenance_before_publication():
    workflow = load_workflow("release.yml")
    commands = step_run_commands(workflow, "release")
    assert "python scripts/release_provenance.py" in commands
    assert '--source-sha "$GITHUB_SHA"' in commands
    assert '--ref "$GITHUB_REF"' in commands
    assert "--out ./dist/PROVENANCE.json" in commands

    release_step = next(
        step
        for step in workflow["jobs"]["release"]["steps"]
        if step.get("name") == "Create GitHub Release"
    )
    assert "dist/PROVENANCE.json" in release_step["with"]["files"]


def test_release_uses_explicit_write_permission_only_for_release_job():
    workflow = load_workflow("release.yml")
    assert workflow["jobs"]["release"]["permissions"] == {"contents": "write"}


def test_ci_validates_behavioral_eval_contracts_without_claiming_live_model_results():
    commands = step_run_commands(load_workflow("ci.yml"), "test")
    assert "python scripts/behavioral_evals.py validate-suite evals/cases.jsonl" in commands
    assert "python scripts/behavioral_evals.py validate-suite evals/domain-routing-cases.jsonl" in commands
