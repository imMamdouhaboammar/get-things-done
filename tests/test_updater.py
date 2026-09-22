import importlib.util
import io
import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "skills/get-things-done/scripts/updater.py"

spec = importlib.util.spec_from_file_location("gtd_updater", UPDATER_PATH)
updater = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = updater
assert spec.loader is not None
spec.loader.exec_module(updater)


def make_archive(core_text: str = "core-v1", marker: str = "new") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        prefix = "get-things-done-test/skills"
        files = {
            "get-things-done/SKILL.md": f"---\nname: get-things-done\n---\n{marker}\n",
            "get-things-done/references/core-contract.md": core_text,
            "get-things-done/domains/software.md": "canonical software",
            "building-gtd-domain-packs/SKILL.md": "---\nname: building-gtd-domain-packs\n---\n",
            "building-gtd-domain-packs/references/core-contract.md": core_text,
            "gtd-capability-router/SKILL.md": "---\nname: gtd-capability-router\n---\n",
            "gtd-capability-router/references/core-contract.md": core_text,
            "gtd-deliberation/SKILL.md": "---\nname: gtd-deliberation\n---\n",
        }
        for rel, content in files.items():
            zf.writestr(f"{prefix}/{rel}", content)
    return buf.getvalue()


def source(ref: str = "abc1234"):
    return updater.RemoteSource(
        channel="main",
        kind="main",
        ref=ref,
        archive_url=f"https://example.invalid/{ref}.zip",
    )


def test_update_installs_all_skills_and_writes_state(tmp_path):
    skills = tmp_path / "skills"
    result = updater.update_from_archive(make_archive(), skills, source())

    for name in updater.SKILL_NAMES:
        assert (skills / name / "SKILL.md").is_file()
    state = json.loads((skills / updater.STATE_FILE).read_text())
    assert state["source"]["ref"] == "abc1234"
    assert state["canonical_manifest"]
    assert result["canonical_files"] == len(state["canonical_manifest"])


def test_update_preserves_custom_domain_files(tmp_path):
    skills = tmp_path / "skills"
    old_domains = skills / "get-things-done/domains"
    old_domains.mkdir(parents=True)
    (skills / "get-things-done/SKILL.md").write_text("old")
    (old_domains / "my-finance.md").write_text("custom")

    result = updater.update_from_archive(make_archive(), skills, source())

    assert (skills / "get-things-done/domains/my-finance.md").read_text() == "custom"
    assert result["preserved_custom_domains"] == ["my-finance.md"]


def test_second_update_refuses_modified_canonical_file_without_force(tmp_path):
    skills = tmp_path / "skills"
    updater.update_from_archive(make_archive(marker="one"), skills, source("one"))
    canonical = skills / "get-things-done/SKILL.md"
    canonical.write_text("locally edited")

    with pytest.raises(updater.UpdateError, match="local canonical files changed"):
        updater.update_from_archive(make_archive(marker="two"), skills, source("two"))

    updater.update_from_archive(make_archive(marker="two"), skills, source("two"), force=True)
    assert "two" in canonical.read_text()


def test_validation_rejects_unsynchronized_core_contracts(tmp_path):
    skills = tmp_path / "skills"
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        p = "repo/skills"
        zf.writestr(f"{p}/get-things-done/SKILL.md", "x")
        zf.writestr(f"{p}/get-things-done/references/core-contract.md", "a")
        zf.writestr(f"{p}/building-gtd-domain-packs/SKILL.md", "x")
        zf.writestr(f"{p}/building-gtd-domain-packs/references/core-contract.md", "b")
        zf.writestr(f"{p}/gtd-capability-router/SKILL.md", "x")
        zf.writestr(f"{p}/gtd-capability-router/references/core-contract.md", "a")
        zf.writestr(f"{p}/gtd-deliberation/SKILL.md", "x")

    with pytest.raises(updater.UpdateError, match="not synchronized"):
        updater.update_from_archive(archive.getvalue(), skills, source())


def test_extractor_ignores_path_traversal_and_unrelated_files(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("repo/../../evil.txt", "bad")
        zf.writestr("repo/README.md", "unrelated")
        zf.writestr("repo/skills/get-things-done/SKILL.md", "ok")
    staged = tmp_path / "stage"
    staged.mkdir()
    updater.extract_skill_archive(buf.getvalue(), staged)
    assert (staged / "get-things-done/SKILL.md").is_file()
    assert not (tmp_path / "evil.txt").exists()


def test_check_does_not_download_archive(monkeypatch, tmp_path, capsys):
    skills = tmp_path / "skills"
    skills.mkdir()
    updater._write_state(skills, source("old"), {})

    monkeypatch.setattr(updater, "resolve_remote", lambda channel, timeout=15.0: source("new"))

    def forbidden(*args, **kwargs):
        raise AssertionError("archive download must not run during --check")

    monkeypatch.setattr(updater, "_request", forbidden)
    rc = updater.run_update(pack_root=tmp_path, target_path=str(skills), check=True)
    out = capsys.readouterr().out
    assert rc == 0
    assert "UPDATE AVAILABLE" in out


def test_repository_checkout_refuses_self_mutation_without_target(tmp_path, capsys):
    (tmp_path / ".git").mkdir()
    rc = updater.run_update(pack_root=tmp_path)
    assert rc == 2
    assert "repository checkout detected" in capsys.readouterr().out


def test_stable_channel_does_not_silently_fallback(monkeypatch):
    class NotFound(Exception):
        pass

    def fake_json(url, timeout):
        error = __import__("urllib.error", fromlist=["HTTPError"]).HTTPError(url, 404, "no release", {}, None)
        raise error

    monkeypatch.setattr(updater, "_json_request", fake_json)
    with pytest.raises(updater.UpdateError, match="latest release"):
        updater.resolve_remote("stable")


def test_latest_channel_falls_back_to_main_when_no_release(monkeypatch):
    def fake_json(url, timeout):
        if url.endswith("/releases/latest"):
            raise __import__("urllib.error", fromlist=["HTTPError"]).HTTPError(url, 404, "no release", {}, None)
        return {"commit": {"sha": "f" * 40}}

    monkeypatch.setattr(updater, "_json_request", fake_json)
    resolved = updater.resolve_remote("latest")
    assert resolved.kind == "main"
    assert resolved.ref == "f" * 40


def test_canonical_cli_registers_update_command():
    import subprocess

    result = subprocess.run(
        [sys.executable, str(ROOT / "skills/get-things-done/scripts/gtd.py"), "update", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--channel" in result.stdout
    assert "--check" in result.stdout
    assert "--target-path" in result.stdout
    assert "--force" in result.stdout
