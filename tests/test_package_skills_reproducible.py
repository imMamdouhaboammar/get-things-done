import subprocess
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package_skills.py"


def test_package_skills_produces_deterministic_checksums(tmp_path):
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    
    r1 = subprocess.run([sys.executable, str(SCRIPT), "--root", str(ROOT), "--out", str(out1)], capture_output=True, text=True, check=False)
    assert r1.returncode == 0, r1.stderr
    
    r2 = subprocess.run([sys.executable, str(SCRIPT), "--root", str(ROOT), "--out", str(out2)], capture_output=True, text=True, check=False)
    assert r2.returncode == 0, r2.stderr
    
    for skill_name in ["get-things-done", "building-gtd-domain-packs"]:
        f1 = out1 / f"{skill_name}.zip"
        f2 = out2 / f"{skill_name}.zip"
        assert f1.is_file()
        assert f2.is_file()
        h1 = hashlib.sha256(f1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(f2.read_bytes()).hexdigest()
        assert h1 == h2, f"Checksum mismatch for {skill_name}: {h1} != {h2}"
