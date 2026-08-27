import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_checksums.py"


def test_checksum_script_writes_sorted_sha256_manifest(tmp_path):
    (tmp_path / "b.zip").write_bytes(b"b")
    (tmp_path / "a.zip").write_bytes(b"a")
    output = tmp_path / "SHA256SUMS"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--out", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    lines = output.read_text().splitlines()
    assert lines == [
        f"{hashlib.sha256(b'a').hexdigest()}  a.zip",
        f"{hashlib.sha256(b'b').hexdigest()}  b.zip",
    ]


def test_checksum_script_ignores_non_zip_files(tmp_path):
    (tmp_path / "bundle.zip").write_bytes(b"bundle")
    (tmp_path / "notes.txt").write_text("ignore")
    output = tmp_path / "SHA256SUMS"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--out", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    text = output.read_text()
    assert "bundle.zip" in text
    assert "notes.txt" not in text


def test_checksum_script_fails_when_no_archives_exist(tmp_path):
    output = tmp_path / "SHA256SUMS"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--out", str(output)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "no .zip artifacts" in result.stderr
    assert not output.exists()


def test_checksum_script_verifies_valid_manifest(tmp_path):
    (tmp_path / "pkg1.zip").write_bytes(b"content1")
    (tmp_path / "pkg2.zip").write_bytes(b"content2")
    manifest = tmp_path / "SHA256SUMS"
    res1 = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--out", str(manifest)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert res1.returncode == 0
    res2 = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--verify", str(manifest)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert res2.returncode == 0, res2.stderr
    assert "OK" in res2.stdout


def test_checksum_script_fails_verification_on_corrupted_file(tmp_path):
    (tmp_path / "pkg.zip").write_bytes(b"original")
    manifest = tmp_path / "SHA256SUMS"
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), "--out", str(manifest)], check=True)
    # Corrupt the file
    (tmp_path / "pkg.zip").write_bytes(b"tampered")
    res = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--verify", str(manifest)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert res.returncode == 1
    assert "FAILED" in res.stderr or "mismatch" in res.stderr


def test_checksum_script_fails_verification_on_missing_file(tmp_path):
    (tmp_path / "pkg.zip").write_bytes(b"original")
    manifest = tmp_path / "SHA256SUMS"
    subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), "--out", str(manifest)], check=True)
    # Delete the file
    (tmp_path / "pkg.zip").unlink()
    res = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--verify", str(manifest)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert res.returncode == 1
    assert "missing" in res.stderr or "FAILED" in res.stderr

