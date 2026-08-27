import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gtd.py"


def test_doctor_passes_on_canonical_pack_with_adapters():
    result = subprocess.run(
        [sys.executable, str(CLI), "doctor", "--root", str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PASS: core files valid" in result.stdout
    assert "4 domain packs found" in result.stdout


def test_doctor_fails_if_required_file_missing(tmp_path):
    # Empty dir
    result = subprocess.run(
        [sys.executable, str(CLI), "doctor", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "FAIL" in result.stdout
