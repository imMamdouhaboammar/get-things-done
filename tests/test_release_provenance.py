import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/release_provenance.py"

spec = importlib.util.spec_from_file_location("gtd_release_provenance", SCRIPT)
provenance = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(provenance)


def make_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    (dist / "adapters").mkdir(parents=True)
    (dist / "get-things-done.zip").write_bytes(b"canonical")
    (dist / "adapters/codex.zip").write_bytes(b"adapter")
    (dist / "SHA256SUMS").write_text("test\n", encoding="utf-8")
    (dist / "adapters/SHA256SUMS").write_text("adapter-test\n", encoding="utf-8")
    return dist


def make_version_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in ["pyproject.toml", *provenance.VERSION_JSON_PATHS]:
        source = ROOT / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return root


def test_build_provenance_links_version_source_and_artifact_hashes(tmp_path):
    dist = make_dist(tmp_path)
    output = dist / "PROVENANCE.json"
    payload = provenance.build_provenance(
        ROOT,
        dist,
        "a" * 40,
        "refs/tags/v1.4.0",
        output,
    )

    assert payload["schema_version"] == 1
    assert payload["version"] == "1.4.0"
    assert payload["source"] == {"sha": "a" * 40, "ref": "refs/tags/v1.4.0"}
    assert set(payload["version_manifests"].values()) == {"1.4.0"}
    paths = [item["path"] for item in payload["artifacts"]]
    assert paths == sorted(paths)
    assert "get-things-done.zip" in paths
    assert "adapters/codex.zip" in paths
    assert all(len(item["sha256"]) == 64 for item in payload["artifacts"])


def test_provenance_is_deterministic_for_same_inputs(tmp_path):
    dist = make_dist(tmp_path)
    output = dist / "PROVENANCE.json"
    first = provenance.build_provenance(ROOT, dist, "b" * 40, "refs/heads/main", output)
    second = provenance.build_provenance(ROOT, dist, "b" * 40, "refs/heads/main", output)
    assert first == second


def test_release_tag_must_match_project_version(tmp_path):
    dist = make_dist(tmp_path)
    with pytest.raises(provenance.ProvenanceError, match="does not match project version"):
        provenance.build_provenance(
            ROOT,
            dist,
            "c" * 40,
            "refs/tags/v9.9.9",
            dist / "PROVENANCE.json",
        )


def test_manifest_version_drift_fails_closed(tmp_path):
    root = make_version_root(tmp_path)
    package_path = root / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["version"] = "9.9.9"
    package_path.write_text(json.dumps(package), encoding="utf-8")

    with pytest.raises(provenance.ProvenanceError, match="release version mismatch"):
        provenance.validate_release_identity(root, "refs/heads/main")


def test_full_commit_sha_is_required(tmp_path):
    dist = make_dist(tmp_path)
    with pytest.raises(provenance.ProvenanceError, match="40-character"):
        provenance.build_provenance(ROOT, dist, "abc123", "refs/heads/main", dist / "PROVENANCE.json")


def test_provenance_cli_writes_json(tmp_path):
    import subprocess
    import sys

    dist = make_dist(tmp_path)
    output = dist / "PROVENANCE.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ROOT),
            "--dist",
            str(dist),
            "--source-sha",
            "d" * 40,
            "--ref",
            "refs/tags/v1.4.0",
            "--out",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["source"]["sha"] == "d" * 40
