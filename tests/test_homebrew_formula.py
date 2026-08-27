from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMULA = (ROOT / "Formula" / "get-things-done.rb").read_text(encoding="utf-8")


def test_formula_is_head_only_until_versioned_release_exists():
    assert 'head "https://github.com/imMamdouhaboammar/get-things-done.git", branch: "main"' in FORMULA
    assert "sha256 " not in FORMULA


def test_formula_declares_python_runtime():
    assert 'depends_on "python@3.13"' in FORMULA


def test_formula_installs_canonical_skills_and_adapter_metadata():
    assert 'libexec.install "skills", "scripts", "adapters"' in FORMULA
    assert 'libexec.install ".claude-plugin", ".codex-plugin"' in FORMULA


def test_formula_exposes_gtd_cli_wrapper():
    assert 'bin.write_exec_script libexec/"scripts/gtd.py"' in FORMULA


def test_formula_has_runtime_doctor_test():
    assert 'system bin/"gtd", "doctor"' in FORMULA


def test_formula_caveat_explains_skill_location_and_head_status():
    assert "canonical Agent Skills" in FORMULA
    assert "HEAD-only" in FORMULA
