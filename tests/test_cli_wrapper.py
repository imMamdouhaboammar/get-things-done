import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "gtd.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("gtd_wrapper", WRAPPER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_wrapper_import_is_side_effect_free():
    module = load_wrapper()
    assert callable(module.main)


def test_wrapper_points_at_canonical_cli():
    module = load_wrapper()
    assert module.CANONICAL == ROOT / "skills" / "get-things-done" / "scripts" / "gtd.py"
    assert module.CANONICAL.is_file()


def test_wrapper_doctor_command_succeeds():
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "doctor"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS: core files valid" in result.stdout


def test_wrapper_list_domains_lists_all_domains():
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "list-domains"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "software" in result.stdout
    assert "marketing" in result.stdout
    assert "product" in result.stdout
    assert "research" in result.stdout


def test_wrapper_new_and_validate_brief_workflow(tmp_path):
    import subprocess
    import sys
    brief_file = tmp_path / "test_brief.json"
    r1 = subprocess.run(
        [sys.executable, str(WRAPPER), "new-brief", "--title", "Test Brief", "--domain", "software", "--out", str(brief_file)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert r1.returncode == 0, r1.stderr
    assert brief_file.is_file()

    r2 = subprocess.run(
        [sys.executable, str(WRAPPER), "validate-brief", str(brief_file), "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert r2.returncode == 0, r2.stderr
    assert "VALID" in r2.stdout

